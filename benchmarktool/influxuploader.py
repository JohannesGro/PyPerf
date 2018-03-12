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
    RELEVANT_SYSINFOS = {
        "Current User": "user",
        "CPU Count (locial CPUs)": "CPU_count",
        "Memory Total (MB)": "memory_total",
        "OS-Platform": "OS",
        "Processor": "CPU",
        "VM running?: (probably) ": "VM"
    }

    def extract_tags(self, sysinfo):
        tags = {}
        for info, tag_name in self.RELEVANT_SYSINFOS.iteritems():
            tags[tag_name] = sysinfo[info]
        return tags

    def upload_to_influxdb(self, lines, influxurl, database, precision):
        precision = precision or "u"

        rsp = requests.post("%s/write?db=%s&precision=%s" % (influxurl, database, precision),
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

    def fieldname(self, benchname):
        parts = benchname.split("bench_")
        if len(parts) < 2:
            raise Exception("Error: the bench name '%s' " % benchname +
                            "doesnt follow the convention 'bench_<name>'")
        return parts[1]

    def aggregate_series(self, bench, series):
        fieldprefix = self.fieldname(bench)
        return {
            "%s_avr" % fieldprefix: sum(series) / len(series),
            "%s_min" % fieldprefix: min(series),
            "%s_max" % fieldprefix: max(series)
        }

    def extract_timestamp(self, sysinfos):
        time_iso = sysinfos["Current Time (UTC)"]
        return dateparser.parse(time_iso).strftime('%s%f')

    def main(self, filename, influxurl, database, timestamp, precision):
        with open(filename, "r") as fd:
            results = json.load(fd)
            sysinfos = results["Sysinfos"]

            time_epoch = timestamp or self.extract_timestamp(sysinfos)

            tags = self.extract_tags(sysinfos)
            tags["hostname"] = self.extract_hostname(sysinfos)
            tags_str = ",".join(["%s=%s" % (tagname, tagvalue)
                                 for tagname, tagvalue in tags.iteritems()])
            lines = []
            fields = {}
            for benchmark, benchmark_results in results["results"].iteritems():
                for bench, bench_results in benchmark_results["data"].iteritems():
                    values = bench_results["value"]
                    if len(values) > 1:
                        fields.update(self.aggregate_series(bench, bench_results["value"]))

                fields_str = ",".join(["%s=%s" % (name, value)
                                       for name, value in fields.iteritems()])
                lines.append(self.MSG_TMPL % (benchmark, tags_str, fields_str, time_epoch))
            self.upload_to_influxdb(lines, influxurl, database, precision)
