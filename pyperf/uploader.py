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
import datetime
import time

from .influxmock import InfluxMock


__docformat__ = "restructuredtext en"
__revision__ = "$Id$"

# Exported objects
__all__ = ["upload_2_influx", "InvalidReportError"]


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


EPOCH = datetime.datetime(1970, 1, 1)
MAX_UPLOAD_RETRIES = 5
UPLOAD_SLEEP = 1


class InvalidReportError(Exception):
    pass


class ValuesParseError(Exception):
    def __init__(self, values):  # pylint: disable=super-init-not-called
        self.values = values

    def __str__(self):
        return "Additional values '%s' cannot be parsed" % self.values


def extract_tags(sysinfo):
    tags = {}
    for info, tag_name in RELEVANT_SYSINFOS.items():
        tags[tag_name] = sysinfo[info]
    return tags


def upload_to_influxdb(lines, influxurl, database, precision):
    if os.environ.get("FAKEINFLUX", "false") == "true":
        requests.post = InfluxMock()

    for trial in range(MAX_UPLOAD_RETRIES+1):
        try:
            rsp = requests.post("%s/write?db=%s&precision=%s" % (influxurl, database, precision),
                                data="\n".join(lines))
            if (rsp.status_code < 200 or rsp.status_code >= 400):
                raise Exception("Error while uploading benchmark results: %i ('%s')"
                                % (rsp.status_code, rsp.text))
        except requests.ConnectionError, ce:
            if trial < MAX_UPLOAD_RETRIES:
                # TODO: log the trial
                time.sleep(UPLOAD_SLEEP)
                continue
            raise ce


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
        parts = pair.split(":")
        if len(parts) == 2:
            key, value = parts
            res[key] = value
        else:
            raise ValuesParseError(values)
    return res


def convert_to_timestamp(time_iso):
    dt = dateparser.parse(time_iso)
    return "%i" % ((dt - EPOCH).total_seconds())


def extract_timestamp(sysinfos):
    return convert_to_timestamp(sysinfos["time"])


def upload_2_influx(reportpath, influxdburl, database, timestamp=None, precision=None,
                    values=None, add_tags=None):
    with open(reportpath, "r") as fd:
        try:
            report = json.load(fd)
        except ValueError:
            raise InvalidReportError("Report '%s' cannot be parsed." % reportpath)

        sysinfos = report["Sysinfos"]
        if len(sysinfos) == 0:
            raise InvalidReportError("Report '%s' doesn't contain sysinfos." % reportpath)

        if not precision:
            precision = "s"
        time_epoch = timestamp or extract_timestamp(sysinfos)

        tags = extract_tags(sysinfos)
        tags["hostname"] = extract_hostname(sysinfos)
        if add_tags:
            tags.update(parse_additional_values(add_tags))

        tags_str = ",".join(["%s=%s" % (tagname, tagvalue)
                             for tagname, tagvalue in tags.items()])

        lines = []

        if "results" not in report:
            raise InvalidReportError("Report '%s' doesn't contain any results." % reportpath)

        for benchmark, args_and_data in report["results"].items():
            fields = {}
            data = args_and_data["data"]
            if not data:
                raise InvalidReportError(
                    "Report '%s' doesn't contain any result data for the benchmark '%s'."
                    % (reportpath, benchmark)
                )
            for bench, bench_results in args_and_data["data"].items():

                report_values = bench_results["value"]
                if isinstance(report_values, list):
                    if report_values:
                        fields.update(aggregate_series(bench, report_values))
                else:
                    fields[fieldname(bench)] = report_values
                if values:
                    fields.update(parse_additional_values(values))

            if fields:
                fields_str = ",".join(["%s=%s" % (name, value)
                                       for name, value in fields.items()])
                lines.append(MSG_TMPL % (benchmark, tags_str, fields_str, time_epoch))

        if lines:
            upload_to_influxdb(lines, influxdburl, database, precision)
