# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2019 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""Helper module for initalizing the logger for the pkg.
"""

import logging
import os.path
from sys import stdout, stderr

from pyperf.ioservice import loadJSONData
from pyperf.exceptions import PyperfError


logLevel = {
    "NOTSET": 0,
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50
}


def init_logging(configFile="", debug=False):
    """
    This method initialises the logging for pyperf. It will setup the root logger and it's handlers according
    to a config file. When the logging can't be initialised an error will be raised.
    :param configFile: Path to a config file that determines how the logging shall work. Default is `pyperf/log/loggingConf.json`
    :param debug: Boolean variable that enables the `DEBUG` loglevel when true.
    :raises PyperfError
    :return: True when the logging could be initialised.
    """
    if not configFile:
        configFile = os.path.join(os.path.dirname(__file__), "loggingConf.json")

    try:
        config = loadJSONData(configFile)
    except PyperfError as e:
        e.message += "Please provide a valid logging configuration."
        raise

    rootLogger = logging.root
    if debug:
        rootLogger.setLevel(logging.DEBUG)
    else:
        rootLogger.setLevel(logging.INFO)

    for logging_source in config:
        for logging_destination in config[logging_source]:
            destination_dict = config[logging_source][logging_destination]
            try:
                min_ = logLevel[destination_dict["min"]]
            except KeyError:
                min_ = "DEBUG"
            try:
                max_ = logLevel[destination_dict["max"]]
            except KeyError:
                max_ = "CRITICAL"
            try:
                logfile = destination_dict["filename"]
            except KeyError:
                logfile = None

            maxFilter = _MaxLogLevel(max_)
            if logging_source == "third-party":
                sourceFilter = _ExcludeLoggername(["pyperf", "benchmark"])
            else:
                sourceFilter = _IncludeLoggername(logging_source)

            if logfile:
                handler = logging.FileHandler(logfile, "a")
                formatString = '%(asctime)s [%(levelname)s] [%(name)s]: %(message)s'
            else:
                if logging_destination == "stdout":
                    handler = logging.StreamHandler(stdout)
                elif logging_destination == "stderr":
                    handler = logging.StreamHandler(stderr)
                formatString = '%(message)s'

            if handler:
                formatter = logging.Formatter(fmt=formatString, datefmt='%m-%d %H:%M')
                handler.setLevel(min_)
                handler.addFilter(maxFilter)
                if sourceFilter:
                    handler.addFilter(sourceFilter)
                handler.setFormatter(formatter)
                rootLogger.addHandler(handler)

    logging.getLogger(__name__).info("Logging enabled using configuration file %s", configFile)


class _IncludeLoggername(logging.Filter):
    """
    This class is used for filtering logs.
    All logs, that come from a logger whose name contains `loggername`, will come through the filter.
    """
    def __init__(self, loggername):
        """
        Initialises the Filter.
        :param loggername: The string that shall be in the logger of the record.
        """
        super(_IncludeLoggername, self).__init__()
        self.loggername = loggername.lower()

    def filter(self, record):
        return self.loggername in record.name.lower()


class _ExcludeLoggername(logging.Filter):
    """
    This class is used for filtering logs.
    All logs, that come from a logger that contain any of the `loggernames` will not pass the filter.
    """
    def __init__(self, loggernames):
        """
        Initialises the Filter.
        :param loggernames: List of strings that the logger of a record may not have.
        """
        super(_ExcludeLoggername, self).__init__()
        self.loggernames = loggernames

    def filter(self, record):
        for loggername in self.loggernames:
            if loggername.lower() in record.name.lower():
                return False
        return True


class _MaxLogLevel(logging.Filter):
    """
    This class is used for filtering logs.
    All logs, that have a higher loglevel than `maxlevel` will not pass the filter.
    """
    def __init__(self, maxlevel):
        """
        Initialises the Filter.
        :param maxlevel: The highest loglevel that a record may have.
        """
        super(_MaxLogLevel, self).__init__()
        self.maxlevel = maxlevel

    def filter(self, record):
        return record.levelno <= self.maxlevel
