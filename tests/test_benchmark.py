# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

from benchmarktool import benchmark
from nose.tools import eq_, raises


def test_parse_timestamp():
    data = {
        "1s": ("1", "s"),
        "1ms": ("1", "ms"),
        "1111111111111111ms": ("1111111111111111", "ms"),
        "2222222222222222s": ("2222222222222222", "s")
    }

    for rawts, exp_output, in data.iteritems():
        output = benchmark.parse_timestamp_param(rawts)
        eq_(exp_output, output)


@raises(benchmark.BadTimestampError)
def test_parse_timestamp_wrong_unit():
    benchmark.parse_timestamp_param("10kilo")


@raises(benchmark.BadTimestampError)
def test_parse_bad_timestamp():
    benchmark.parse_timestamp_param("1.1.1.1.1.1")
