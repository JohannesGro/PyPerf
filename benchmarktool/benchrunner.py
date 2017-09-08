#!launcher.cmd
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/


"""The benchrunner runs different benchmarks. These benchmarks inherit from the
abstract class 'Bench'. Several different benches can be collected and define by a
benchsuite. A benchsuite describes a list of benches and their call parameter.
The suite is stored in json format (Read more: :doc:`benchsuite`).
The benchrunner reads the benchsuite and executes each bench. The benches return
measurements which will be gathered and stored by the benchrunner. The result is
stored in a json formatted outputfile.
"""

import argparse
import getpass
import importlib

import logging.config
import multiprocessing
import platform
import sys

from cdb import rte, version
import ioservice
from log import customlogging
import systemInfos

# TODO
__revision__ = "$Id: benchrunner.py ? 2017-08-21 10:23:29Z ? $"

# workaround for realtiv path
sys.path.append('..')

# defaults
suite_file = 'benchsuite.json'
output_file = 'benchmarkResults.json'
logging_file = 'log/benchrunner.log'
results = {'results': {}}


def main():
    global logger
    logger = customlogging.init_logging("[Benchrunner]", configFile=opts.logconfig, fileName=logging_file)
    sys_infos()
    logger.info("Starting")
    logger.debug("Options: " + str(opts))
    logger.info("Reading the benchsuite: " + opts.suite)
    data = ioservice.loadJSONData(opts.suite)

    # iterating the suite
    for bench_key, bench_val in data["suite"].iteritems():
        if "active" in bench_val and (bench_val["active"] is False):
            continue
        logger.info("Execute bench: " + bench_key)
        result = start_bench_script(bench_val["file"], bench_val["className"], bench_val["args"])
        results['results'][bench_key] = {'args': bench_val["args"], 'data': result}
    ioservice.saveJSONData(opts.outfile, results)


def start_bench_script(path, class_name, args):
    """This functions imports the bench module and creates an instance of the given
    class_name. It calls the method run(args) which is the entry point for
    the test classes. Returns the result of the bench.

    :param path: path to the module of the benchmark
    :param class_name: name of the benchmark
    :param args: serveral arguments for the benchmark
    :returns: the dict with measurements of the benchmark.
    """
    try:
        mod = __import__(path, fromlist=[class_name])
        bench_class = getattr(mod, class_name)
    except ImportError as err:
        logger.error("Could not import bench file! " + str(err))
        return
    except AttributeError as err:
        logger.error("Could not find className: {0}! {1}".format(class_name, str(err)))
        return
    except:
        logger.error("Unexpected error occurred! " + str(sys.exc_info()[0:1]))
        return

    # perform the benchmark
    return bench_class().run(args)





def sys_infos():
    """Detect serveral system infos. This infos will be saved later with the
    results of the benchmarks.
    """
    results['Sysinfos'] = systemInfos.getAllSysInfos()
    logger.info("Script Version: %s", __revision__)
    results['Sysinfos']['Script Version'] = __revision__


if __name__ == "__main__":
    # CLI
    parser = argparse.ArgumentParser(description="""The benchrunner reads a list of benches from a benchsuite.
                                    Each bench will be called with an argument list. The result will
                                    be written into output file. The file is json formatted.""")
    parser.add_argument("--suite", "-s", nargs='?', default=suite_file, help="A json file which contains the benches. (default: %(default)s)")
    parser.add_argument("--outfile", "-o", nargs='?', default=output_file, help="The results will be stored in this file. (default: %(default)s)")
    parser.add_argument("--logconfig", "-l", nargs='?', default="", help="Configuration file for the logger. (default: %(default)s)")

    # Grab the opts from argv
    opts = parser.parse_args()

    main()
