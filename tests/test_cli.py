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
from nose.tools import eq_, raises
from .utils import coverage_opts

"""
Contains basic CLI tests for all subcommands,
including integration tests for subcommand collaboration.
"""

__docformat__ = "restructuredtext en"
__revision__ = "$Id$"


INFLUX = "http://localhost:8086"
INFLUXDB = "sdperf"
HERE = os.path.abspath(os.path.dirname(__file__))
BENCH = os.path.normpath(os.path.join(HERE, "..", "bench.py"))
DEVNULL = open(os.devnull, "w")
DATADIR = os.path.join(HERE, "testdata")
SUITE = os.path.join(DATADIR, "dummy.json")


class RunnerTest(unittest.TestCase):
    REPORTFILE = "report_tmp.json"

    def tearDown(self):
        if os.path.exists(self.REPORTFILE):
            os.remove(self.REPORTFILE)

    def test_trivial_run(self):
        cmdline = ["python"] + coverage_opts() + [
            BENCH, "runner",
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
            BENCH, "runner",
            "--suite", SUITE,
            "-o", self.REPORTFILE,
            "--verbose"
        ]
        rc = subprocess.check_call(cmdline, stdout=DEVNULL, stderr=DEVNULL)

        # 1. exit code is zero
        # 2. there are some sysinfos

        eq_(rc, 0)
        report = json.load(open(self.REPORTFILE))
        sysinfos = report["Sysinfos"]
        assert sysinfos


class RendererTest(unittest.TestCase):
    RENDER_FILE = "render.html"
    REPORT1 = os.path.join(DATADIR, "report.json")
    REPORT2 = os.path.join(DATADIR, "report2.json")

    def tearDown(self):
        try:
            os.remove(self.RENDER_FILE)
        except OSError:
            pass

    def test_render_simple(self):
        # the simplest case: render just one report
        cmdline = ["python"] + coverage_opts() + [
            BENCH, "render",
            self.REPORT1,
            "-o", self.RENDER_FILE
        ]
        rc = subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        eq_(rc, 0)
        # The output differs for different OSes
        # Retain for on-demand usage though
        # html_as_expected = filecmp.cmp(os.path.join(self.DATADIR, "render_simple.html"),
        #                               self.RENDER_FILE)
        # assert html_as_expected

    def test_render_two(self):
        # render two benchmark results
        cmdline = ["python"] + coverage_opts() + [
            BENCH, "render",
            self.REPORT1,
            self.REPORT2,
            "-o", self.RENDER_FILE
        ]
        rc = subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        eq_(rc, 0)
        # The output differs for different OSes
        # Retain for on-demand usage though
        # html_as_expected = filecmp.cmp(os.path.join(self.DATADIR, "render_two.html"),
        #                               self.RENDER_FILE)
        # assert html_as_expected

    # Rendering with reference seems to be broken.
    # Include this tests though: as change/regression detector.
    @raises(subprocess.CalledProcessError)
    def test_render_reference(self):
        # render with reference
        cmdline = ["python"] + coverage_opts() + [
            BENCH, "render",
            self.REPORT1,
            "-r", self.REPORT2,
            "-o", self.RENDER_FILE
        ]
        subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_render_trend(self):
        # render two benchmark results with trend
        cmdline = ["python"] + coverage_opts() + [
            BENCH, "render",
            self.REPORT1,
            self.REPORT2,
            "-t",
            "-o", self.RENDER_FILE
        ]
        rc = subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        eq_(rc, 0)
        # The output differs for different OSes
        # Retain for on-demand usage though
        # html_as_expected = filecmp.cmp(os.path.join(self.DATADIR, "render_trend.html"),
        #                                self.RENDER_FILE)
        # assert html_as_expected


class UploaderTest(unittest.TestCase):
    def test_basic_upload(self):
        rc = subprocess.check_call(["python"] + coverage_opts() + [
            BENCH, "upload",
            "--filename=%s" % os.path.join(HERE, "testdata", "report.json"),
            "--influxdburl=%s" % INFLUX,
            "--database=%s" % INFLUX
        ], stdout=subprocess.PIPE)
        eq_(rc, 0)

    # TODO: upload without file given should be rejected by the CLI
    # test CLI!
    # upload blocks?


class Test_Integration(unittest.TestCase):
    REPORTFILE = os.path.join(HERE, "report_tmp.json")
    RENDERFILE = "render.html"

    def setUp(self):
        cmdline = [
            "python",
            BENCH,
            "runner",
            "--suite", os.path.join(HERE, "testdata", "dummy.json"),
            "-o", self.REPORTFILE
        ]
        subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def tearDown(self):
        if os.path.exists(self.REPORTFILE):
            os.remove(self.REPORTFILE)
        if os.path.exists(self.RENDERFILE):
            os.remove(self.RENDERFILE)

    def test_upload(self):
        rc = subprocess.check_call(["python"] + coverage_opts() + [
            BENCH,
            "upload",
            "--filename=%s" % self.REPORTFILE,
            "--influxdburl=%s" % INFLUX,
            "--database=%s" % INFLUXDB
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        eq_(rc, 0)

    def test_render(self):
        cmdline = ["python"] + coverage_opts() + [
            BENCH,
            "render",
            self.REPORTFILE,
            "-o", self.RENDERFILE
        ]
        rc = subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        eq_(rc, 0)


# Allow running this testfile directly
if __name__ == "__main__":
    unittest.main()