#!/usr/bin/env python
# -*- python -*- coding: iso-8859-1 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# http://www.contact.de/
#

class InfluxMock(object):
    data_last = None

    class MockedResponse(object):
        def __init__(self, sc):
            self.text = ""
            self.status_code = sc

    def __init__(self, sc=200, exception=None):
        self.sc = sc
        self.exception = exception

    def __call__(self, url, data):
        if self.exception:
            raise self.exception

        # record for later checking
        self.data_last = data

        return self.MockedResponse(self.sc)
