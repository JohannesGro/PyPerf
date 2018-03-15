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


class RunnerTest(unittest.TestCase):
    REPORTFILE = "report_tmp.json"
    HERE = os.path.abspath(os.path.dirname(__file__))
    BENCH = os.path.normpath(os.path.join(HERE, "..", "bench.py"))
    SUITE = os.path.join(HERE, "testdata", "dummy.json")
    DEVNULL = open(os.devnull, "w")

    def tearDown(self):
        if os.path.exists(self.REPORTFILE):
            os.remove(self.REPORTFILE)

    def test_trivial_run(self):
        cmdline = ["python"] + coverage_opts() + [
            self.BENCH, "runner", "--suite", self.SUITE, "-o", self.REPORTFILE
        ]
        proc = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=self.DEVNULL)

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
            self.BENCH, "runner", "--suite", self.SUITE, "-o", self.REPORTFILE,
            "--verbose"
        ]
        rc = subprocess.check_call(cmdline, stdout=self.DEVNULL, stderr=self.DEVNULL)

        # 1. exit code is zero
        # 2. there are some sysinfos

        eq_(rc, 0)
        report = json.load(open(self.REPORTFILE))
        sysinfos = report["Sysinfos"]
        assert sysinfos


class RendererTest(unittest.TestCase):
    RENDER_FILE = "render.html"
    HERE = os.path.abspath(os.path.dirname(__file__))
    DATADIR = os.path.join(HERE, "testdata")
    REPORT1 = os.path.join(DATADIR, "report.json")
    REPORT2 = os.path.join(DATADIR, "report2.json")
    BENCH = os.path.normpath(os.path.join(HERE, "..", "bench.py"))

    def tearDown(self):
        try:
            os.remove(self.RENDER_FILE)
        except OSError:
            pass

    def test_render_simple(self):
        # the simplest case: render just one report
        cmdline = ["python"] + coverage_opts() + \
                  [self.BENCH, "render", self.REPORT1, "-o", self.RENDER_FILE]
        rc = subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        eq_(rc, 0)
        # The output differs for different OSes
        # Retain for on-demand usage though
        # html_as_expected = filecmp.cmp(os.path.join(self.DATADIR, "render_simple.html"),
        #                               self.RENDER_FILE)
        # assert html_as_expected

    def test_render_two(self):
        # render two benchmark results
        cmdline = ["python"] + coverage_opts() + \
                  [self.BENCH, "render", self.REPORT1, self.REPORT2, "-o", self.RENDER_FILE]
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
        cmdline = ["python"] + coverage_opts() + \
                  [self.BENCH, "render", self.REPORT1, "-r", self.REPORT2, "-o", self.RENDER_FILE]
        subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_render_trend(self):
        # render two benchmark results with trend
        cmdline = ["python"] + coverage_opts() + \
                  [self.BENCH, "render", self.REPORT1, self.REPORT2, "-t", "-o", self.RENDER_FILE]
        rc = subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        eq_(rc, 0)
        # The output differs for different OSes
        # Retain for on-demand usage though
        # html_as_expected = filecmp.cmp(os.path.join(self.DATADIR, "render_trend.html"),
        #                                self.RENDER_FILE)
        # assert html_as_expected


class UploaderTest(unittest.TestCase):
    def test_basic_upload(self):
        # assumes a running influx on localhost
        # and an 'sdperf' database inside of it
        # TODO: assume less or automate the setup
        here = os.path.abspath(os.path.dirname(__file__))
        bench = os.path.normpath(os.path.join(here, "..", "bench.py"))
        rc = subprocess.check_call(["python"] + coverage_opts() + [
            bench, "upload", "--filename=%s" % os.path.join(here, "testdata", "report.json"),
            "--influxdburl=http://con-wen.contact.de:8086", "--database=sdperf"
        ], stdout=subprocess.PIPE)
        eq_(rc, 0)


class Test_Integration(unittest.TestCase):
    here = os.path.abspath(os.path.dirname(__file__))
    REPORTFILE = os.path.join(here, "report_tmp.json")
    RENDERFILE = "render.html"
    BENCH = os.path.normpath(os.path.join(here, "..", "bench.py"))

    def setUp(self):
        cmdline = [
            "python", self.BENCH, "runner", "--suite",
            os.path.join(self.here, "testdata", "dummy.json"),
            "-o", self.REPORTFILE
        ]
        subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def tearDown(self):
        if os.path.exists(self.REPORTFILE):
            os.remove(self.REPORTFILE)
        if os.path.exists(self.RENDERFILE):
            os.remove(self.RENDERFILE)

    def test_upload(self):
        # assumes a running influx on con-wen
        # and an 'sdperf' database inside of it
        # TODO: assume less or automate the setup
        rc = subprocess.check_call(["python"] + coverage_opts() + [
            self.BENCH, "upload", "--filename=%s" % self.REPORTFILE,
            "--influxdburl=http://con-wen.contact.de:8086", "--database=sdperf"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        eq_(rc, 0)

    def test_render(self):
        cmdline = ["python"] + coverage_opts() + [
            self.BENCH, "render", self.REPORTFILE, "-o", self.RENDERFILE
        ]
        rc = subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        eq_(rc, 0)


# Allow running this testfile directly
if __name__ == "__main__":
    unittest.main()
