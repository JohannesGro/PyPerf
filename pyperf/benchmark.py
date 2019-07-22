#!/usr/bin/env python
# -*- python -*- coding: iso-8859-1 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# http://www.contact.de/
#

import argparse
import time
import sys
import re

SUITEFILE_DEFAULT = "benchsuite.json"
REPORTFILE_DEFAULT = 'benchmarkResults_{}.json'.format(time.strftime("%Y-%m-%d_%H-%M-%S"))
UPLOADTARGET_DEFAULT = "influx"
INFLUXURL_DEFAULT = "http://localhost:8086"
INFLUXDB_DEFAULT = "perf"

UNKNOWN_SUBCOMMAND = 1
UPLOAD_TARGET_NOT_SUPPORTED = 21
UPLOAD_BAD_TIMESTAMP = 22


class BadTimestampError(Exception):
    pass


def parse_timestamp_param(timestamp):
    TS_RE = r"^([\d]{1,16})([a-z]{1,4})$"
    match = re.match(TS_RE, timestamp)
    if match and len(match.groups()) == 2:
        ts, unit = match.groups()
        if unit in ["s", "ms"]:
            return ts, unit
        else:
            raise BadTimestampError("Invalid unit: '%s'" % unit)
    else:
        raise BadTimestampError("Invalid time stamp: '%s'" % timestamp)


def main():
    help_txt = ("Help")
    parser = argparse.ArgumentParser(description=help_txt)
    subparsers = parser.add_subparsers(dest='subcommand')

    runner = subparsers.add_parser("run")
    helpstr = "A JSON file which contains the benches (default: %s)." % SUITEFILE_DEFAULT
    runner.add_argument("--suite", "-s", nargs='?', default=SUITEFILE_DEFAULT, help=helpstr)
    helpstr = "The results will be stored in this file (default: %s)." % REPORTFILE_DEFAULT
    runner.add_argument("--outfile", "-o", nargs='?', default=REPORTFILE_DEFAULT, help=helpstr)
    runner.add_argument("--logconfig", "-l", nargs='?', default="",
                        help="Configuration file for the logger.")
    runner.add_argument("--debug", "-d", default=False,
                        action='store_true', help="Get some more logging.")
    runner.add_argument("--verbose", "-v", default=False,
                        action='store_true', help="Get more detailled system infos.")

    upload_parser = subparsers.add_parser("upload")
    upload_parser.add_argument("filename", help="JSON report to upload.")
    upload_parser.add_argument(
        "--target", "-t",
        default=UPLOADTARGET_DEFAULT,
        help="The target storage to upload to (default: %s)." % UPLOADTARGET_DEFAULT
    )
    upload_parser.add_argument(
        "--url",
        default=INFLUXURL_DEFAULT,
        help="The URL of the Influx DBMS to upload onto (default: %s)." % INFLUXURL_DEFAULT
    )
    upload_parser.add_argument(
        "--db",
        default=INFLUXDB_DEFAULT,
        help="The database to upload the results into (default: %s)." % INFLUXDB_DEFAULT
    )
    upload_parser.add_argument(
        "--ts",
        metavar="<timestamp><unit>",
        help="If given, overrides the timestamp given in the report. Valid units are 's' and 'us'."
    )
    upload_parser.add_argument("--values", help="Additional values to upload.")
    upload_parser.add_argument("--tags", help="Additional tags to upload.")
    upload_parser.add_argument("--logconfig", "-l", nargs='?', default="",
                               help="Configuration file for the logger.")
    upload_parser.add_argument("--debug", "-d", default=False,
                               action='store_true', help="Get some more logging.")

    args = parser.parse_args()
    subcommand = args.subcommand
    rc = 0
    if subcommand == "run":
        from .benchrunner import Benchrunner
        return Benchrunner().main(args.suite, args.outfile, args.logconfig, args.verbose, args.debug)
    elif subcommand == "upload":
        if args.target == "influx":
            try:
                ts, unit = parse_timestamp_param(args.ts) if args.ts else (None, None)
                from .uploader import upload_2_influx
                return upload_2_influx(args.filename, args.url, args.db, ts, unit,
                                       args.values, args.tags, args.logconfig, args.debug)
            except BadTimestampError as tse:
                sys.stderr.write("%s %s: %s\n" %
                                 (parser.prog, args.subcommand, str(tse)))
                rc = UPLOAD_BAD_TIMESTAMP
        else:
            sys.stderr.write("%s %s: Target '%s' is not supported\n" %
                             (parser.prog, args.subcommand, args.target))
            rc = UPLOAD_TARGET_NOT_SUPPORTED
    else:
        # defensive programming, should never happen...
        sys.stderr.write("%s: Unknown subcommand '%s'" % (parser.prog, args.subcommand))
        rc = UNKNOWN_SUBCOMMAND

    return rc


if __name__ == "__main__":
    sys.exit(main())
