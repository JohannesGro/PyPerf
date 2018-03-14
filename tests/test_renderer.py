#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

import unittest
import subprocess
import os
import filecmp

from nose.tools import eq_, raises
from .utils import coverage_opts

"""
Contains basic CLI tests for the 'render' subcommand
"""

__docformat__ = "restructuredtext en"
__revision__ = "$Id$"


class RendererTest(unittest.TestCase):
    RENDER_FILE = "render.html"
    HERE = os.path.abspath(os.path.dirname(__file__))
    DATADIR = os.path.join(HERE, "testdata")
    REPORT1 = os.path.join(DATADIR, "report.json")
    REPORT2 = os.path.join(DATADIR, "report2.json")
    BENCH = os.path.normpath(os.path.join(HERE, "..", "bench.py"))

    def test_render_simple(self):
        # the simplest case: render just one report
        cmdline = ["python"] + coverage_opts() + \
                  [self.BENCH, "render", self.REPORT1, "-o", self.RENDER_FILE]
        rc = subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        eq_(rc, 0)
        html_as_expected = filecmp.cmp(os.path.join(self.DATADIR, "render_simple.html"),
                                       self.RENDER_FILE)
        assert html_as_expected

    def test_render_two(self):
        # render two benchmark results
        cmdline = ["python"] + coverage_opts() + \
                  [self.BENCH, "render", self.REPORT1, self.REPORT2, "-o", self.RENDER_FILE]
        rc = subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        eq_(rc, 0)
        html_as_expected = filecmp.cmp(os.path.join(self.DATADIR, "render_two.html"),
                                       self.RENDER_FILE)
        assert html_as_expected

    # rendering with reference this one seems to be broken.
    # include this tests as change/regression detector
    @raises(subprocess.CalledProcessError)
    def test_render_reference(self):
        # render with reference
        cmdline = ["python"] + coverage_opts() + \
                  [self.BENCH, "render", self.REPORT1, "-r", self.REPORT2, "-o", self.RENDER_FILE]
        subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def test_render_two(self):
        # render two benchmark results with trend
        cmdline = ["python"] + coverage_opts() + \
                  [self.BENCH, "render", self.REPORT1, self.REPORT2, "-t", "-o", self.RENDER_FILE]
        rc = subprocess.check_call(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        eq_(rc, 0)
        html_as_expected = filecmp.cmp(os.path.join(self.DATADIR, "render_trend.html"),
                                       self.RENDER_FILE)
        assert html_as_expected


# Allow running this testfile directly
if __name__ == "__main__":
    unittest.main()
