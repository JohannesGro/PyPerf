# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2019 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

import unittest
import logging
import os
from pyperf import ioservice
from nose.tools import eq_
from shutil import rmtree
from pyperf.exceptions import PyperfError

logger = logging.getLogger("Foo")


class Testioservice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.json_data = {
            "suite": {
                "DummyBenchmark": {
                    "file": "DummyBenchmark.py",
                    "className": "DummyBenchmark",
                    "args": {}
                }
            }
        }
        cls.tmpdir = os.path.join(os.getcwd(), "tests", "tmpdir")
        try:
            os.mkdir(cls.tmpdir)
        except Exception:
            rmtree(cls.tmpdir)
            os.mkdir(cls.tmpdir)

    @classmethod
    def tearDownClass(cls):
        rmtree(cls.tmpdir)

    def test_loadJSONData_valid(self):
        filePath = os.path.join(os.getcwd(), "tests", "testdata", "dummy.json")
        method_result = ioservice.loadJSONData(filePath)
        eq_(method_result, self.json_data)

    def test_loadJSONData_invalid(self):
        filePath = os.path.join(os.getcwd(), "tests", "testdata", "plain_textfile.txt")
        self.assertRaises(PyperfError, ioservice.loadJSONData, filePath)

    def test_loadJSONData_no_file(self):
        filePath = os.path.join(os.getcwd(), "tests", "testdata", "not_existing_jsonfile.json")
        self.assertRaises(PyperfError, ioservice.loadJSONData, filePath)

    def test_saveJSONData(self):
        filePath = os.path.join(os.getcwd(), "tests", "tmpdir", "not_yet_existing_jsonfile.json")
        result = ioservice.saveJSONData(self.json_data, filePath)
        self.assertTrue(result)

    def test_saveJSONData_could_not_open_file(self):
        filePath = os.path.join(os.getcwd(), "tests", "tmpdir")
        self.assertRaises(PyperfError, ioservice.saveJSONData, self.json_data, filePath)

    def test_saveJSONData_no_serialisation(self):
        class Testclass(object):
            def __init__(self):
                self.content = "no json!"

        noJSON = Testclass
        filePath = os.path.join(os.getcwd(), "tests", "tmpdir", "foobar.json")
        self.assertRaises(PyperfError, ioservice.saveJSONData, noJSON, filePath)

    def test_readFile(self):
        filePath = os.path.join(os.getcwd(), "tests", "testdata", "plain_textfile.txt")
        data = ioservice.readFile(filePath)
        eq_(data, "This is a test.")

    def test_readFile_that_does_not_exist(self):
        filePath = os.path.join(os.getcwd(), "tests", "testdata", "not_existing_textfile.txt")
        self.assertRaises(PyperfError, ioservice.readFile, filePath)

    def test_writeToFile(self):
        filePath = os.path.join(os.getcwd(), "tests", "tmpdir", "not_yet_existing_textfile.txt")
        testString = "Das ist ein Test."
        result = ioservice.writeToFile("Das ist ein Test.", filePath)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(filePath))
        self.assertEqual(testString, ioservice.readFile(filePath))
