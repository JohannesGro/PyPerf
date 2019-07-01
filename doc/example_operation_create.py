# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2018 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""
This benchmarks the operation "create", raising the measurements
'runtime' and 'number of issued SQL statements'.

Note: this implementation strives to be compatible with older CDB
versions, currently 'older' means >= 15.0".
"""

import logging
import uuid

from pyperf.bench import Bench
from pyperf.timer import Timer
from cdb import constants
from cdb import sqlapi
from cdb import version
from cdb.objects.operations import operation
from cdb.platform.gui import Mask
from cdb.testcase import run_level_setup


logger = logging.getLogger(__name__)


class OperationCreate(Bench):

    def setUpClass(self):
        if run_level_setup:
            run_level_setup()
        self.createargs = {"role_id": "public"}
        self.warmup()

    def tearDownClass(self):
        for cdbobj in self.opresults:
            operation(constants.kOperationDelete, cdbobj)

    def warmup(self):
        self._call_operation()

    def bench_operation(self):
        times = []
        sql_counts = []
        self.opresults = []

        call_operation = self._call_operation

        for _ in range(self.args["iterations"]):
            sql_count_before = sqlapi.SQLget_statistics()['statement_count']
            with Timer() as t:
                opresult = call_operation()
            sql_count_after = sqlapi.SQLget_statistics()['statement_count']
            self.opresults.append(opresult)
            times.append(t.elapsed.total_seconds())
            sql_counts.append(sql_count_after - sql_count_before)

        self.storeResult(times, name="bench_runtime", type="time_series")
        self.storeResult(sql_counts, name="bench_sqlstms", type="count", unit="statements")

    def _call_operation(self):
        maskname = str(uuid.uuid1())[:30]
        return operation(constants.kOperationNew, Mask, name=maskname, **self.createargs)
