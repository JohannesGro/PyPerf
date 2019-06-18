#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

import unittest
import subprocess
import os
import json
import six
from nose.tools import eq_, raises, assert_not_equals
from .utils import coverage_opts

"""
Contains basic CLI tests for all subcommands,
including integration tests for subcommand collaboration.
"""

__docformat__ = "restructuredtext en"
__revision__ = "$Id$"


INFLUX = "http://localhost:8086"
INFLUXDB = "_test"
HERE = os.path.abspath(os.path.dirname(__file__))
BENCH = os.path.normpath(os.path.join(HERE, "..", "bench.py"))
DEVNULL = open(os.devnull, "w")
DATADIR = os.path.join(HERE, "testdata")
SUITE = os.path.join(DATADIR, "dummy.json")
SUITE_BROKEN = os.path.join(DATADIR, "suite_broken.json")
SUITE_BENCH_BROKEN = os.path.join(DATADIR, "suite_bench_broken.json")


class RunnerTest(unittest.TestCase):
    REPORTFILE = "report_tmp.json"

    def tearDown(self):
        if os.path.exists(self.REPORTFILE):
            os.remove(self.REPORTFILE)

    def test_trivial_run(self):
        cmdline = ["python"] + coverage_opts() + [
            BENCH, "run",
            "--suite", SUITE,
            "-o", self.REPORTFILE
        ]
        proc = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=DEVNULL)

        expected = [
            "setUpClass called",
            "setUp called",
            "tearDown called",
            "setUp called",
            "tearDown called",
            "tearDownClass called"
        ]

        stdout = proc.stdout.read().splitlines()
        if six.PY3:
            stdout = [bytes.decode(entry) for entry in stdout]
        rc = proc.wait()

        # 1. exit code is zero
        # 2. std. output as expected (hook prints are there)
        # 3. generated JSON is valid and contains expected values

        eq_(rc, 0)
        eq_(expected, stdout)
        report = json.load(open(self.REPORTFILE))
        data = report["results"]["DummyBenchmark"]["data"]
        eq_(data["bench_func1"]["value"], 1)
        eq_(data["bench_func2"]["value"], 2)

    def test_run_with_verbose_sysinfos(self):
        cmdline = ["python"] + coverage_opts() + [
            BENCH, "run",
            "--suite", SUITE,
            "-o", self.REPORTFILE,
            "--verbose"
        ]
        rc = subprocess.call(cmdline, stdout=DEVNULL, stderr=DEVNULL)

        # 1. exit code is zero
        # 2. there are some sysinfos

        eq_(rc, 0)
        report = json.load(open(self.REPORTFILE))
        sysinfos = report["Sysinfos"]
        assert sysinfos

    def test_run_broken_suite(self):
        cmdline = ["python"] + coverage_opts() + [
            BENCH, "run",
            "--suite", SUITE_BROKEN,
            "-o", self.REPORTFILE
        ]
        rc = subprocess.call(cmdline, stdout=DEVNULL, stderr=DEVNULL)
        assert_not_equals(rc, 0)

    def test_run_broken_benchmark(self):
        cmdline = ["python"] + coverage_opts() + [
            BENCH, "run",
            "--suite", SUITE_BENCH_BROKEN,
            "-o", self.REPORTFILE
        ]
        rc = subprocess.call(cmdline, stdout=DEVNULL, stderr=DEVNULL)
        assert_not_equals(rc, 0)


class UploaderTest(unittest.TestCase):
    def test_basic_default_upload(self):
        cmdline = ["python"] + coverage_opts() + [
            BENCH, "upload",
            os.path.join(DATADIR, "report.json"),
            "--url=%s" % INFLUX,
            "--db=%s" % INFLUXDB
        ]
        rc = subprocess.call(cmdline, stdout=DEVNULL, stderr=DEVNULL)
        eq_(rc, 0, "'%s' failed." % subprocess.list2cmdline(cmdline))

    def test_fully_parametrized_upload(self):
        cmdline = ["python"] + coverage_opts() + [
            BENCH, "upload",
            os.path.join(DATADIR, "report.json"),
            "--url=%s" % INFLUX,
            "--db=%s" % INFLUXDB,
            "--ts=%s" % "111111111111ms",
            "--tags=arch:x64",
            "--values=CI:1"
        ]
        rc = subprocess.call(cmdline, stdout=DEVNULL, stderr=DEVNULL)
        eq_(rc, 0, "'%s' failed." % subprocess.list2cmdline(cmdline))

    def test_target_not_supported(self):
        cmdline = ["python"] + coverage_opts() + [
            BENCH, "upload",
            "--target=SAP",
            os.path.join(DATADIR, "report.json"),
        ]
        rc = subprocess.call(cmdline, stdout=DEVNULL, stderr=DEVNULL)
        eq_(rc, 21, "'%s' failed." % subprocess.list2cmdline(cmdline))

    def test_bad_report(self):
        cmdline = ["python"] + coverage_opts() + [
            BENCH, "upload",
            os.path.join(DATADIR, "bad_report.json"),
        ]
        rc = subprocess.call(cmdline, stdout=DEVNULL, stderr=DEVNULL)
        assert_not_equals(rc, 0, "'%s' failed." % subprocess.list2cmdline(cmdline))

    def test_bad_timestamp(self):
        cmdline = ["python"] + coverage_opts() + [
            BENCH, "upload",
            os.path.join(DATADIR, "report.json"),
            "--ts=111XX"
        ]
        rc = subprocess.call(cmdline, stdout=DEVNULL, stderr=DEVNULL)
        eq_(rc, 22, "'%s' failed." % subprocess.list2cmdline(cmdline))

    def test_bad_values(self):
        cmdline = ["python"] + coverage_opts() + [
            BENCH, "upload",
            os.path.join(DATADIR, "report.json"),
            "--values=bad"
        ]
        rc = subprocess.call(cmdline, stdout=DEVNULL, stderr=DEVNULL)
        assert_not_equals(rc, 0, "'%s' failed." % subprocess.list2cmdline(cmdline))


class Test_Integration(unittest.TestCase):
    REPORTFILE = os.path.join(HERE, "report_tmp.json")

    def setUp(self):
        cmdline = [
            "python",
            BENCH,
            "run",
            "--suite", os.path.join(DATADIR, "dummy.json"),
            "-o", self.REPORTFILE
        ]
        subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def tearDown(self):
        if os.path.exists(self.REPORTFILE):
            os.remove(self.REPORTFILE)

    def test_upload(self):
        rc = subprocess.check_call(["python"] + coverage_opts() + [
            BENCH,
            "upload",
            self.REPORTFILE,
            "--url=%s" % INFLUX,
            "--db=%s" % INFLUXDB
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        eq_(rc, 0)


# Allow running this testfile directly
if __name__ == "__main__":
    unittest.main()
