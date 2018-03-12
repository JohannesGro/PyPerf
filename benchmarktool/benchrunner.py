#!demoLauncher.cmd
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/
"""
"""

import os
import sys

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

    logging_file = 'benchrunner.log'
    results = {'results': {}}

    def main(self, suite, outfile, logconfig):
        global logger
        logger = customlogging.init_logging("[Benchrunner]", configFile=logconfig, fileName=self.logging_file)
        self.sys_infos()
        logger.info("Starting")
        logger.info("Reading the benchsuite: " + suite)
        data = ioservice.loadJSONData(suite)

        # iterating the suite
        for bench_key, bench_val in data["suite"].iteritems():
            logger.info("Execute bench: " + bench_key)
            result = self.start_bench_script(bench_val["file"], bench_val["className"], bench_val["args"])
            self.results['results'][bench_key] = {'args': bench_val["args"], 'data': result}
        ioservice.saveJSONData(outfile, self.results)

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
            logger.exception("Could not import bench file! {}".format(str(err)))
            return
        except AttributeError as err:
            logger.exception("Could not find className: {0}! {1}".format(class_name, str(err)))
            return
        except ValueError as err:
            logger.exception(str(err))
            return
        except:
            logger.exception("Unexpected error occurred! " + str(sys.exc_info()[0:1]))
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
