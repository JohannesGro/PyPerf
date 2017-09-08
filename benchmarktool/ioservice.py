#!demoLauncher.cmd
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""This module is used for i/o operations.
"""

import json
import logging
import sys


logger = logging.getLogger("[" + __name__ + " - I/O Service]")


def loadJSONData(json_file):
    """This functions load the json-data and returns it.

    :param json_file: the file in json format
    :returns: json object
    """
    try:
        with open(json_file) as data_file:
            data = json.load(data_file)
    except IOError as err:
        logger.error("Could not open json file! " + str(err))
        sys.exit(1)
    except ValueError as err:  # JSONDecodeError inherrits from ValueError
        logger.error("Could not decode json file! " + str(err))
        sys.exit(1)
    except:
        logger.error("Unexpected error occurred! " + str(sys.exc_info()[0:1]))
        sys.exit(1)
    else:
        logger.info("Reading json file successful")
    return data


def saveJSONData(fileName, data):
    """This functions dumps json data into a file. The name of the output file
    is determined by parameter. The default output file is 'benchmarkResults.json'.

    :param data: json data which will be saved to file
    """
    logger.info("Saving json to file: " + fileName)
    try:
        with open(fileName, 'w') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=4)
    except IOError as err:
        logger.error("Could not open file to save the data! " + str(err))
    except ValueError as err:  # JSONDecodeError inherrits from ValueError
        logger.error("Could not decode values! " + str(err))
    except TypeError as err:
        logger.error("Could not serialize object! " + str(err))
    except:
        logger.error("Unexpected error occurred! " + str(sys.exc_info()[0:1]))
    else:
        logger.info("Saving successful")


def readFile(fileName):
    """Reads a file and return the content

    :param fileName: name of the file
    :returns: content of the file as string
    """
    with open(fileName, 'r') as f:
        data = f.read()
    return data


def writeToFile(data, outfile):
    """This functions dumps json data into a file.

    :param data: json data
    :param outfile: name of the output file
    """
    logger.info("Saving Results to file: " + outfile)
    try:
        with open(outfile, 'w') as out:
            out.write(data)
    except IOError as err:
        logger.error("Could not open file to save the data! " + str(err))
    except:
        logger.error("Unexpected error occurred! " + str(sys.exc_info()[0:1]))
    else:
        logger.info("Saving successful")
