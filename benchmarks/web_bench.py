import io
import json
import logging
import requests
import time

logging.basicConfig()
logger = logging.getLogger("[" + __name__ + " - WebBenchmark]")
ch = logging.StreamHandler()
logger.addHandler(ch)

from pyperf.bench import Bench
from pyperf.timer import Timer

from cdb import sqlapi, constants, rte
rte.ensure_run_level(rte.USER_IMPERSONATED, prog="", user="caddok")

from cs.platform.web.root import Root
from webtest import TestApp as Client
from cdbwrapc import Operation
from cdb.platform.mom import SimpleArguments
from cdb.platform.mom.entities import CDBClassDef

from cs.restgenericfixture import TestBenchmark


class WebBenchmark(Bench):
    def setUpClass(self):
        app = Root()
        self.client = Client(app)
        self.table = "test_benchmark"

    def bench_get_all(self):
        logger.info("bench_get_all")
        sql_count_before =  sqlapi.SQLget_statistics()['statement_count']
        with Timer() as t:
            response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'")
        sql_count_after =  sqlapi.SQLget_statistics()['statement_count']

        self.storeResult(t.elapsed.total_seconds(), name="RestApi Collection All Rows: no_cache")
        self.storeResult(sql_count_after - sql_count_before, name="RestApi Collection All Rows: SQL-Count", type="count", unit="statements")

        with Timer() as t:
            response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'")
        self.storeResult(t.elapsed.total_seconds(),  name="RestApi Collection All Rows: cache")


    def bench_get_subset(self):
        logger.info("bench_get_subset")

        for i in range(1,6):
            maxrows = 100 * i
            sql_count_before =  sqlapi.SQLget_statistics()['statement_count']
            with Timer() as t:
                response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'&maxrows={}".format(maxrows))
            sql_count_after =  sqlapi.SQLget_statistics()['statement_count']

            self.storeResult(t.elapsed.total_seconds(), name="RestApi Collection (Rows: {}): no_cache".format(maxrows))
            self.storeResult(sql_count_after - sql_count_before, name="RestApi Collection (Rows: {}): SQL-Count".format(maxrows), type="count", unit="statements")

            with Timer() as t:
                response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'&maxrows={}".format(maxrows))
            self.storeResult(t.elapsed.total_seconds(),  name="RestApi Collection (Rows: {}): cache".format(maxrows))


    def bench_get_all_as_table(self):
        logger.info("bench_get_all_as_table")

        self.get_all_as_table(self.table)
        self.get_all_as_table(self.table + "_no_icons")
        self.get_all_as_table(self.table + "_no_uuid")


    def get_all_as_table(self, table):
        sql_count_before =  sqlapi.SQLget_statistics()['statement_count']
        with Timer() as t:
            response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'&_as_table={}".format(table))
        sql_count_after =  sqlapi.SQLget_statistics()['statement_count']

        self.storeResult(t.elapsed.total_seconds(), name="RestApi Collection as table '{}' All Rows: no cache".format(table))
        self.storeResult(sql_count_after - sql_count_before, name="RestApi Collection as table '{}' All Rows SQL-Count".format(table), type="count", unit="statements")

        with Timer() as t:
            response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'&_as_table={}".format(table))
        self.storeResult(t.elapsed.total_seconds(), name="RestApi Collection as table '{}' All Rows: cache".format(table))


    def bench_get_subset_as_table(self):
        logger.info("bench_get_subset_as_table")

        for i in range(1,6):
            maxrows = 100 * i
            self.get_subset_as_table(self.table, maxrows)
            self.get_subset_as_table(self.table + "_no_icons", maxrows)
            self.get_subset_as_table(self.table + "_no_uuid", maxrows)


    def get_subset_as_table(self, table, maxrows):
            sql_count_before =  sqlapi.SQLget_statistics()['statement_count']
            with Timer() as t:
                response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'&_as_table={}&maxrows={}".format(table, maxrows))
            sql_count_after =  sqlapi.SQLget_statistics()['statement_count']

            self.storeResult(t.elapsed.total_seconds(), name="RestApi Collection as table '{}' (Rows: {}): no cache".format(table, maxrows))
            self.storeResult(sql_count_after - sql_count_before, name="RestApi Collection as table '{}' (Rows: {}) SQL-Count".format(table, maxrows), type="count", unit="statements")

            with Timer() as t:
                response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'&_as_table={}&maxrows={}".format(table, maxrows))
            self.storeResult(t.elapsed.total_seconds(), name="RestApi Collection as table '{}' (Rows: {}): cache".format(table, maxrows))


    def bench_get_progesseviley(self):
        logger.info("bench_get_progressively")
        time_series = []
        statements = []
        totalRows = 2000
        for i in range(self.args["step"], totalRows, self.args["step"]):
            sql_count_before =  sqlapi.SQLget_statistics()['statement_count']
            with Timer() as t:
                response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'&maxrows={}".format(i))
            sql_count_after =  sqlapi.SQLget_statistics()['statement_count']

            time_series.append(t.elapsed.total_seconds())
            statements.append(sql_count_after - sql_count_before)

        tmp = list(time_series)
        for i, val in enumerate(tmp):
            if i > 0:
                time_series[i] = val - tmp[i-1]

        self.storeResult(time_series, name="RestApi Collection All Row with maxrows Intervals", type="time_series")

        tmp = list(statements)
        for i, val in enumerate(tmp):
            if i > 0:
                statements[i] = val - tmp[i-1]

        self.storeResult(statements, name="RestApi Collection All Rows with maxrows Intervals SQL-Count", type="count_series", unit="statements")


    def bench_get_as_table_progesseviley(self):
        logger.info("bench_get_as_table_progressively")
        self.get_table_progressivly(self.table)
        self.get_table_progressivly(self.table + "_no_icons")
        self.get_table_progressivly(self.table + "_no_uuid")


    def get_table_progressivly(self, table):
        time_series = []
        statements = []
        totalRows = 2000
        for i in range(self.args["step"], totalRows, self.args["step"]):
            sql_count_before =  sqlapi.SQLget_statistics()['statement_count']
            with Timer() as t:
                response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'&maxrows={}&_as_table={}".format(i, table))
            sql_count_after =  sqlapi.SQLget_statistics()['statement_count']

            time_series.append(t.elapsed.total_seconds())
            statements.append(sql_count_after - sql_count_before)

        tmp = list(time_series)
        for i, val in enumerate(tmp):
            if i > 0:
                time_series[i] = val - tmp[i-1]

        self.storeResult(time_series, name="RestApi Collection with maxrows Intervals as table '{}'".format(table), type="time_series")

        tmp = list(statements)
        for i, val in enumerate(tmp):
            if i > 0:
                statements[i] = val - tmp[i-1]

        self.storeResult(statements, name="RestApi Collection with maxrows Intervals as table '{}' SQL-Count".format(table), type="count_series", unit="statements")


    def bench_search_operation(self):
        logger.info("bench_search_operation")
        op = Operation(constants.kOperationSearch,
                       CDBClassDef("test_benchmark"),
                       SimpleArguments(cdb_module_id="cs.restgenericfixture"))
        op.run()
        self.test_retrieve_table_data_cpp(op, "test_benchmark")
        self.test_retrieve_table_data_elements_ui(op, "test_benchmark")


    def test_retrieve_table_data_cpp(self, op, table_name):
        logger.info("test_retrieve_table_data_cpp")
        with Timer() as t:
            res = op.get_result()[1].as_table(table_name).getData()
        self.storeResult(t.elapsed.total_seconds(), name="Retrieve Table data (Kernel Operation)", type="time")

        with Timer() as t:
            res = op.get_result()[1].as_table(table_name + "_no_icons").getData()
        self.storeResult(t.elapsed.total_seconds(), name="Retrieve Table data without icons (Kernel Operation)", type="time")

        with Timer() as t:
            res = op.get_result()[1].as_table(table_name + "_no_uuid").getData()
        self.storeResult(t.elapsed.total_seconds(), name="Retrieve Table data without UUID (Kernel Operation)", type="time")


    def test_retrieve_table_data_elements_ui(self, op, table_name):
        logger.info("test_retrieve_table_data_elements_ui")
        params = {"object_navigation_id": None,
                  "values": {},
                  "operation_state" : op.getOperationState()}
        with Timer() as t:
            response = self.client.post_json(u'/internal/uisupport/operation/class/test_benchmark/CDB_Search/run',
                    params)
        self.storeResult(t.elapsed.total_seconds(), name="Retrieve Table data elements ui operations", type="time")




if __name__ == "__main__":
    step = 100
    webui = WebBenchmark()
    webui.run({'step': step})
