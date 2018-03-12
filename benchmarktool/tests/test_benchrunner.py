# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

import unittest
import os

from ..benchrunner import Benchrunner
from nose.tools import eq_


class TestBenchrunner(unittest.TestCase):
    def setUp(self):
        pass

    def test_normalize_bench_path(self):
        # positive cases:
        # - both absolute
        # - benchpath is relative, the suite is absolute
        # - benchpath is relative, the suite is also relative

        cwd = os.getcwd()
        cases = [
            # <suitepath>, <benchpath>, <expected result>
            ("suite.json", "/benchmark.py", "/benchmark.py"),
            ("/suite.json", "/benchmark.py", "/benchmark.py"),
            ("/suite.json", "benchmark.py", "/benchmark.py"),
            ("/folder/suite.json", "benchmark.py", "/folder/benchmark.py"),
            ("/folder/suite.json", "subfolder/benchmark.py", "/folder/subfolder/benchmark.py"),
            ("folder/suite.json", "subfolder/benchmark.py",
             os.path.join(cwd, "folder/subfolder/benchmark.py")),

            # one backstep case
            ("/folder/../suite.json", "benchmark.py", "/benchmark.py")
        ]

        benchrunner = Benchrunner()
        for suitepath, benchpath, expected_result in cases:
            result = benchrunner.normalize_bench_path(suitepath, benchpath)
            eq_(result, expected_result)
