#!C:\ce\trunk\win32\release\img\python
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

import inspect
import logging
from abc import ABCMeta

logger = logging.getLogger("[" + __name__ + " - Bench]")


class Bench(object):
    """'Bench' is an abstract class which has to be used for creating benchmarks.
    """
    __metaclass__ = ABCMeta
    args = {}
    """This dict contains the arguments for the benchmark. The arguments are set
    in a benchsuite, read by the benchrunner and passed by the run method. """

    results = {}
    """This dict contains the result of the benchmark. A entry can be added by calling
    the storeResult method. The run method returns the result."""

    namespace = ""
    """The namespace is important for storing the result of the test. Whenever a
    result is stored by the storeResult method, the namespace attribute will used
    as prefix (default = \"\"). E.g. two methods calling a third method which stores
    measurements. The data would be stored under the name of the third method.
    In order to distinguish the calls the namespace attribute was introduced."""

    def setUp(self):
        """Method called to prepare the test fixture. The default implementation does nothing.
        This is called immediately before calling the test method;
        """
        pass

    def tearDown(self):
        """Method called immediately after the test method has been called.
        Usually this method is used for cleaning purposes. The default implementation
        does nothing.
        """
        pass

    def setUpClass(self):
        """This method is called exactly once before the first test and is used for preparing all test.
        If an exception is raised during a setUpClass then the tests in the class
        are not run and the tearDownClass is not run.
        """
        pass

    def tearDownClass(self):
        """This method is called after the last test and is used for cleaning purposes.
        """
        pass

    def storeResult(self, val, name="", type="time", unit="seconds"):
        """Store the benchmark result. The run-Method call will return all stored results.
        Note that the global variable 'namespace' is used as a prefix for the name.
        If a method is called several times from different test, a namespace is
        used to distinguish the entries. Entries with the same name will be updated.

        :param val: measurments; the val can be a collection or a single value.
        :param name: the name of the entry for this data. If name is empty or not
            specified, the name of calling method (parent frame) will be used.
        :param type: type of measurments. this is important for further processing of
            the data.
        :param unit: the unit of the values.
        """
        if name == "":
            curframe = inspect.currentframe()
            calframe = inspect.getouterframes(curframe, 2)
            name = calframe[1][3]
        # overrides if the entry already exist
        self.results.update({self.namespace + name: {"value": val, "unit": unit, "type": type}})

    def discard(self, prefix):
        """Discard results with the given prefix.

        :param prefix: prefix or complete name of the entry
        """
        remove = []
        for key in self.results:
            if key.startswith(prefix):
                remove.append(key)
        for ele in remove:
            self.results.pop(ele, None)

    def run(self, args):
        """This method calls every test in this class. Test are indentified by the prefix "bench\_".
        The setUp-method is called immediately before each test and the tearDown-method is
        called immediately after each test. The result stored by 'storeResult'
        is structured in json format and will be returned.

        :param args: a dictionary consisting of all parameter which are used in this benchmark.
            E.g. iterations could be used for the repitition of an insert query.
        :returns: a dict with the result of the benchmark.
        """
        # pylint: disable=broad-except, too-many-nested-blocks
        self.args = args
        self.results = {}
        rc = True
        try:
            self.setUpClass()
            for test in dir(self):
                if test.find('bench_') == 0:
                    try:
                        self.setUp()
                        getattr(self, test)()
                    except Exception:
                        rc = False
                        logger.exception("Exception while running '%s'",
                                         self.__class__.__name__)
                    finally:
                        try:
                            self.tearDown()
                        except Exception:
                            rc = False
                            logger.exception("Exception while running tearDown of '%s'",
                                             self.__class__.__name__)
        except Exception:
            rc = False
            logger.exception("Exception while running '%s'",
                             self.__class__.__name__)
        finally:
            try:
                self.tearDownClass()
            except Exception:
                rc = False
                logger.exception("Exception while running tearDownClass of '%s'",
                                 self.__class__.__name__)

        return rc, self.results
