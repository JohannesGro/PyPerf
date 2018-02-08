# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""
Module template

This is the documentation for the template module.
"""

import argparse

__docformat__ = "restructuredtext en"
__revision__ = "$Id$"

# Exported objects
__all__ = []


class InfluxUploader(object):
    """
    Reads the results and uploads it to InfluxDB.
    """
    parser = argparse.ArgumentParser(description=__doc__, prog="Uploader")
    parser.add_argument("--influxdburl", "-u",
                        help="The URL to the Influx DBMS to upload the results onto.")
    parser.add_argument("--database", "-d", help="The database to upload the results into.")

    def __init__(self, args):
        pass

    def main(self):
        print("called!")
