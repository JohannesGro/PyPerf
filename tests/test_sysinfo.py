# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

from pyperf import systemInfos as si
import unittest


def test_getAllSysInfos():
    sysinfos_verbose = si.getAllSysInfos(verbose=True)
    sysinfos_sparse = si.getAllSysInfos(verbose=False)

    assert sysinfos_verbose
    assert sysinfos_sparse
    assert len(sysinfos_verbose) > len(sysinfos_sparse)


def test_matchVersion():
    inputs = {"15.3 Service Level 5 (build#r12355)": ("15.3", "5"),
              "15.3 Service Level dev (build564646)": ("15.3", "dev"),
              "15.10 Service Level dev (build#r123553)": ("15.10", "dev"),
              "15.10 Service Level 222 (build#r123553)": ("15.10", "222")}

    for ver in inputs:
        assert inputs[ver] == si.matchVersion(ver)


# TODO: Probably the production code should tolerate that
@unittest.skip("Failes on CI (no traceroute in container)")
def test_traceroute():
    routes = si.traceroute("localhost")
    assert routes
