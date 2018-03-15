# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

import unittest
import os
from os.path import join

from ..benchrunner import Benchrunner
from nose.tools import eq_


class TestBenchrunner(unittest.TestCase):
    def setUp(self):
        pass

    def test_normalize_bench_path(self):
        def abspath(path):
            return join(os.path.abspath(os.sep), path)
        
        # positive cases:
        # - both absolute
        # - benchpath is relative, the suite is absolute
        # - benchpath is relative, the suite is also relative

        cwd = os.getcwd()
        cases = [
            # (<suitepath>,
            # <benchpath>,
            # <expected result>)
            
            ("suite.json",
             abspath("benchmark.py"),
             abspath("benchmark.py")),
            
            (abspath("suite.json"),
             abspath("benchmark.py"),
             abspath("benchmark.py")),
            
            (abspath("suite.json"),
             "benchmark.py",
             abspath("benchmark.py")),
            
            (abspath(join("folder", "suite.json")),
             "benchmark.py",
             abspath(join("folder", "benchmark.py"))),
            
            (abspath(join("folder", "suite.json")),
             join("subfolder", "benchmark.py"),
             abspath(join("folder", "subfolder", "benchmark.py"))),
            
            (join("folder", "suite.json"),
             join("subfolder", "benchmark.py"),
             join(cwd, "folder", "subfolder", "benchmark.py")),

            # one backstep case
            (abspath(join("folder", "..", "suite.json")),
             "benchmark.py",
             abspath("benchmark.py"))
        ]

        benchrunner = Benchrunner()
        for suitepath, benchpath, expected_result in cases:
            result = benchrunner.normalize_bench_path(suitepath, benchpath)
            eq_(result, expected_result)
