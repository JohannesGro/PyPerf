# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

import os
import sys
import logging

from . import ioservice
from . import systemInfos
from pyperf.log import customlogging
from pyperf.exceptions import PyperfError

logger = logging.getLogger(__name__)


class Benchrunner(object):
    """The benchrunner runs different benchmarks. These benchmarks inherit from the
    abstract class 'Bench'. Several different benches can be collected and defined by a
    benchsuite. A benchsuite describes a list of benches and their call parameters.
    The suite is stored in json format (Read more: :ref:`howto_benchsuite`).
    The benchrunner reads the benchsuite and executes each bench. The benches return
    measurements which will be gathered and stored by the benchrunner as
    a json formatted output file.
    """

    results = {'results': {}}

    def main(self, suite, outfile, logconfig="", verbose=False, debug=False):
        """
        This method is the entry point for the pyperf run subcommand, but may be called by
        importing this module too.

        :param suite: the path to the benchsuite to load
        :param outfile: the path to the file to write the report to
        :param logconfig: the config file for the logging, see :ref:`howto_logging`
        :param verbose: whether the collected system info shall be verbose or not
        :param debug: whether DEBUG logging shall be enabled or not
        :return: 0 on success, 1 otherwise
        """
        try:
            customlogging.init_logging(logconfig, debug)
        except PyperfError as e:
            raise
        self.sys_infos(verbose)
        logger.info("Starting")
        logger.info("Reading the benchsuite '%s'", suite)
        try:
            data = ioservice.loadJSONData(suite)
        except PyperfError as e:
            logger.error("The Testsuite '%s' could not be loaded. %s" % (suite, e.message))
        else:
            # iterating the suite
            rc_all = True
            for bench_key, bench_val in data["suite"].items():
                if bench_val.get("active", True) is False:
                    logger.info("Bench '%s' is inactive, skipping", bench_key)
                    continue

                logger.info("Executing bench '%s'", bench_key)
                rc, results = self.start_bench_script(suite, bench_val["file"],
                                                      bench_val["className"], bench_val["args"])
                rc_all &= rc
                self.results['results'][bench_key] = {'args': bench_val["args"], 'data': results}
            if ioservice.saveJSONData(self.results, outfile):
                logger.info("Results saved to %s", outfile)
            return int(not rc_all)

    def start_bench_script(self, suitepath, benchpath, class_name, args):
        """This function imports the bench module and creates an instance of the given
        class_name. It calls the method run(args) which is the entry point for
        the test classes. Returns the result of the bench.

        :param path: path to the module of the benchmark
        :param class_name: name of the benchmark
        :param args: serveral arguments for the benchmark
        :returns: the dict with measurements of the benchmark.
        """
        prevSysPath = sys.path
        try:
            benchpath = self.normalize_bench_path(suitepath, benchpath)
            dirPath = os.path.dirname(benchpath)
            fileName = os.path.basename(benchpath)
            module, extension = os.path.splitext(fileName)
            if (extension != '' and extension != '.py') or module == '':
                raise ValueError("The bench file '{}' is not specified correctly.".format(fileName))
            sys.path.append(dirPath)
            mod = __import__(module, fromlist=[class_name])
            bench_class = getattr(mod, class_name)
        except ImportError as err:
            logger.exception("Could not import bench file! {}".format(str(err)))
            raise
        except AttributeError as err:
            logger.exception("Could not find className: {0}! {1}".format(class_name, str(err)))
            raise
        except ValueError as err:
            logger.exception(str(err))
            raise
        except:
            logger.exception("Unexpected error occurred! %s", sys.exc_info()[0:1])
            raise
        finally:
            sys.path = prevSysPath

        # perform the benchmark
        return bench_class().run(args)

    def sys_infos(self, verbose):
        """Detect several system information. These information will be saved later
        with the results of the benchmarks.
        """
        self.results['Sysinfos'] = systemInfos.getAllSysInfos(verbose)

    def normalize_bench_path(self, suitepath, benchpath):
        """
        Normalizes the path to the benchmark, given an absolute or
        relative path to the suite and an absolute or relative path to
        the benchmark

        :param suitepath: path to the benchsuite file
        :param benchpath: path to the benchmark file
        :returns: normalized absolute path to the benchmark file
        """
        path = None
        if os.path.isabs(benchpath):
            path = benchpath
        elif os.path.isabs(suitepath):
            path = os.path.join(os.path.dirname(suitepath), benchpath)
        else:
            path = os.path.join(os.getcwd(), os.path.dirname(suitepath), benchpath)

        return os.path.normpath(path)
