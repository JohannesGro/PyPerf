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
  coming after "bench\_"
"""

import requests
import dateutil.parser as dateparser
import json
import os
import datetime
import time
import logging

from .influxmock import InfluxMock
from .log import customlogging
from .exceptions import PyperfError
from .ioservice import loadJSONData


__docformat__ = "restructuredtext en"
__revision__ = "$Id$"

# Exported objects
__all__ = ["upload_2_influx", "InvalidReportError"]


# <measurement>[,<tag_key>=<tag_value>[,...]] <field_key>=<field_value>[,...] [<timestamp>]
MSG_TMPL = "%s,%s %s %s"


EPOCH = datetime.datetime(1970, 1, 1)
MAX_UPLOAD_RETRIES = 5
UPLOAD_SLEEP = 1


logger = logging.getLogger(__name__)


class InvalidReportError(Exception):
    pass


class ValuesParseError(Exception):
    def __init__(self, values):  # pylint: disable=super-init-not-called
        self.values = values

    def __str__(self):
        return "Additional values '%s' cannot be parsed" % self.values


def extract_tags(sysinfo, config):
    """
    This function will either extract the relevant sysinfo,
    or extract the sysinfos that are specified in the config file
    and return it as a new dict to be used as tags

    The relevant measures from the sysinfos are:

    * user
    * cpu_cores_logical
    * mem_total
    * os
    * vm

    If cdb can be imported, then these will also be added to the relevant sysinfos:

    * ce_minor
    * ce_sl
    * dbms_driver
    * dbms_version

    :param sysinfo: The sysinfo of a report
    :param config: The config file containing the mapping from sysInfos to influx tags
    :return: A dict containing the relevant sysinfo
    """
    # Contains stuff, which is useful as metadata and doesnt have much variability in values
    # https://docs.influxdata.com/influxdb/v1.4/concepts/schema_and_data_layout/
    #
    tags = {}
    if config:
        infos_to_upload = loadJSONData(config)
    else:
        infos_to_upload = {"user": "user",
                           "cpu_cores_logical": "cpu_count",
                           "mem_total": "mem_total",
                           "os": "os",
                           "vm": "vm"}
        try:
            import cdb
            if cdb:
                infos_to_upload.update({"ce_minor": "ce_version",
                                        "ce_sl": "ce_sl",
                                        "dbms_driver": "dbms_driver",
                                        "dbms_version": "dbms_version"})
        except ImportError:
            # We can just ignore this error since we only want to know here weather the
            # cdb relevant data could be gathered or not.
            pass

    for info, tag_name in infos_to_upload.items():
        try:
            tags[tag_name] = sysinfo[info]
        except KeyError:
            logger.info("Couldn't find %s in the systemInfos of the report file. It will be skipped.", info)
            continue
    return tags


def upload_to_influxdb(lines, influxurl, database, precision):
    """
    This function will upload the data into an influxdb by making a post request.

    :param lines: The lines to upload
    :param influxurl: The URL of the Influx instance
    :param database: The database of the Influx instance to store the lines
    :param precision: The precision of the data, may be 's' or 'ms'
    :return:
    """
    if os.environ.get("FAKEINFLUX", "false") == "true":
        requests.post = InfluxMock()

    for trial in range(MAX_UPLOAD_RETRIES+1):
        try:
            rsp = requests.post("%s/write?db=%s&precision=%s" % (influxurl, database, precision),
                                data="\n".join(lines))
            if (rsp.status_code < 200 or rsp.status_code >= 400):
                raise Exception("Error while uploading benchmark results: %i ('%s')"
                                % (rsp.status_code, rsp.text))
        except requests.ConnectionError as ce:
            if trial < MAX_UPLOAD_RETRIES:
                # TODO: log the trial
                time.sleep(UPLOAD_SLEEP)
                continue
            raise ce


def extract_hostname(sysinfo):
    """
    This function extracts the hostnames from the sysinfos.

    :param sysinfo: The sysinfos of the report that gets uploaded
    :return: The hostname that executed the benchmark
    :raises Exception: when no suitable hostname could be found
    """
    hostnames = sysinfo["hostnames"]
    for name in hostnames:
        if "." not in name and name != "localhost":
            return name
    raise Exception("Could not find a suitable hostname")


def fieldname(benchname):
    """
    This function strips the 'bench_' from a bench-method's name to normalize it.

    :param benchname: The benchname to normalize
    :return: The normalized method name.
    """
    parts = benchname.split("bench_")
    if len(parts) < 2:
        raise Exception("Error: the bench name '%s' " % benchname +
                        "doesnt follow the convention 'bench_<name>'")
    return parts[1]


def aggregate_series(bench, series):
    """
    This method calculates the average, minimun and maximum for a series.

    :param bench: The bench of the series to aggregate
    :param series: The benches time series
    :return: A dict containing the aggregated values of the series
    """
    fieldprefix = fieldname(bench)
    return {
        "%s_avr" % fieldprefix: sum(series) / len(series),
        "%s_min" % fieldprefix: min(series),
        "%s_max" % fieldprefix: max(series)
    }


def parse_additional_values(values):
    """
    Parses the additional values and returns them as a dict.

    :param values: The additional values to parse
    :return: A dict containing the additional values
    :raises ValuesParseError: when the values could not be identified as key, value pairs
    """
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
    """
    Converts a date in iso-format to an epoch timestamp.

    :param time_iso: The date in iso-format
    :return: The epoch timestamp representation of the date
    """
    dt = dateparser.parse(time_iso)
    return "%i" % ((dt - EPOCH).total_seconds())


def extract_timestamp(sysinfos):
    """
    Extracts the date of a reports sysinfo and returns it as an epoch timestamp

    :param sysinfos: The sysinfo of a report
    :return: Epoch timestamp of the reports date
    """
    return convert_to_timestamp(sysinfos["time"])


def upload_2_influx(reportpath, influxdburl, database, timestamp=None, precision=None, uploadconfig=None,
                    values=None, add_tags=None, logconfig="", debug=False):
    """
        This method uploads a benchmark report to an influx database.

        :param reportpath: The path to the benchmark report to upload
        :param influxdburl: URL of the Inxlux instance
        :param database: The database of the Influx instance to upload the data into
        :param timestamp: The timestamp for uploading into the Influx DB. If :code:`None`,
            the report's timestamp will be used.
        :param precision: The precision of the data. May be 's' or 'ms'
        :param uploadconfig: The configfile containing a dictionary of systemInfos to be used as Tags in Influx
        :param values: Additional values to upload
        :param add_tags: Additional tags to upload
        :param logconfig: the config file for the logging, see :ref:`howto_logging`
        :param debug: whether DEBUG logging shall be enabled or not
        :raises InvalidReportError: When the report could not be parsed or does not contain sysinfos.
        """
    try:
        customlogging.init_logging(logconfig, debug)
    except PyperfError:
        raise
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

        tags = extract_tags(sysinfos, uploadconfig)
        tags["hostname"] = extract_hostname(sysinfos)
        if add_tags:
            tags.update(parse_additional_values(add_tags))

        tags_str = ",".join(["%s=%s" % (tagname, tagvalue)
                             for tagname, tagvalue in tags.items()])

        lines = []

        if "results" not in report:
            raise InvalidReportError("Report '%s' doesn't contain any results." % reportpath)

        invalid_benchmarks = 0

        for benchmark, args_and_data in report["results"].items():
            fields = {}
            data = args_and_data["data"]
            if not data:
                logger.warning("Report '%s' doesn't contain any result data for the benchmark '%s'.",
                               reportpath, benchmark)
                invalid_benchmarks += 1
                continue
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

        if invalid_benchmarks == len(report["results"]):
            raise InvalidReportError("Report '%s' doesn't contain any result data for any benchmark."
                                     % reportpath)

        if lines:
            upload_to_influxdb(lines, influxdburl, database, precision)
