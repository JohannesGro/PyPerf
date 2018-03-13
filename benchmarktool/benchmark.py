#!/usr/bin/env python
# -*- python -*- coding: iso-8859-1 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# http://www.contact.de/
#

import argparse
import time

SUITEFILE_DEFAULT = "benchsuite.json"
REPORTFILE_DEFAULT = 'benchmarkResults_{}.json'.format(time.strftime("%Y-%m-%d_%H-%M-%S"))
RENDERFILE_DEFAULT = 'benchmarkResults_{}.html'.format(time.strftime("%Y-%m-%d_%H-%M-%S"))


def main():
    help_txt = ("Help")
    parser = argparse.ArgumentParser(description=help_txt)
    subparsers = parser.add_subparsers(dest='subcommand')

    runner = subparsers.add_parser("runner")
    helpstr = "A JSON file which contains the benches (default: %s)." % SUITEFILE_DEFAULT
    runner.add_argument("--suite", "-s", nargs='?', default=SUITEFILE_DEFAULT, help=helpstr)
    helpstr = "The results will be stored in this file (default: %s)." % REPORTFILE_DEFAULT
    runner.add_argument("--outfile", "-o", nargs='?', default=REPORTFILE_DEFAULT, help=helpstr)
    runner.add_argument("--logconfig", "-l", nargs='?', default="",
                        help="Configuration file for the logger.")

    render = subparsers.add_parser("render")
    render.add_argument("benchmarks", nargs='+',
                        help="One or more json files which contain the benchmarks."
                        "It is also possible to use folders. "
                        "All JSON files from a folder will be loaded.")
    render.add_argument("--outfile", "-o", nargs='?', default=RENDERFILE_DEFAULT,
                        help="The results will be stored in this file (HTML).")
    render.add_argument("--reference", "-r", nargs='?',
                        help="A referenced benchmark for the comparision."
                        "Uses the reference to mark some benchmarks result"
                        "as positiv or negativ. This option will be ignored"
                        "if the -trend option is active.")
    render.add_argument("--logconfig", "-l", nargs='?', default="",
                        help="Configuration file for the logger.")
    render.add_argument("--trend", "-t", default=False, action="store_true",
                        help="Using the benchmarks to show a trend of a system.")

    upload_parser = subparsers.add_parser("upload")
    upload_parser.add_argument("--influxdburl", "-u",
                               help="The URL to the Influx DBMS to upload the results onto.")
    upload_parser.add_argument("--database", "-d",
                               help="The database to upload the results into.")
    upload_parser.add_argument("--filename", "-f",
                               help="JSON report to upload.")
    upload_parser.add_argument("--precision", "-p",
                               help="The precision of the timestamp.")
    upload_parser.add_argument("--timestamp", "-t",
                               help="If given, overrides the timestamp given in the report.")
    upload_parser.add_argument("--values", "-v",
                               help="Additional values to upload.")

    args = parser.parse_args()
    subcommand = args.subcommand
    if subcommand == "runner":
        from benchrunner import Benchrunner
        Benchrunner().main(args.suite, args.outfile, args.logconfig)
    elif subcommand == "render":
        from renderer import Renderer
        rend = Renderer(args.benchmarks, args.outfile, args.reference,
                        args.logconfig, args.trend)
        rend.main()
    elif subcommand == "upload":
        from influxuploader import upload
        upload(args.filename, args.influxdburl, args.database,
               args.timestamp, args.precision, args.values)

if __name__ == "__main__":
    main()
