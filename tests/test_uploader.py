# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

import unittest
import os
import requests
from nose.tools import raises, eq_
from mock import patch

from pyperf import uploader
from pyperf.influxmock import InfluxMock
from pyperf.exceptions import PyperfError


class TestInfluxdbUploader(unittest.TestCase):
    influxdburl = "http://localhost:8086"
    database = "_test"
    here = os.path.abspath(os.path.dirname(__file__))
    testdata = os.path.join(here, "testdata")

    @classmethod
    def setUpClass(cls):
        if "FAKEINFLUX" in os.environ:
            cls.orig_env = os.environ.copy()
            del os.environ["FAKEINFLUX"]
        else:
            cls.orig_env = None

    @classmethod
    def tearDownClass(cls):
        if cls.orig_env:
            os.environ = cls.orig_env
        try:
            os.remove(".influxdata")
        except OSError:
            pass
        try:
            os.remove(".influxurl")
        except OSError:
            pass

    def setUp(self):
        self.influxmock = InfluxMock()

    def test_happy_case(self):
        with patch('pyperf.uploader.requests.post', new=self.influxmock):
            uploader.upload_2_influx(os.path.join(self.testdata, "report_happy.json"),
                                     self.influxdburl, self.database)
            data = self.influxmock.data_last
            url = self.influxmock.url_last
            benchmarks = sorted(data.split("\n"))
            benchmark_a, benchmark_b = benchmarks

            assert benchmark_a.startswith("BenchmarkA")
            assert benchmark_a.find("user=wen") != -1
            assert benchmark_a.find("a1_min=0.01") != -1
            assert benchmark_a.find("a2_avr=6") != -1

            assert benchmark_b.startswith("BenchmarkB")
            assert benchmark_b.find("user=wen") != -1
            assert benchmark_b.find("b1_min=0.01") != -1
            assert benchmark_b.find("b2_avr=6") != -1

            # but the benchmark lines arent mangled
            assert benchmark_a.find("b1") == -1
            assert benchmark_b.find("a1") == -1

            assert url.find("precision=s") != -1

    def test_no_measurements(self):
        with patch('pyperf.uploader.requests.post', new=self.influxmock):
            # if there are no measurements, just do nothing
            uploader.upload_2_influx(os.path.join(self.testdata, "report_no_measurements.json"),
                                     self.influxdburl, self.database)
            data = self.influxmock.data_last
            eq_(data, None)

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

    def test_with_additional_values(self):
        with patch('pyperf.uploader.requests.post', new=self.influxmock):
            uploader.upload_2_influx(os.path.join(self.testdata, "report.json"),
                                     self.influxdburl, self.database, values="buildno:15.2.1")
            lp_msg = self.influxmock.data_last
            assert lp_msg.find("buildno=15.2.1") != -1

    def test_with_additional_tags(self):
        with patch('pyperf.uploader.requests.post', new=self.influxmock):
            uploader.upload_2_influx(os.path.join(self.testdata, "report.json"),
                                     self.influxdburl, self.database, add_tags="arch:x64")
            lp_msg = self.influxmock.data_last
            assert lp_msg.find("arch=x64") != -1

    def test_report_with_number(self):
        with patch('pyperf.uploader.requests.post', new=self.influxmock):
            uploader.upload_2_influx(os.path.join(self.testdata, "report_number.json"),
                                     self.influxdburl, self.database)
            lp_msg = self.influxmock.data_last
            assert lp_msg.find("sqlstms=0") != -1

    @raises(requests.ConnectionError)
    @patch('pyperf.uploader.requests.post',
           new=InfluxMock(exception=requests.ConnectionError))
    def test_failed_connection(self):
        uploader.upload_2_influx(os.path.join(self.testdata, "report.json"),
                                 self.influxdburl, self.database)

    @raises(Exception)
    @patch('pyperf.uploader.requests.post', new=InfluxMock(sc=500))
    def test_influx_error(self):
        uploader.upload_2_influx(os.path.join(self.testdata, "report.json"),
                                 self.influxdburl, self.database)

    def test_multiple_benchmarks_one_without_data(self):
        with patch('pyperf.uploader.requests.post', new=self.influxmock):
            uploader.upload_2_influx(os.path.join(self.testdata, "report_one_valid_one_invalid.json"),
                                     self.influxdburl, self.database)
            data = self.influxmock.data_last
            url = self.influxmock.url_last
            benchmarks = sorted(data.split("\n"))
            assert len(benchmarks) == 1

            benchmark = benchmarks[0]

            assert benchmark.startswith("BenchmarkA")
            assert benchmark.find("user=wen") != -1
            assert benchmark.find("a1_min=0.01") != -1
            assert benchmark.find("a2_avr=6") != -1

            assert url.find("precision=s") != -1

    def test_upload_with_uploadconfig(self):
        with patch('pyperf.uploader.requests.post', new=self.influxmock):
            uploader.upload_2_influx(os.path.join(self.testdata, "report.json"),
                                     self.influxdburl,
                                     self.database,
                                     uploadconfig=os.path.join(self.testdata, "uploadconfig.json"))
            data = self.influxmock.data_last
            assert "cpu=x86_64" in data

    @raises(PyperfError)
    def test_upload_with_broken_uploadconfig(self):
        uploader.upload_2_influx(os.path.join(self.testdata, "report.json"), self.influxdburl, self.database,
                                 uploadconfig=os.path.join(self.testdata, "uploadconfig_broken.json"))

    def test_upload_with_uploadconfig_with_broken_tag(self):
        with patch('pyperf.uploader.requests.post', new=self.influxmock):
            uploader.upload_2_influx(os.path.join(self.testdata, "report.json"),
                                     self.influxdburl,
                                     self.database,
                                     uploadconfig=os.path.join(self.testdata, "uploadconfig_invalid_sysinfo.json"))
            data = self.influxmock.data_last
            assert "foo=bar" not in data


def test_convert_to_timestamp():
    eq_(uploader.convert_to_timestamp("2018-03-13T15:40:04.859709"), "1520955604")
    eq_(uploader.convert_to_timestamp("1970-01-01T00:0:00.000000"), "0")


# Further testcases:
# * tagging:
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
