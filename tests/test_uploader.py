#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""
Test Module pytest

This is the documentation for the tests.
"""

__docformat__ = "restructuredtext en"
__revision__ = "$Id$"

import unittest
import subprocess
import os
import json
from nose.tools import eq_

class UploaderTest(unittest.TestCase):
    def setUp(self):
        self.here = os.path.abspath(os.path.dirname(__file__))
        self.orig_cwd = os.getcwd()

    def tearDown(self):
        if self.orig_cwd != os.getcwd():
            os.chdir(self.orig_cwd)

    def test_happy_case(self):
        # assumes a running influx on localhost
        # and an 'sdperf' database inside of it
        # TODO: assume less or automate the setup
        here = os.path.abspath(os.path.dirname(__file__))
        os.chdir(here)
        rc = subprocess.check_call([
            "python", os.path.join(here, "..", "bench.py"), "upload",
            os.path.join(here, "report.json"),
            "--influxdburl=http://localhost:8086", "--database=sdperf"
        ], stdout=subprocess.PIPE)
        eq_(rc, 0)


# Allow running this testfile directly
if __name__ == "__main__":
    unittest.main()
