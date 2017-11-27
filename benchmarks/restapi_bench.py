import logging
import requests


logging.basicConfig()
logger = logging.getLogger("root")


from benchmarktool.bench import Bench
from benchmarktool.timer import Timer

from cdb import sqlapi

from cs.platform.web.root import Root
from webtest import TestApp as Client


logger = logging.getLogger("[" + __name__ + " - RestapiBenchmark]")

class RestapiBenchmark(Bench):
    def setUpClass(self):
        app = Root()
        self.client = Client(app)    

    def bench_get_all(self):
        logger.info("bench_get_all")
        sql_count_before =  sqlapi.SQLget_statistics()['statement_count']
        with Timer() as t:
            response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'")
        sql_count_after =  sqlapi.SQLget_statistics()['statement_count']    
        self.storeResult(t.elapsed.total_seconds(), name="Get: no_cache")
        self.storeResult(sql_count_after - sql_count_before, name="Get SQL-Count: no cache", type="count")

        with Timer() as t:
            response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'")
        self.storeResult(t.elapsed.total_seconds(),  name="Get: cache")
#        print response.json


    def bench_get_all_astable(self):
        logger.info("bench_get_all_astable")
        with Timer() as t:
            response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'&_as_table")
        self.storeResult(t.elapsed.total_seconds(), name="Get as table: no cache")

        with Timer() as t:
            response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'&_as_table")
        self.storeResult(t.elapsed.total_seconds(),  name="Get as table: cache")
#        print response.json


    def bench_progesseviley(self):
        result = []
        for i in range(1,2000, self.args["step"]):
            with Timer() as t:
                response = self.client.get(u"/api/v1/collection/TestBench?$filter=cdb_module_id eq 'cs.restgenericfixture'&maxrows={}".format(i))
            result.append(t.elapsed.total_seconds())
        self.storeResult(result, name="Get Progessive", type="time_series")

    def tearDownClass(self):
        print self.results


if __name__ == "__main__":
    RestapiBenchmark().run({'step': 50})
