# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

from nose.tools import eq_
from .. import systemInfos as si


def test_getcpuifo_verbose():
    res = si.getCPUInfo(verbose=True)
    assert res

def test_getcpuifo_nonverbose():
    res = si.getCPUInfo(verbose=False)
    assert res


def test_getAllSysInfos():
    res = si.getAllSysInfos()
    assert res
