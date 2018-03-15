#!c:\ce\trunk\win32\debug\img\python.exe
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/


import unittest

from benchmarktool.bench import Bench


class test_class(Bench):

    testString = []

    def setUp(self):
        self.testString.append("setUp")

    def tearDown(self):
        self.testString.append("tearDown")

    def setUpClass(self):
        self.testString.append("setUpClass")

    def tearDownClass(self):
        self.testString.append("tearDownClass")

    def bench_A(self):
        self.testString.append("bench_A")

    def bench_B(self):
        self.testString.append("bench_B")
        self.help()

    def bench_C(self):
        self.testString.append("bench_C")

    def help(self):
        self.testString.append("help")


class TestBenchMethods(unittest.TestCase):

    def setUp(self):
        self.t = test_class()

    def test_exec_order(self):
        expected = ["setUpClass", "setUp", "bench_A", "tearDown", "setUp", "bench_B", "help", "tearDown", "setUp", "bench_C", "tearDown", "tearDownClass"]
        self.t.run({})
        self.assertEqual(len(self.t.testString), len(expected))
        self.assertEqual(self.t.testString, expected)

    def test_storeResult1(self):
        # {self.namespace + name: {"value": val, "unit": unit, "type": type}}
        val = [1, 2, 3]
        expected = {"test_storeResult1": {"value": val, "unit": "hour", "type": "time_series"}}
        self.t.storeResult(val, name="", type="time_series", unit="hour")
        self.assertTrue(expected.viewitems() <= self.t.results.viewitems())

    def test_storeResult2(self):
        # {self.namespace + name: {"value": val, "unit": unit, "type": type}}
        val = [1, 2, 3]
        expected = {"test_storeResult2": {"value": val, "unit": "seconds", "type": "time_series"}}
        self.t.storeResult(val, name="", type="time_series", unit="seconds")
        self.assertTrue(expected.viewitems() <= self.t.results.viewitems())

    def test_storeResult3(self):
        # {self.namespace + name: {"value": val, "unit": unit, "type": type}}
        val = 1
        expected = {"test_storeResult3": {"value": val, "unit": "seconds", "type": "time"}}
        self.t.storeResult(val)
        self.assertTrue(expected.viewitems() <= self.t.results.viewitems())

    def test_storeResult4(self):
        # {self.namespace + name: {"value": val, "unit": unit, "type": type}}
        self.t.namespace = "prefix_"
        val = [1, 2, 3]
        expected = {"prefix_test_storeResult4": {"value": val, "unit": "seconds", "type": "time"}}
        self.t.storeResult(val)
        self.assertTrue(expected.viewitems() <= self.t.results.viewitems())

    def test_discard(self):
        # {self.namespace + name: {"value": val, "unit": unit, "type": type}}
        val = [1, 2, 3]
        expected = {"test_discard": {"value": val, "unit": "seconds", "type": "time_series"}}
        self.t.storeResult(val, name="", type="time_series", unit="seconds")
        self.assertTrue(expected.viewitems() <= self.t.results.viewitems())
        self.t.discard("test_")
        self.assertFalse(expected.viewitems() <= self.t.results.viewitems())


if __name__ == '__main__':
    unittest.main()
