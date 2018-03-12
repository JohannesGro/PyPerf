#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

import unittest
import subprocess
import os
from nose.tools import eq_, raises
from .utils import coverage_opts

"""
Contains basic CLI tests for the 'render' subcommand
"""

__docformat__ = "restructuredtext en"
__revision__ = "$Id$"


class RendererTest(unittest.TestCase):
    # FIXME: currently it blows up with an encoding under Linux.
    #        TST should have a fix for that.
    @raises(subprocess.CalledProcessError)
    def test_render(self):
        # Pretty basic: render just one report, everything default
        here = os.path.abspath(os.path.dirname(__file__))
        bench = os.path.normpath(os.path.join(here, "..", "bench.py"))
        cmdline = ["python"] + coverage_opts() + \
                  [bench, "render", os.path.join(here, "report.json")]
        rc = subprocess.check_call(cmdline, stdout=subprocess.PIPE)
        eq_(rc, 0)


# Allow running this testfile directly
if __name__ == "__main__":
    unittest.main()
