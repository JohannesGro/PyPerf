# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""
Command line interface for benchmarktool
"""

import click

from .influxuploader import InfluxUploader
from .benchrunner import Benchrunner

DEFAULT_SUITEFILE = "benchsuite.json"
DEFAULT_INFLUXURL = "http://localhost:8086"
DEFAULT_INFLUXDB = "metrics"


@click.group()
def main():
    pass


@click.command()
@click.option("--suite", "-s", default=DEFAULT_SUITEFILE,
              help="A JSON file which contains the benches (default: %s)." % DEFAULT_SUITEFILE)
@click.option("--outfile", "-o",
              help="File to store the results into. Defaults to ...")
@click.option("--logconfig", "-l",
              help="Configuration file for the logger.")
def runner(suite, outfile, logconfig):
    benchrunner = Benchrunner()
    benchrunner.main(suite, outfile, logconfig)


@click.command()
@click.argument('report')
@click.option("--influxdburl", "-u", default=DEFAULT_INFLUXURL,
              help="The URL of InfluxDB. Defaults to a local setup (%s)." % DEFAULT_INFLUXURL)
@click.option("--database", "-d", default=DEFAULT_INFLUXDB,
              help="The Influx database to upload to. Defaults to '%s'." % DEFAULT_INFLUXDB)
@click.option("--timestamp", "-t",
              help="Timestamp to use for the upload. If given, overwrites those in the report files.")
@click.option("--precision", "-p", help="The precision of the timestamp.")
def upload(report, influxdburl, database, timestamp, precision):
    uploader = InfluxUploader()
    uploader.main(report, influxdburl, database, timestamp, precision)


@click.command()
def render():
    pass

main.add_command(runner)
main.add_command(upload)
main.add_command(render)


if __name__ == '__main__':
    main()
