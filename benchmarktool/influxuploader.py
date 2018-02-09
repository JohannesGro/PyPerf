# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""
InfluxdbUploader loads benchmark run results into an Influx DB.

The data mapping is as follows:
* The classname maps to an Influx Measurement
* Sysinfo (reasonable subset of) maps to Influx Tags
* Values of type "time series" are aggregated and mapped to Influx Fields:
  "<name>_avg", "<name>_max" and "<name>_min", where <name> is the string
  coming after "bench_"

"""

import argparse
import sys
import requests
import dateutil.parser as dateparser
import json

# TODO
# * code verbessern
# * testen
# * Umstrukturieren:
#    - UI code raus
#    - Zugang ueber entry-point weg
#    - An templates (setuptools, cli apps) orientieren
#

__docformat__ = "restructuredtext en"
__revision__ = "$Id$"

# Exported objects
__all__ = []


class InfluxUploader(object):
    # <measurement>[,<tag_key>=<tag_value>[,...]] <field_key>=<field_value>[,...] [<timestamp>]
    MSG_TMPL = "%s,%s %s %s"

    # Contains stuff, which is useful as metadata and doesnt have much variability in values
    # https://docs.influxdata.com/influxdb/v1.4/concepts/schema_and_data_layout/
    #
    RELEVANT_SYSINFOS = [
        "Current User",
        "CPU Count (locial CPUs)",
        "CPU Count (physical CPUs)",
        "Memory Total (MB)",
        "OS-Platform",
        "Processor",
        "VM running?: (probably) "
    ]

    parser = argparse.ArgumentParser(description=__doc__, prog="Uploader")
    parser.add_argument("--influxdburl", "-u",
                        help="The URL to the Influx DBMS to upload the results onto.")
    parser.add_argument("--database", "-d", help="The database to upload the results into.")
    parser.add_argument("--filename", "-f", help="JSON report to upload.")

    def __init__(self, args):
        # Grab the self.args from argv
        if type(args) == argparse.Namespace:
            prev = sys.argv
            sys.argv = []
            self.args = self.parser.parse_args(args=None, namespace=args)
            sys.argv = prev
        else:
            self.args = self.parser.parse_args(args)

    def extract_tags(self, sysinfo):
        tags = {}
        for info in self.RELEVANT_SYSINFOS:
            tags[info.replace(" ", "_")] = sysinfo[info]
        return tags

    def upload_to_influxdb(self, lines):
        influxurl = self.args.influxdburl
        database = self.args.database

        rsp = requests.post("%s/write?db=%s&precision=s" % (influxurl, database),
                            data="\n".join(lines))

        if (rsp.status_code < 200 or rsp.status_code >= 400):
            raise Exception("Error while uploading benchmark results: %i ('%s')"
                            % (rsp.status_code, rsp.text))

    def extract_hostname(self, sysinfo):
        hostnames = sysinfo["Hostnames"]
        for name in hostnames:
            if "." not in name and name != "localhost":
                return name
        raise Exception("Could not find a suitable hostname")

    def aggregate_time_series(self, bench, series):
        return {
            "%s_avr" % bench: sum(series) / len(series),
            "%s_min" % bench: min(series),
            "%s_max" % bench: max(series)
        }

    def main(self):
        filename = self.args.filename

        with open(filename, "r") as fd:
            results = json.load(fd)
            sysinfos = results["Sysinfos"]
            time_iso = sysinfos["Current Time (UTC)"]
            time_epoch = dateparser.parse(time_iso).strftime('%s')
            tags = self.extract_tags(sysinfos)
            tags["hostname"] = self.extract_hostname(sysinfos)
            tags_str = ",".join(["%s=%s" % (tagname, tagvalue)
                                 for tagname, tagvalue in tags.iteritems()])
            lines = []
            fields = {}
            for benchmark, benchmark_results in results["results"].iteritems():
                for bench, bench_results in benchmark_results["data"].iteritems():
                    if bench_results["type"] == "time_series":
                        fields.update(self.aggregate_time_series(bench, bench_results["value"]))
                fields_str = ",".join(["%s=%s" % (name, value)
                                       for name, value in fields.iteritems()])
                lines.append(self.MSG_TMPL % (bench, tags_str, fields_str, time_epoch))
            self.upload_to_influxdb(lines)
