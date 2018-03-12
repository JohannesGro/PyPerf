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
from nose.tools import eq_
from .utils import coverage_opts

"""
Contains basic CLI tests for the 'runner' subcommand
"""

__docformat__ = "restructuredtext en"
__revision__ = "$Id$"


class RunnerTest(unittest.TestCase):
    REPORTFILE = "report_tmp.json"

    def tearDown(self):
        if os.path.exists(self.REPORTFILE):
            os.remove(self.REPORTFILE)

    def test_trivial_run(self):
        here = os.path.abspath(os.path.dirname(__file__))
        bench = os.path.normpath(os.path.join(here, "..", "bench.py"))
        cmdline = ["python"] + coverage_opts() + [
            bench, "runner", "--suite", os.path.join(here, "dummy.json"),
            "-o", self.REPORTFILE]
        proc = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        expected = """setUpClass called
setUp called
tearDown called
setUp called
tearDown called
tearDownClass called"""

        stdout = proc.stdout.read()
        rc = proc.wait()

        # 1. exit code is zero
        # 2. std. output as expected (hook prints are there)
        # 3. generated JSON is valid and contains expected values

        eq_(rc, 0)
        assert stdout.find(expected) != -1, "Hooks havent been called"
        report = json.load(open(self.REPORTFILE))
        data = report["results"]["DummyBenchmark"]["data"]
        eq_(data["bench_func1"]["value"], 1)
        eq_(data["bench_func2"]["value"], 2)


# Allow running this testfile directly
if __name__ == "__main__":
    unittest.main()
