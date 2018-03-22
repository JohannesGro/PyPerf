# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

import unittest
import os
import requests
from nose.tools import raises
from mock import patch

from pyperf import uploader
from pyperf.influxmock import InfluxMock


class TestInfluxdbUploader(unittest.TestCase):
    influxdburl = "http://con-wen:8086"
    database = "sdperf"
    here = os.path.abspath(os.path.dirname(__file__))
    testdata = os.path.join(here, "testdata")
    influxmock = InfluxMock()

    @classmethod
    def setUpClass(cls):
        if "FAKEINFLUX" in os.environ:
            cls.orig_env = os.environ.copy()
            del os.environ["FAKEINFLUX"]
        else:
            cls.orig_env = None

    @classmethod
    def teardDownClass(cls):
        if cls.orig_env:
            os.environ = cls.orig_env

    @patch('pyperf.uploader.requests.post', new=influxmock)
    def test_happy_case(self):
        uploader.upload_2_influx(os.path.join(self.testdata, "report_happy.json"),
                                 self.influxdburl, self.database)
        lp_msg = self.influxmock.data_last
        assert lp_msg.startswith("SomeBenchmark")
        assert lp_msg.find("user=wen") != -1
        assert lp_msg.find("runtime_avr=0.01") != -1

    @raises(uploader.InvalidReportError)
    def test_sysinfos_incomplete(self):
        uploader.upload_2_influx(os.path.join(self.testdata, "report_no_sysinfos.json"),
                                 self.influxdburl, self.database)

    @raises(uploader.InvalidReportError)
    def test_no_results(self):
        uploader.upload_2_influx(os.path.join(self.testdata, "report_no_results.json"),
                                 self.influxdburl, self.database)

    @raises(uploader.InvalidReportError)
    def test_invalid_report(self):
        uploader.upload_2_influx(os.path.join(self.testdata, "report_invalid.json"),
                                 self.influxdburl, self.database)

    @patch('pyperf.uploader.requests.post', new=influxmock)
    def test_with_additional_values(self):
        uploader.upload_2_influx(os.path.join(self.testdata, "report.json"),
                                 self.influxdburl, self.database, values="buildno=15.2.1")
        lp_msg = self.influxmock.data_last
        assert lp_msg.find("buildno=15.2.1") != -1

    @patch('pyperf.uploader.requests.post', new=influxmock)
    def test_report_with_number(self):
        uploader.upload_2_influx(os.path.join(self.testdata, "report_number.json"),
                                 self.influxdburl, self.database)
        lp_msg = self.influxmock.data_last
        assert lp_msg.find("sqlstms=0") != -1

    @raises(requests.exceptions.ConnectionError)
    @patch('pyperf.uploader.requests.post',
           new=InfluxMock(exception=requests.exceptions.ConnectionError))
    def test_failed_connection(self):
        uploader.upload_2_influx(os.path.join(self.testdata, "report.json"),
                                 self.influxdburl, self.database)

    @raises(Exception)
    @patch('pyperf.uploader.requests.post', new=InfluxMock(sc=500))
    def test_influx_error(self):
        uploader.upload_2_influx(os.path.join(self.testdata, "report.json"),
                                 self.influxdburl, self.database)


# Further testcases:
# * tagging:
#   - happy case
#   - nothing relevant in sysinfo
#   - empty sysinfo
#
# * aggregating_time_series:
#   - empty series
#   - trivial
#   - second trivial
#   - a big one

# * extract_hostname:
#   - happy case
#   - no valid hostname there
#   - empty dict
