#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

import unittest
import subprocess
import os
from nose.tools import eq_
from .utils import coverage_opts

"""
Contains basic CLI tests for the 'upload' subcommand
"""

__docformat__ = "restructuredtext en"
__revision__ = "$Id$"


class UploaderTest(unittest.TestCase):
    def test_basic_upload(self):
        # assumes a running influx on localhost
        # and an 'sdperf' database inside of it
        # TODO: assume less or automate the setup
        here = os.path.abspath(os.path.dirname(__file__))
        bench = os.path.normpath(os.path.join(here, "..", "bench.py"))
        rc = subprocess.check_call(["python"] + coverage_opts() + [
            bench, "upload", "--filename=%s" % os.path.join(here, "report.json"),
            "--influxdburl=http://con-wen.contact.de:8086", "--database=sdperf"
        ], stdout=subprocess.PIPE)
        eq_(rc, 0)


# Allow running this testfile directly
if __name__ == "__main__":
    unittest.main()
