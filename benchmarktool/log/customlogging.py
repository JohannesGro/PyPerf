# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""Helper module for initalizing the logger for the pkg.
"""

from .. import ioservice
import logging
import sys


def init_logging(logger_name, configFile="", fileName=""):
    """Initialize the logger. The name of the config file is determined by parameter.
    The default config file is 'loggingConf.json'.
    """
    # removing the root handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    if fileName == "":
        fileName = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    # initialize the logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=fileName)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    ch.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(ch)

    if not configFile == "":
        # try to read configFile
        config = ioservice.loadJSONData(configFile)
        logging.config.dictConfig(config)

    logger = logging.getLogger(logger_name)
    return logger
