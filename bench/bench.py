#!C:\ce\trunk\win32\release\img\python
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/
from abc import ABCMeta
import inspect
import logging

logger = logging.getLogger("[" + __name__ + " - Bench]")


class Bench(object):
    _metaclass_ = ABCMeta
    args = {}
    results = []
    namespace = ""

    def setUp(self):
        """Method called to prepare the test fixture. The default implementation does nothing.
        """
        pass

    def tearDown(self):
        """Method called immediately after the test method has been called and
        the result recorded.  The default implementation does nothing.
        """
        pass

    def setUpClass(self):
        """This method is called before the first test and is used for preparing all test.
        """
        pass

    def tearDownClass(self):
        """
        This method is called after the last test and is used for cleaning purposes.
        """
        pass

    def storeResult(self, val, name="", type="time", unit="seconds"):
        """Store the benchmark result. The run-Method call will be return all stored results.

        Keyword arguments:
        res -- a dictionary with a format spezified in the field res['type']
        """
        if name == "":
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            name = calframe[1][3]
        # overrides if the entry already exist
        self.results.update({self.namespace + name: {"value": val, "unit": unit, "type": type}})

    def run(self, args):
        """
        This method calls every test in this class. Test are indentified by the prefix 'test_'.
        The setUp-method is called immediately before each test and the tearDown-method is
        called immediately after each test. The result of benchmark is structured in json format and will be returned.

        Keyword arguments:
        args -- a dictionary consisting of all parameter which are used in this benchmark. E.g. iterations could be used for the repitition of an insert query.
        """
        self.args = args
        self.results = {}
        try:
            self.setUpClass()
            try:
                for test, val in sorted(self.__class__.__dict__.iteritems()):
                    if test.find('bench_') == 0:
                        test_method = getattr(self, test)
                        self.setUp()
                        test_method()
                        self.tearDown()
            except Exception:
                logger.exception("Exception while running Bench")
            finally:
                self.tearDownClass()
        except Exception:
            logger.exception("Exception while running Bench")
        return self.results
