# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

from nose.tools import eq_
from .. import systemInfos as si


def test_getcpuifo_verbose():
    res = si.getCPUInfo(verbose=True)
    eq_(len(res), 9)


def test_getcpuifo_nonverbose():
    res = si.getCPUInfo(verbose=False)
    eq_(len(res), 3)
