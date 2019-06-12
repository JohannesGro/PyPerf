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
from six import PY2
from pyperf.exceptions import PyperfError

logger = logging.getLogger("[" + __name__ + " - I/O Service]")


def loadJSONData(json_file):
    """This functions load the json-data and returns it.

    :param fileName: name of the destination file
    :param json_file: the file in json format
    :returns: json object
    :raises: ValueError: the file content could not be decoded as JSON
    """
    try:
        with io.open(json_file, encoding="UTF-8") as data_file:
            return json.load(data_file)
    except ValueError:
        raise PyperfError("The content of '%s' could not be decoded as JSON." % json_file)
    except IOError:
        raise PyperfError("Could not open file '%s' to load the data!" % json_file)


def saveJSONData(data, fileName="benchmarkResults.json"):
    """This functions dumps json data into a file. The name of the output file
    is determined by parameter. The default output file is 'benchmarkResults.json'.

    :param data: json data which will be saved to file
    :param fileName: the name of the file where the data will be saved
    :raises TypeError: when data could not be converted to JSON
    :raises IOError: when the JSON-data could not be written to fileName
    :returns True when data could be written to fileName
    """
    try:
        if PY2:
            jsonData = json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False).decode(encoding="utf-8")
        else:
            jsonData = json.dumps(data, sort_keys=True, indent=4, ensure_ascii=False)
    except TypeError:
        raise PyperfError("Could not serialize object %s!" % data)
    else:
        try:
            with io.open(fileName, 'w', encoding="utf-8") as outfile:
                outfile.write(jsonData)
            return True
        except IOError:
            raise PyperfError("Could not open file '%s' to save the data!" % fileName)


def readFile(fileName):
    """Reads a file and return the content

    :param fileName: name of the file
    :returns content of the file as string
    """
    try:
        with io.open(fileName, 'r') as f:
            data = f.read()
        return data
    except IOError:
        raise PyperfError("Could not open file '%s' to load the data!" % fileName)


def writeToFile(data, outfile):
    """This functions dumps json data into a file.

    :param data: json data
    :param outfile: name of the output file
    :raises IOError: when the data could not be written to outfile
    :returns True when the data has been written to outfile
    """
    try:
        with io.open(outfile, 'w', encoding="UTF-8") as out:
            if PY2 and not isinstance(data, unicode):
                out.write(data.decode("utf-8"))
            else:
                out.write(data)
        return True
    except IOError:
        raise PyperfError("Could not open file '%s' to save the data!" % outfile)
