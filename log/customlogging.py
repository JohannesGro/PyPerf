# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""Helper module for initalizing the logger for the pkg.
"""

import ioservice
import logging


def init_logging(logger_name, config=""):
    """Initialize the logger. The name of the config file is determined by parameter.
    The default config file is 'loggingConf.json'.
    """
    # removing the root handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # initialize the logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    if not config == "":
        # try to read config
        config = ioservice.loadJSONData(config)
        logging.config.dictConfig(config)

    logger = logging.getLogger(logger_name)
    return logger
