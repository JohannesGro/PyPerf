#!c:\ce\trunk\win32\debug\img\python.exe
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/


import unittest
import mock
import types
from nose.tools import eq_
from pyperf.bench import Bench


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

    def tearDown(self):
        self.t.__class__.results = {}

    def test_exec_order(self):
        expected = ["setUpClass", "setUp", "bench_A", "tearDown", "setUp",
                    "bench_B", "help", "tearDown", "setUp", "bench_C",
                    "tearDown", "tearDownClass"]
        self.t.run({})
        eq_(self.t.testString, expected)

    def test_storeResult1(self):
        # {self.namespace + name: {"value": val, "unit": unit, "type": type}}
        val = [1, 2, 3]
        expected = {"test_storeResult1": {"value": val, "unit": "hour", "type": "time_series"}}
        self.t.storeResult(val, name="", type="time_series", unit="hour")
        eq_(self.t.results, expected)

    def test_storeResult2(self):
        # {self.namespace + name: {"value": val, "unit": unit, "type": type}}
        val = [1, 2, 3]
        expected = {"test_storeResult2": {"value": val, "unit": "seconds", "type": "time_series"}}
        self.t.storeResult(val, name="", type="time_series", unit="seconds")
        eq_(self.t.results, expected)

    def test_storeResult3(self):
        # {self.namespace + name: {"value": val, "unit": unit, "type": type}}
        val = 1
        expected = {"test_storeResult3": {"value": val, "unit": "seconds", "type": "time"}}
        self.t.storeResult(val)
        eq_(self.t.results, expected)

    def test_storeResult4(self):
        # {self.namespace + name: {"value": val, "unit": unit, "type": type}}
        self.t.namespace = "prefix_"
        val = [1, 2, 3]
        expected = {"prefix_test_storeResult4": {"value": val, "unit": "seconds", "type": "time"}}
        self.t.storeResult(val)
        eq_(self.t.results, expected)

    def test_discard(self):
        # {self.namespace + name: {"value": val, "unit": unit, "type": type}}
        val = [1, 2, 3]
        expected = {}
        self.t.storeResult(val, name="", type="time_series", unit="seconds")
        self.assertTrue(expected.items() <= self.t.results.items())
        self.t.discard("test_")
        eq_(self.t.results, expected)


class Test_ErrorHandling(unittest.TestCase):
    class TestBench(Bench):
        def bench_1(self):
            self.storeResult(1)

        def bench_2(self):
            self.storeResult(2)

    hooks = ["setUp", "tearDown"]
    cls_hooks = ["setUpClass", "tearDownClass"]
    all_hooks = hooks + cls_hooks
    complete_results = {
            'bench_1': {'type': 'time', 'unit': 'seconds', 'value': 1},
            'bench_2': {'type': 'time', 'unit': 'seconds', 'value': 2}
        }

    def assert_hooks_called(self, bench):
        bench.setUpClass.assert_called_once()
        bench.tearDownClass.assert_called_once()
        eq_(bench.setUp.call_count, 2)
        eq_(bench.tearDown.call_count, 2)

    def bench_bare(self):
        return self._bench([])

    def bench_cls_hooks(self):
        return self._bench(self.cls_hooks)

    def bench_all_hooks(self):
        return self._bench(self.all_hooks)

    def results_contain(self, results, benchname, exp_result):
        return benchname in results and (results[benchname]["value"] == exp_result)

    def results_complete(self, results):
        return results == self.complete_results

    def _bench(self, methods):
        mocked_bench = self.TestBench()
        for method in methods:
            setattr(mocked_bench, method, types.MethodType(mock.Mock(), method))
        return mocked_bench

    def setUp(self):
        self.bench = self.bench_all_hooks()
        self.throwing_mock = mock.Mock(side_effect=Exception('foo'))

    def test_happy_case(self):
        # * Everything is executed
        # * Results are complete
        # * No error is reported

        rc, results = self.bench.run(None)

        assert self.results_complete(results)
        self.assert_hooks_called(self.bench)
        eq_(rc, True)

        # incomplete benches do at least not throw...
        for bench_mock in [self.bench_bare(), self.bench_cls_hooks()]:
            rc, results = bench_mock.run(None)
            assert results is not None
            eq_(rc, True)

    def test_classsetup_failure(self):
        # * classSetUp and classTearDown are executed
        # * No bench method is executed
        # * No bench hooks are executed
        # * There are no results
        # * An error is reported

        self.bench.setUpClass = types.MethodType(self.throwing_mock, self.bench)

        rc, results = self.bench.run(None)

        eq_(results, {})
        eq_(rc, False)
        self.bench.setUpClass.assert_called_once()
        self.bench.tearDownClass.assert_called_once()
        self.bench.setUp.assert_not_called()
        self.bench.tearDown.assert_not_called()

    def test_classteardown_failure(self):
        # * Everything is executed
        # * Results are complete
        # * An error is reported

        self.bench.tearDownClass = types.MethodType(self.throwing_mock, self.bench)

        rc, results = self.bench.run(None)
        assert self.results_complete(results)
        self.assert_hooks_called(self.bench)
        eq_(rc, False)

    def test_setup_failure(self):
        # * The bench method, whose setup failed, is NOT executed
        # * Everything else is
        # * Results are complete except of those of the failing method
        # * An error is reported

        self.bench.setUp = types.MethodType(self.throwing_mock, self.bench)

        rc, results = self.bench.run(None)

        eq_(results, {})
        eq_(rc, False)
        self.assert_hooks_called(self.bench)

    def test_teardown_failure(self):
        # * Everything is executed
        # * Results are complete
        # * An error is reported

        self.bench.tearDown = types.MethodType(self.throwing_mock, self.bench)

        rc, results = self.bench.run(None)
        assert self.results_complete(results)
        self.assert_hooks_called(self.bench)
        eq_(rc, False)

    def test_bench_failure(self):
        # * Everything is executed
        # * Results are complete except of those of the failing bench
        # * An error is reported

        self.bench.bench_1 = types.MethodType(self.throwing_mock, self.bench)

        rc, results = self.bench.run(None)

        self.bench.bench_1.assert_called_once()
        assert not self.results_contain(results, "bench_1", 1)
        assert self.results_contain(results, "bench_2", 2)
        self.assert_hooks_called(self.bench)
        eq_(rc, False)


if __name__ == '__main__':
    unittest.main()
