#!demoLauncher.cmd
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""This module is used for i/o operations.
"""

import io
import json
import logging
import sys

logger = logging.getLogger("[" + __name__ + " - I/O Service]")


def loadJSONData(json_file):
    """This functions load the json-data and returns it.

    :param fileName: name of the destination file
    :param json_file: the file in json format
    :returns: json object
    """
    try:
        with io.open(json_file, encoding="UTF-8") as data_file:
            data = json.load(data_file)
    except IOError as err:
        logger.exception("Could not open json file ({})! ".format(json_file, str(err)))
        sys.exit(1)
    except ValueError as err:  # JSONDecodeError inherrits from ValueError
        logger.exception("Could not decode json file ({})! {}".format(json_file, str(err)))
        sys.exit(1)
    except:
        logger.exception("Unexpected error occurred! {}".format(str(sys.exc_info()[0:1])))
        sys.exit(1)
    else:
        logger.info("Reading json file successful ({})".format(json_file))
    return data


def saveJSONData(fileName, data):
    """This functions dumps json data into a file. The name of the output file
    is determined by parameter. The default output file is 'benchmarkResults.json'.

    :param data: json data which will be saved to file
    """
    logger.info("Saving json to file '%s'", fileName)
    try:
        with io.open(fileName, 'w', encoding="utf-8") as outfile:
            outfile.write(unicode(json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)))
    except IOError as err:
        logger.exception("Could not open file to save the data! %s", err)
    except ValueError as err:  # JSONDecodeError inherrits from ValueError
        logger.exception("Could not decode values! %s", err)
    except TypeError as err:
        logger.exception("Could not serialize object! %s", err)
    except:
        logger.exception("Unexpected error occurred! %s", sys.exc_info()[0:1])
    else:
        logger.info("Saving successful")


def readFile(fileName):
    """Reads a file and return the content

    :param fileName: name of the file
    :returns: content of the file as string
    """
    with io.open(fileName, 'r') as f:
        data = f.read()
    return data


def writeToFile(data, outfile):
    """This functions dumps json data into a file.

    :param data: json data
    :param outfile: name of the output file
    """
    logger.info("Saving results to file '%s'", outfile)
    try:
        with io.open(outfile, 'w', encoding="UTF-8") as out:
            out.write(unicode(data))
    except IOError as err:
        logger.exception("Could not open file to save the data! %s", err)
    except:
        logger.exception("Unexpected error occurred! %s", sys.exc_info()[0:1])
    else:
        logger.info("Saving successful")
