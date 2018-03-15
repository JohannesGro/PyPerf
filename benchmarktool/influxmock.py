#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

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
        with open(".influxupload", "w") as fd:
            fd.write(data)

        return self.MockedResponse(self.sc)
