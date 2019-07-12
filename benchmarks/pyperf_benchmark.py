# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""
This benchmarks measures the performance of pyperf itself
"""

import logging
import subprocess
import sys

from pyperf.bench import Bench
from pyperf.timer import Timer


logger = logging.getLogger(__name__)


class PyPerfBenchmark(Bench):

    def setUpClass(self):
        pass

    def tearDownClass(self):
        pass

    def bench_nop(self):
        times = []
        for i in range(0, self.args["iterations"]):
            python = sys.executable
            cmdline = [python, "-m", "pyperf", "run", "-o", "nop-report.json", "-s", "nop-suite.json"]
            with Timer() as t:
                subprocess.check_call(cmdline)
            times.append(t.elapsed.total_seconds())
        self.storeResult(times, name="bench_runtime", type="time_series")
