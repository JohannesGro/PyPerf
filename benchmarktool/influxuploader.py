# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""
The uploader loads benchmark run results (currently) into an Influx DB .
We'll probably make it more generic in the future.

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
import os

from influxmock import InfluxMock


__docformat__ = "restructuredtext en"
__revision__ = "$Id$"

# Exported objects
__all__ = ["upload", "InvalidReportError"]


# <measurement>[,<tag_key>=<tag_value>[,...]] <field_key>=<field_value>[,...] [<timestamp>]
MSG_TMPL = "%s,%s %s %s"

# Contains stuff, which is useful as metadata and doesnt have much variability in values
# https://docs.influxdata.com/influxdb/v1.4/concepts/schema_and_data_layout/
#
RELEVANT_SYSINFOS = {
    "user": "user",
    "cpu_cores_logical": "cpu_count",
    "mem_total": "mem_total",
    "os": "os",
    # "Processor": "CPU",
    "vm": "vm"
}


class InvalidReportError(Exception):
    pass


def extract_tags(sysinfo):
    tags = {}
    for info, tag_name in RELEVANT_SYSINFOS.iteritems():
        tags[tag_name] = sysinfo[info]
    return tags


def upload_to_influxdb(lines, influxurl, database, precision):
    if os.environ.get("FAKEINFLUX", "false") == "true":
        requests.post = InfluxMock()

    rsp = requests.post("%s/write?db=%s&precision=%s" % (influxurl, database, precision),
                        data="\n".join(lines))

    if (rsp.status_code < 200 or rsp.status_code >= 400):
        raise Exception("Error while uploading benchmark results: %i ('%s')"
                        % (rsp.status_code, rsp.text))


def extract_hostname(sysinfo):
    hostnames = sysinfo["hostnames"]
    for name in hostnames:
        if "." not in name and name != "localhost":
            return name
    raise Exception("Could not find a suitable hostname")


def fieldname(benchname):
    parts = benchname.split("bench_")
    if len(parts) < 2:
        raise Exception("Error: the bench name '%s' " % benchname +
                        "doesnt follow the convention 'bench_<name>'")
    return parts[1]


def aggregate_series(bench, series):
    fieldprefix = fieldname(bench)
    return {
        "%s_avr" % fieldprefix: sum(series) / len(series),
        "%s_min" % fieldprefix: min(series),
        "%s_max" % fieldprefix: max(series)
    }


def parse_additional_values(values):
    res = {}
    for pair in values.split(","):
        parts = pair.split("=")
        if len(parts) == 2:
            key, value = parts
            res[key] = value
    return res


def extract_timestamp(sysinfos):
    time_iso = sysinfos["time"]
    return dateparser.parse(time_iso).strftime('%S%f')


def upload(report, influxdburl, database, timestamp=None, precision=None, values=None):
    with open(report, "r") as fd:
        try:
            results = json.load(fd)
        except ValueError:
            raise InvalidReportError("Report '%s' cannot be parsed." % report)

        sysinfos = results["Sysinfos"]
        if len(sysinfos) == 0:
            raise InvalidReportError("Report '%s' doesn't contain sysinfos." % report)

        time_epoch = timestamp or extract_timestamp(sysinfos)

        tags = extract_tags(sysinfos)
        tags["hostname"] = extract_hostname(sysinfos)
        tags_str = ",".join(["%s=%s" % (tagname, tagvalue)
                             for tagname, tagvalue in tags.iteritems()])
        lines = []
        fields = {}

        if "results" not in results:
            raise InvalidReportError("Report '%s' doesn't contain any results." % report)

        for benchmark, benchmark_results in results["results"].iteritems():
            for bench, bench_results in benchmark_results["data"].iteritems():
                report_values = bench_results["value"]
                if isinstance(report_values, list):
                    fields.update(aggregate_series(bench, report_values))
                else:
                    fields[fieldname(bench)] = report_values
                if values:
                    fields.update(parse_additional_values(values))

            fields_str = ",".join(["%s=%s" % (name, value)
                                   for name, value in fields.iteritems()])
            lines.append(MSG_TMPL % (benchmark, tags_str, fields_str, time_epoch))
        upload_to_influxdb(lines, influxdburl, database, precision)
