# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

from .. import systemInfos as si


def test_getcpuifo_verbose():
    cpuinfos_verbose = si.getCPUInfo(verbose=True)
    cpuinfos_sparse = si.getCPUInfo(verbose=False)
    assert cpuinfos_verbose
    assert cpuinfos_sparse
    assert len(cpuinfos_verbose) > len(cpuinfos_sparse)


def test_getAllSysInfos():
    sysinfos_verbose = si.getAllSysInfos(verbose=True)
    sysinfos_sparse = si.getAllSysInfos(verbose=False)

    assert sysinfos_verbose
    assert sysinfos_sparse
    assert len(sysinfos_verbose) > len(sysinfos_sparse)


def test_traceroute():
    routes = si.traceroute("localhost")
    assert routes
