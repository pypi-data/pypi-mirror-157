################################################################################
#                               rstats-logreader                               #
#   Parse RStats logfiles, display bandwidth usage, convert to other formats   #
#                    (C) 2016, 2019-2020, 2022 Jeremy Brown                    #
#                Released under Prosperity Public License 3.0.0                #
################################################################################


import gzip

from collections import namedtuple
from csv import DictWriter
from datetime import date
from json import dumps
from struct import unpack


class RStatsParser:
    RawEntry = namedtuple("_raw_entry", ["date", "download", "upload"])
    AggregateStat = namedtuple(
        "_aggregate_stat", ["start", "end", "download", "upload"]
    )

    @staticmethod
    def _get_factor(unit):
        """
        Determine how much to divide the raw values from the logfile
        by

        :param unit: (str) Unit abbreviation of desired factor

        :returns: (int) numerical factor of unit
        """
        factors = {
            "B": 2**0,
            "KiB": 2**10,
            "MiB": 2**20,
            "GiB": 2**30,
            "TiB": 2**40,
        }

        try:
            return factors[unit]
        except KeyError:
            raise ValueError("Invalid Factor")

    @staticmethod
    def _to_date(num):
        """
        Convert a packed date value from the logfile into a Date object

        :param num: (int) Packed date value

        :returns: (Date) Date from logfile
        """
        year = ((num >> 16) & 0xFF) + 1900
        month = ((num >> 8) & 0xFF) + 1
        day = (num & 0xFF) or 1
        return date(year, month, day)

    @staticmethod
    def _build_stat_entry(data):
        """
        Convert a raw logfile entry into a helper object more suitable
        for later manipulation

        :param data: (bytes) Packed tuple containing upload/download
                             values on date

        :returns: (RawEntry) Helper object containing upload/download
                             values on date
        """
        result = None

        date, dl, ul = unpack("<3Q", data)

        if date:
            date = RStatsParser._to_date(date)
            result = RStatsParser.RawEntry(date, dl, ul)

        return result

    @staticmethod
    def _get_logfile_version(data):
        """
        Retrieve the version of the logfile being parsed for later use

        :param data: (bytes) Log file data

        :returns: (str, int) Version of logfile
                             and number of data-months
        """
        version = None
        data_months = 12

        try:
            version = unpack("<4s", data[:4])[0].decode("utf-8")
            if version not in ("RS00", "RS01"):
                raise TypeError("File is not valid rstats logfile")

            elif version == "RS01":
                data_months = 25
        except Exception:
            raise
        else:
            return version, data_months

    @staticmethod
    def _get_day_data(data):
        """
        Retrieve bandwidth data for individual days from the given
        logfile

        :param data: (bytes) Log file data

        :returns: (list) RawEntry objects containing bandwidth data for
                         their associated days
        """
        stats = []
        start = 8

        try:
            # Logs hold 62 data-days
            for _ in range(62):
                entry = RStatsParser._build_stat_entry(data[start : start + 24])
                start += 24

                if entry is None:
                    continue

                stats.append(entry)

            data_entries = data[start]
            if len(stats) != data_entries:
                pass
                # raise RuntimeError("Log month data is corrupted")
        except Exception:
            raise
        else:
            return list(sorted(stats))

    @staticmethod
    def _get_month_data(data, data_months):
        """
        Retrieve bandwidth data for individual months from the given
        logfile

        :param data: (bytes) Log file data
        :param data_months: (int) Number of months of month-level data
                                  in the logfile

        :returns: (list) RawEntry objects containing bandwidth data for
                         their associated months
        """
        # RS00 logs hold 12 data-months, RS01 logs hold 25 data-months
        stats = []
        start = 1504

        try:
            for _ in range(data_months):
                entry = RStatsParser._build_stat_entry(data[start : start + 24])
                start += 24

                if entry is None:
                    continue

                stats.append(entry)

            data_entries = data[start]
            if len(stats) != data_entries:
                raise RuntimeError("Log month data is corrupted")
        except Exception:
            raise
        else:
            return list(sorted(stats))

    @staticmethod
    def _partition(entries, resolution, week_start=None, month_start=None):
        """
        Group bandwidth data by the given resolution according to the
        specified group boundary

        :param entries: (list) Individual bandwith entries
        :param resolution: (str) Switch for splitting by week/month
        :param week_start: (int) If using weekly resolution,
                                 the day of the week where groups begin
        :param month_start: (int) If using monthly resolution,
                                  the day of the month where groups
                                  begin
        """
        result = []
        current = []

        if resolution == "weekly":
            if week_start is None:
                raise TypeError("Missing week_start")

            for entry in entries:
                stat_date = entry.date

                if stat_date.weekday() == week_start:
                    result.append(current)
                    current = []

                current.append(entry)

        elif resolution == "monthly":
            if month_start is None:
                raise TypeError("Missing month_start")

            for entry in entries:
                stat_date = entry.date

                if stat_date.day == month_start:
                    result.append(current)
                    current = []

                current.append(entry)

        if len(current):
            result.append(current)

        return [group for group in result if len(group)]

    @staticmethod
    def _aggregate_stats(raw_data, factor, week_start, month_start):
        """
        Combine all raw bandwidth entries in each group into an aggregate

        :param raw_data: (list) RawEntry objects containing daily
                                statistics
        :param factor: (int) Factor to divide raw numbers by to get
                             results in desired units
        :param week_start: (int) The day of the week where groups begin
        :param month_start: (int) The day of the month where groups
                                  begin

        :returns: (dict) Lists of AggregateStat objects containing
                         aggregated values grouped daily, weekly and
                         monthly
        """
        result = {"daily": [], "weekly": [], "monthly": []}

        for stat_range in result:
            if stat_range == "daily":
                data = raw_data
            elif stat_range == "weekly":
                data = RStatsParser._partition(
                    raw_data, "weekly", week_start=week_start
                )
            elif stat_range == "monthly":
                data = RStatsParser._partition(
                    raw_data, "monthly", month_start=month_start
                )

            for segment in data:
                if isinstance(segment, list):
                    start = min(entry.date for entry in segment)
                    end = max(entry.date for entry in segment)
                    download = sum(entry.download for entry in segment)
                    upload = sum(entry.upload for entry in segment)
                else:
                    start = end = segment.date
                    download = segment.download
                    upload = segment.upload

                if factor != 1:
                    download /= factor
                    upload /= factor

                result[stat_range].append(
                    RStatsParser.AggregateStat(start, end, download, upload)
                )

        return result

    def __init__(self, week_start, month_start, units, path=None):
        self.week_start = week_start
        self.month_start = month_start
        self.units = units
        self.factor = self._get_factor(units)
        self.aggregates = {}

        if path is not None:
            self.parse_file(path)

    def parse_file(self, logpath):
        """
        Parse the given logfile and store its values in the object

        :param logpath: (Path) The path to the logfile
        """
        # RStats log format:
        # First four bytes are magic string that indicate version
        # Next four bytes are empty, presumably for QWORD alignment
        # Next are 62 3-tuples for day-level stats,
        # contains date, download and upload totals (8 byte/value)
        # Next is one-byte counter that should match actual number of previous 3-tuples
        # Next seven bytes are empty, presumably for QWORD alignment
        # Next are 12 3-tuples for month-level stats,
        # contains date, download and upload totals (8 byte/value)
        # Version 1 logfiles hold another 13 month-level stat entries
        # Last is one-byte counter that should match actual number of previous 3-tuples
        try:
            with gzip.open(logpath, "rb") as f:
                log_data = bytes(f.read())
        except Exception:
            raise

        logfile_version, data_months = self._get_logfile_version(log_data)
        day_data = self._get_day_data(log_data)
        month_data = self._get_month_data(log_data, data_months)  # noqa
        self.aggregates = self._aggregate_stats(
            day_data, self.factor, self.week_start, self.month_start
        )

    def get_console_stats(self, daily, weekly, monthly):
        """
        Generate the desired statistics from the logfile,
        formatted as desired, to be later printed to the console.

        :param daily: (bool) Print daily stats to the console
        :param weekly: (bool) Print weekly stats to the console
        :param monthly: (bool) Print monthly stats to the console

        :returns: (list) Statistics to be printed to the console
        """
        hdr = "{0} {1:12.0f} {3} down\t{2:12.0f} {3} up"
        output = (
            (monthly, "monthly", self.aggregates["monthly"]),
            (weekly, "weekly", self.aggregates["weekly"]),
            (daily, "daily", self.aggregates["daily"]),
        )

        stat_lines = ["{:-^80}".format("Bandwidth Usage"), ""]
        for _, stat_range, stats in filter(lambda t: t[0], output):
            for stat in stats:
                if stat_range == "daily":
                    date_str = f"{stat.start}:\t\t\t"
                else:
                    date_str = f"{stat.start} - {stat.end}:\t"
                stat_lines.append(
                    hdr.format(date_str, stat.download, stat.upload, self.units)
                )
            stat_lines.append("")

        return stat_lines

    def write_stats(self, out_path, out_format, daily, weekly, monthly):
        """
        Write the desired converted stats for the logfile to a file

        :param out_path: (str) Path to write the converted stats to
        :param out_format: (str) Format to write the converted stats in
        :param daily: (bool) Write daily stats to a file
        :param weekly: (bool) Write weekly stats to a file
        :param monthly: (bool) Write monthly stats to a file
        """
        output = (
            (monthly, "monthly", self.aggregates["monthly"]),
            (weekly, "weekly", self.aggregates["weekly"]),
            (daily, "daily", self.aggregates["daily"]),
        )

        if out_format == "csv":
            fields = [
                "date_start",
                "date_end",
                f"downloaded ({self.units})",
                f"uploaded ({self.units})",
            ]

            with open(out_path, "w") as outfile:
                writer = DictWriter(outfile, fields)
                writer.writeheader()

                for _, _, stats in filter(lambda t: t[0], output):
                    writer.writerows(
                        {
                            "date_start": stat.start,
                            "date_end": stat.end,
                            f"downloaded ({self.units})": round(stat.download, 3),
                            f"uploaded ({self.units})": round(stat.upload, 3),
                        }
                        for stat in stats
                    )

        elif out_format == "json":
            out_stats = {}
            for _, stat_range, stats in filter(lambda t: t[0], output):
                out_stats[stat_range] = [
                    {
                        "date_start": str(stat.start),
                        "date_end": str(stat.end),
                        "downloaded": round(stat.download, 3),
                        "uploaded": round(stat.upload, 3),
                        "units": self.units,
                    }
                    for stat in stats
                ]

            with open(out_path, "w") as outfile:
                outfile.write(dumps(out_stats))
