# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

import unittest

from ..influxuploader import InfluxUploader


class TestInfluxdbUploader(unittest.TestCase):
    def setUp(self):
        pass

    # whatta bs..
    # def test_init_doesnt_throw(self):
    #     parser = argparse.ArgumentParser(description=__doc__)
    #     args = parser.parse_args()
    #     InfluxUploader(args)

# Testcases:
# * tagging:
#   - happy case
#   - nothing relevant in sysinfo
#   - empty sysinfo
#
# * aggregating_time_series:
#   - empty series
#   - trivial
#   - second trivial
#   - a big one

# * extract_hostname:
#   - happy case
#   - no valid hostname there
#   - empty dict

# * main
#   Mock requests
#   - happy case
#   - http error
#   - sysinfos incomplete
#   - report doesnt contain results
#   - JSON invalid
