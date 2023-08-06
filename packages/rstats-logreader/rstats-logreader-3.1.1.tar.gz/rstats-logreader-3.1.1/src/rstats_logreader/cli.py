################################################################################
#                               rstats-logreader                               #
#   Parse RStats logfiles, display bandwidth usage, convert to other formats   #
#                    (C) 2016, 2019-2020, 2022 Jeremy Brown                    #
#                Released under Prosperity Public License 3.0.0                #
################################################################################


from argparse import ArgumentParser, ArgumentTypeError, Namespace
from pathlib import Path

from rstats_logreader import __version__
from rstats_logreader.reader import RStatsParser


def parse_args(arg_list):
    """
    Read arguments from stdin while validating and performing any necessary conversions

    :returns: (Namespace) Tool arguments
    """
    args = None

    def norm_resolution(inp):
        resolutions = {"d": "daily", "w": "weekly", "m": "monthly"}

        if inp:
            if any(res not in resolutions for res in inp):
                raise ArgumentTypeError("Invalid resolution for logs")

            return Namespace(**{v: k in inp for (k, v) in resolutions.items()})

    def norm_day(day):
        days = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}

        if day:
            return days[day]

    main_parser = ArgumentParser(
        prog="rstats-reader",
        description="Displays statistics in RStats logfiles, with optional conversion",
        epilog="Released under Prosperity 3.0.0, (C) 2016, 2019-20, 2022 Jeremy Brown",
    )

    main_parser.add_argument(
        "path",
        type=Path,
        help="gzipped RStats logfile",
    )

    main_parser.add_argument(
        "--print",
        type=norm_resolution,
        dest="print_freq",
        metavar="{dwm}",
        help="Print daily, weekly or monthly statistics to the console",
    )

    main_parser.add_argument(
        "-w",
        "--week-start",
        type=norm_day,
        default="Mon",
        metavar="{Mon - Sun}",
        choices=range(7),
        help="Day of the week statistics should reset",
    )

    main_parser.add_argument(
        "-m",
        "--month-start",
        type=int,
        default=1,
        choices=range(1, 32),
        metavar="{1 - 31}",
        help="Day of the month statistics should reset",
    )

    main_parser.add_argument(
        "-u",
        "--units",
        default="MiB",
        metavar="{B - TiB}",
        choices=["B", "KiB", "MiB", "GiB", "TiB"],
        help="Units statistics will be displayed in",
    )

    main_parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    write_group = main_parser.add_argument_group("write")

    write_group.add_argument(
        "--write",
        type=norm_resolution,
        dest="write_freq",
        metavar="{dwm}",
        help="Write daily, weekly or monthly statistics to a file",
    )

    write_group.add_argument(
        "-o",
        "--outfile",
        type=Path,
        metavar="outfile.dat",
        help="File to write statistics to",
    )

    write_group.add_argument(
        "-f",
        "--format",
        default="csv",
        choices=["csv", "json"],
        help="Format to write statistics in",
    )

    args = main_parser.parse_args(arg_list)

    if getattr(args, "write_freq", False) and args.outfile is None:
        raise ArgumentTypeError("Missing output filename")

    return args


def main(args=None):
    """
    Tool entry point
    """
    args = parse_args(args)
    parser = RStatsParser(args.week_start, args.month_start, args.units, args.path)

    if args.print_freq is not None:
        for line in parser.get_console_stats(**vars(args.print_freq)):
            print(line)

    if args.write_freq is not None:
        parser.write_stats(args.outfile, args.format, **vars(args.write_freq))
