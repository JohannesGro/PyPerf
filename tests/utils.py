#!/usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

import os


def coverage_opts():
    opts = []
    opts_env = os.environ.get("COVERAGE_OPTS", None)
    if opts_env:
        opts = opts_env.split(" ")
    return opts
