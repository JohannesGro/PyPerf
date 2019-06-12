# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2019 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/


class PyperfError(Exception):
    def __init__(self, message):
        self.message = message
