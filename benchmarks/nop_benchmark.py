# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""
This benchmarks measures the performance of pyperf itself
"""

import logging

from pyperf.bench import Bench
from pyperf.timer import Timer


logger = logging.getLogger(__name__)


class NOPBenchmark(Bench):

    def setUpClass(self):
        pass

    def tearDownClass(self):
        pass

    def bench_nop(self):
        times = []
        for i in range(0, self.args["iterations"]):
            with Timer() as t:
                pass
            times.append(t.elapsed.total_seconds())
        self.storeResult(times, name="bench_runtime", type="time_series")
