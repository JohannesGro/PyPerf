# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

import unittest
import os
import mock
from os.path import join

from pyperf.benchrunner import Benchrunner
from nose.tools import eq_

HERE = os.path.abspath(os.path.dirname(__file__))


class TestBenchrunner(unittest.TestCase):
    outfile = "dummy_outfile.json"

    def setUp(self):
        self.benchrunner = Benchrunner()

    def tearDown(self):
        if os.path.exists(self.outfile):
            os.remove(self.outfile)

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

        for suitepath, benchpath, expected_result in cases:
            result = self.benchrunner.normalize_bench_path(suitepath, benchpath)
            eq_(result, expected_result)

    def test_skipping_inactive_benches(self):
        suite = os.path.join(HERE, "testdata", "suite_inactive.json")
        method_mock = mock.MagicMock(return_value={})
        self.benchrunner.start_bench_script = method_mock

        self.benchrunner.main(suite, self.outfile, "", False)

        method_mock.assert_not_called()

    def test_bench_is_active_by_default(self):
        suite = os.path.join(HERE, "testdata", "suite_without_active_property.json")
        method_mock = mock.MagicMock(return_value=(True, {}))
        self.benchrunner.start_bench_script = method_mock

        self.benchrunner.main(suite, self.outfile, "", False)

        method_mock.assert_called()
