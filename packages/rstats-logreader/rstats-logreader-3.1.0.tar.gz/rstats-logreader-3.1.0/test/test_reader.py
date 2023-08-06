################################################################################
#                               rstats-logreader                               #
#   Parse RStats logfiles, display bandwidth usage, convert to other formats   #
#                    (C) 2016, 2019-2020, 2022 Jeremy Brown                    #
#                Released under Prosperity Public License 3.0.0                #
################################################################################


import gzip

from csv import DictReader
from datetime import date, timedelta
from json import load
from struct import error, pack
from unittest.mock import patch

import pytest

from hypothesis import HealthCheck, assume, example, given, settings
from hypothesis.strategies import (
    booleans,
    composite,
    data,
    dates,
    integers,
    just,
    lists,
    none,
    one_of,
)

from rstats_logreader.reader import RStatsParser as parser


def packed_date(date_to_pack):
    raw_year = date_to_pack.year % 1900
    raw_month = date_to_pack.month - 1
    raw_day = 0 if date_to_pack.day == 1 else date_to_pack.day

    return raw_year << 16 | raw_month << 8 | raw_day


def packed_raw_entry(date, download, upload):
    return pack("<3Q", packed_date(date), download, upload)


@composite
def log_date(draw):
    return draw(dates(min_value=date(1900, 1, 2), max_value=date(2155, 12, 31)))


@composite
def raw_entry_list(draw):
    result = []

    max_entries = draw(integers(min_value=1, max_value=62))
    start_date = draw(log_date())
    assume(start_date + timedelta(days=max_entries) <= date(2156, 1, 1))

    for d in range(max_entries):
        dl, ul = draw(
            lists(integers(min_value=0, max_value=2**64 - 1), min_size=2, max_size=2)
        )
        result.append(parser.RawEntry(start_date + timedelta(days=d), dl, ul))

    return result


@pytest.mark.parametrize(
    "factor, result",
    [
        ("B", 2**0),
        ("KiB", 2**10),
        ("MiB", 2**20),
        ("GiB", 2**30),
        ("TiB", 2**40),
        ("PiB", ValueError),
    ],
    ids=["B", "KiB", "MiB", "GiB", "TiB", "invalid"],
)
def test_get_factor(factor, result):
    if isinstance(result, int):
        assert parser._get_factor(factor) == result
    else:
        with pytest.raises(result):
            parser._get_factor(factor)


@given(log_date())
def test_to_date(test_date):
    assert parser._to_date(packed_date(test_date)) == test_date


@given(
    one_of(none(), log_date()),
    lists(integers(min_value=0, max_value=2**64 - 1), min_size=2, max_size=2),
)
def test_build_stat_entry(test_date, test_bw_values):
    dl, ul = test_bw_values

    if test_date is None:
        assert (
            parser._build_stat_entry(packed_raw_entry(date(1900, 1, 1), dl, ul)) is None
        )

    else:
        res = parser._build_stat_entry(packed_raw_entry(test_date, dl, ul))
        assert res.date == test_date
        assert res.download == dl
        assert res.upload == ul


@pytest.mark.parametrize(
    "resolution", ["weekly", "monthly"], ids=["weekly-partition", "monthly-partition"]
)
@given(
    one_of(none(), log_date()),
    integers(min_value=0, max_value=60),
    integers(min_value=1, max_value=31),
    data(),
)
def test_partition(resolution, start_date, entry_count, partition_start, data):
    log_entries = []

    if resolution == "weekly":
        partition_start %= 7

    if start_date is not None:
        for d in range(entry_count):
            dl, ul = data.draw(
                lists(
                    integers(min_value=0, max_value=2**64 - 1), min_size=2, max_size=2
                )
            )
            log_entries.append(parser.RawEntry(start_date + timedelta(days=d), dl, ul))

    if start_date is None:
        with pytest.raises(TypeError):
            parser._partition(log_entries, resolution)
    else:
        if resolution == "weekly":
            res = parser._partition(log_entries, resolution, week_start=partition_start)
            assert sum(len(part) for part in res) == entry_count
            assert all([len(part) <= 7 for part in res])
            for part in res:
                if any([entry.date.weekday() == partition_start for entry in part]):
                    assert (
                        sorted(part, key=lambda e: e.date)[0].date.weekday()
                        == partition_start
                    )
        else:
            res = parser._partition(
                log_entries, resolution, month_start=partition_start
            )
            assert sum(len(part) for part in res) == entry_count
            for part in res:
                if any([entry.date.day == partition_start for entry in part]):
                    assert (
                        sorted(part, key=lambda e: e.date)[0].date.day
                        == partition_start
                    )


@given(
    raw_entry_list(),
    one_of(just(1), just(2**10), just(2**20)),
)
def test_aggregate_stats(raw_entries, factor):
    # start week on monday, month on the 1st
    weekly_partitions = parser._partition(raw_entries, "weekly", week_start=0)
    monthly_partitions = parser._partition(raw_entries, "monthly", month_start=1)
    res = parser._aggregate_stats(raw_entries, factor, 0, 1)

    assert len(res["daily"]) == len(raw_entries)
    assert len(res["weekly"]) == len(weekly_partitions)
    assert len(res["monthly"]) == len(monthly_partitions)

    for entry, stat in zip(raw_entries, res["daily"]):
        assert stat.start == entry.date
        assert stat.end == entry.date

        if factor == 1:
            assert stat.download == entry.download
            assert stat.upload == entry.upload
        else:
            assert stat.download == entry.download / factor
            assert stat.upload == entry.upload / factor

    for partition, stat in zip(weekly_partitions, res["weekly"]):
        assert stat.start == min(entry.date for entry in partition)
        assert stat.end == max(entry.date for entry in partition)

        if factor == 1:
            assert stat.download == sum(entry.download for entry in partition)
            assert stat.upload == sum(entry.upload for entry in partition)
        else:
            assert stat.download == sum(entry.download for entry in partition) / factor
            assert stat.upload == sum(entry.upload for entry in partition) / factor

    for partition, stat in zip(monthly_partitions, res["monthly"]):
        assert stat.start == min(entry.date for entry in partition)
        assert stat.end == max(entry.date for entry in partition)

        if factor == 1:
            assert stat.download == sum(entry.download for entry in partition)
            assert stat.upload == sum(entry.upload for entry in partition)
        else:
            assert stat.download == sum(entry.download for entry in partition) / factor
            assert stat.upload == sum(entry.upload for entry in partition) / factor


@pytest.mark.parametrize(
    "version, months",
    [["RS00", 12], ["RS01", 25], ["RS02", 42]],
    ids=["version-1", "version-2", "invalid-version"],
)
def test_get_logfile_version(version, months):
    data = pack("<4s", version.encode("utf-8"))

    if version != "RS02":
        assert parser._get_logfile_version(data) == (version, months)
    else:
        with pytest.raises(TypeError):
            parser._get_logfile_version(data)


@given(raw_entry_list())
@example(raw_entries=[])
def test_get_day_data(raw_entries):
    data = bytearray(b"RS01\x00\x00\x00\x00")
    entry_count = len(raw_entries)

    for entry in raw_entries:
        data.extend(packed_raw_entry(entry.date, entry.download, entry.upload))

    if len(raw_entries) < 61:
        data.extend(packed_raw_entry(date(1900, 1, 1), 0, 0))
        entry_count += 1

    data.append(entry_count)

    if len(raw_entries) < 62:
        with pytest.raises(error):
            parser._get_day_data(data)
    else:
        res = parser._get_day_data(data)
        assert sorted(raw_entries, key=lambda e: e.date) == sorted(
            res, key=lambda e: e.date
        )


@pytest.mark.parametrize("error", [None, "check"], ids=["no-error", "bad-check"])
@pytest.mark.parametrize("months", [12, 25], ids=["version-0", "version-1"])
@given(raw_entry_list())
@example(raw_entries=[])
def test_get_month_data(months, error, raw_entries):
    raw_entries = raw_entries[:months]
    data = bytearray(b"RS00" if months == 12 else b"RS01")
    data.extend(b"\x00" * 1500)

    for entry in raw_entries:
        data.extend(packed_raw_entry(entry.date, entry.download, entry.upload))

    for _ in range(months - len(raw_entries)):
        data.extend(packed_raw_entry(date(1900, 1, 1), 0, 0))

    if error == "check":
        data.append((len(raw_entries) - 1) % 256)
    else:
        data.append(len(raw_entries))

    if error == "check":
        with pytest.raises(RuntimeError):
            parser._get_month_data(data, months)
    else:
        res = parser._get_month_data(data, months)
        assert sorted(raw_entries, key=lambda e: e.date) == sorted(
            res, key=lambda e: e.date
        )


@patch.object(parser, "parse_file")
@given(
    integers(min_value=0, max_value=6),
    integers(min_value=1, max_value=31),
    one_of(just("B"), just("KiB"), just("MiB"), just("GiB"), just("TiB")),
    one_of(none(), just("/tmp/logfile.gz")),
)
def test_init(mock_parse, week_start, month_start, units, logfile):
    factors = {
        "B": 2**0,
        "KiB": 2**10,
        "MiB": 2**20,
        "GiB": 2**30,
        "TiB": 2**40,
    }

    p = parser(week_start, month_start, units, logfile)
    assert p.week_start == week_start
    assert p.month_start == month_start
    assert p.units == units
    assert p.factor == factors[units]

    if logfile is None:
        mock_parse.assert_not_called()
    else:
        mock_parse.assert_called_once_with(logfile)

    mock_parse.reset_mock()


@pytest.mark.parametrize("error", [True, False], ids=["open-error", "no-error"])
@patch.object(parser, "_aggregate_stats", return_value={"daily": {}})
@patch.object(parser, "_get_month_data", return_value=["month_data"])
@patch.object(parser, "_get_day_data", return_value=["day_data"])
@patch.object(parser, "_get_logfile_version", return_value=(0, 12))
def test_parse_file(
    mock_logfile_version,
    mock_day_data,
    mock_month_data,
    mock_aggregate,
    error,
    tmp_path,
):
    if error:
        path = tmp_path.joinpath("nofile.gz")
    else:
        path = tmp_path.joinpath("logfile.gz")

        with gzip.open(path, "wb") as f:
            f.write(b"RS01")

    p = parser(0, 1, "B")

    if error:
        with pytest.raises(IOError):
            p.parse_file(path)
    else:
        p.parse_file(path)
        assert p.aggregates == {"daily": {}}


@given(
    one_of(just("B"), just("KiB")), booleans(), booleans(), booleans(), raw_entry_list()
)
def test_get_console_stats(
    units, write_daily, write_weekly, write_monthly, raw_entries
):
    p = parser(0, 1, units)
    p.aggregates = p._aggregate_stats(raw_entries, p.factor, 0, 1)

    res = p.get_console_stats(write_daily, write_weekly, write_monthly)
    hdr = "{0} {1:12.0f} {3} down\t{2:12.0f} {3} up"

    if write_daily:
        for stat in p.aggregates["daily"]:
            dateline = f"{stat.start}:\t\t\t"
            assert hdr.format(dateline, stat.download, stat.upload, units) in res

    if write_weekly:
        for stat in p.aggregates["weekly"]:
            dateline = f"{stat.start} - {stat.end}:\t"
            assert hdr.format(dateline, stat.download, stat.upload, units) in res

    if write_monthly:
        for stat in p.aggregates["monthly"]:
            dateline = f"{stat.start} - {stat.end}:\t"
            assert hdr.format(dateline, stat.download, stat.upload, units) in res


@settings(suppress_health_check=(HealthCheck.function_scoped_fixture,))
@pytest.mark.parametrize("out_format", ["csv", "json"])
@given(booleans(), booleans(), booleans(), raw_entry_list())
def test_write_stats(
    tmp_path, out_format, write_daily, write_weekly, write_monthly, raw_entries
):
    outpath = tmp_path.joinpath(f"out.{out_format}")
    p = parser(0, 1, "KiB")
    p.aggregates = p._aggregate_stats(raw_entries, p.factor, 0, 1)
    p.write_stats(outpath, out_format, write_daily, write_weekly, write_monthly)

    if out_format == "json":
        with open(outpath) as f:
            dumped_stats = load(f)

        if write_daily:
            for stat in p.aggregates["daily"]:
                assert {
                    "date_start": str(stat.start),
                    "date_end": str(stat.start),
                    "downloaded": round(stat.download, 3),
                    "uploaded": round(stat.upload, 3),
                    "units": p.units,
                } in dumped_stats["daily"]

        if write_weekly:
            for stat in p.aggregates["weekly"]:
                assert {
                    "date_start": str(stat.start),
                    "date_end": str(stat.end),
                    "downloaded": round(stat.download, 3),
                    "uploaded": round(stat.upload, 3),
                    "units": p.units,
                } in dumped_stats["weekly"]

        if write_monthly:
            for stat in p.aggregates["monthly"]:
                assert {
                    "date_start": str(stat.start),
                    "date_end": str(stat.end),
                    "downloaded": round(stat.download, 3),
                    "uploaded": round(stat.upload, 3),
                    "units": p.units,
                } in dumped_stats["monthly"]

    elif out_format == "csv":
        with open(outpath) as f:
            dumped_stats = list(DictReader(f))

        if write_daily:
            for stat in p.aggregates["daily"]:
                assert {
                    "date_start": str(stat.start),
                    "date_end": str(stat.start),
                    f"downloaded ({p.units})": str(round(stat.download, 3)),
                    f"uploaded ({p.units})": str(round(stat.upload, 3)),
                } in dumped_stats

        if write_weekly:
            for stat in p.aggregates["weekly"]:
                assert {
                    "date_start": str(stat.start),
                    "date_end": str(stat.end),
                    f"downloaded ({p.units})": str(round(stat.download, 3)),
                    f"uploaded ({p.units})": str(round(stat.upload, 3)),
                } in dumped_stats

        if write_monthly:
            for stat in p.aggregates["monthly"]:
                assert {
                    "date_start": str(stat.start),
                    "date_end": str(stat.end),
                    f"downloaded ({p.units})": str(round(stat.download, 3)),
                    f"uploaded ({p.units})": str(round(stat.upload, 3)),
                } in dumped_stats
