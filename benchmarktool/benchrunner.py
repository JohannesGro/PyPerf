#!demoLauncher.cmd
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/
"""
"""

import argparse
import getpass
import importlib
import logging.config
import multiprocessing
import os
import platform
import sys
import time

import ioservice
import systemInfos
from benchmarktool.log import customlogging


class Benchrunner(object):
    """The benchrunner runs different benchmarks. These benchmarks inherit from the
    abstract class 'Bench'. Several different benches can be collected and define by a
    benchsuite. A benchsuite describes a list of benches and their call parameter.
    The suite is stored in json format (Read more: :doc:`benchsuite`).
    The benchrunner reads the benchsuite and executes each bench. The benches return
    measurements which will be gathered and stored by the benchrunner. The result is
    stored in a json formatted outputfile.
    """

    # defaults
    suite_file = 'benchsuite.json'
    output_file = 'benchmarkResults_{}.json'.format(time.strftime("%Y-%m-%d_%H-%M-%S"))
    logging_file = 'benchrunner.log'
    results = {'results': {}}

    # CLI
    parser = argparse.ArgumentParser(description=__doc__, prog="Benchrunner")
    parser.add_argument("--suite", "-s", nargs='?', default=suite_file, help="A json file which contains the benches. (default: %(default)s)")
    parser.add_argument("--outfile", "-o", nargs='?', default=output_file, help="The results will be stored in this file. (default: %(default)s)")
    parser.add_argument("--logconfig", "-l", nargs='?', default=logging_file, help="Configuration file for the logger. (default: %(default)s)")

    def __init__(self, args):
        # Grab the self.args from argv
        if type(args) == argparse.Namespace:
            prev = sys.argv
            sys.argv = []
            self.args = self.parser.parse_args(args=None, namespace=args)
            sys.argv = prev
        else:
            self.args = self.parser.parse_args(args)

    def main(self):
        global logger
        logger = customlogging.init_logging("[Benchrunner]", configFile=self.args.logconfig, fileName=self.logging_file)
        self.sys_infos()
        logger.info("Starting")
        logger.debug("Options: " + str(self.args))
        logger.info("Reading the benchsuite: " + self.args.suite)
        data = ioservice.loadJSONData(self.args.suite)

        # iterating the suite
        for bench_key, bench_val in data["suite"].iteritems():
            logger.info("Execute bench: " + bench_key)
            result = self.start_bench_script(bench_val["file"], bench_val["className"], bench_val["args"])
            self.results['results'][bench_key] = {'args': bench_val["args"], 'data': result}
        ioservice.saveJSONData(self.args.outfile, self.results)

    def start_bench_script(self, path, class_name, args):
        """This functions imports the bench module and creates an instance of the given
        class_name. It calls the method run(args) which is the entry point for
        the test classes. Returns the result of the bench.

        :param path: path to the module of the benchmark
        :param class_name: name of the benchmark
        :param args: serveral arguments for the benchmark
        :returns: the dict with measurements of the benchmark.
        """
        prevSysPath = sys.path
        try:
            dirPath = os.path.dirname(path)
            fileName = os.path.basename(path)
            module, extension = os.path.splitext(fileName)
            if (not extension == '' and not extension == '.py') or module == '':
                raise ValueError("The bench file '{}' is not specified correctly.".format(fileName))
            sys.path.append(dirPath)
            mod = __import__(module, fromlist=[class_name])
            bench_class = getattr(mod, class_name)
        except ImportError as err:
            logger.error("Could not import bench file! {}".format(str(err)))
            return
        except AttributeError as err:
            logger.error("Could not find className: {0}! {1}".format(class_name, str(err)))
            return
        except ValueError as err:
            logger.error(str(err))
            return
        except:
            logger.error("Unexpected error occurred! " + str(sys.exc_info()[0:1]))
            return
        finally:
            sys.path = prevSysPath

        # perform the benchmark
        return bench_class().run(args)

    def sys_infos(self):
        """Detect serveral system infos. This infos will be saved later with the
        results of the benchmarks.
        """
        self.results['Sysinfos'] = systemInfos.getAllSysInfos()
