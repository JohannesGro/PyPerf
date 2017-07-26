#!c:\ce\trunk\sqlite\bin\powerscript.exe
import logging
import time
from random import choice
from string import lowercase

from bench import Bench
from cdb import sqlapi

logger = logging.getLogger(__name__)


class SqlApiBenchmark(Bench):
    """

    """
    def setUpClass(self):
        pass

    def tearDownClass(self):
        pass

    def setUp(self):
        logger.info("[SqlApiBenchmark]: create table benchmark_table...")
        sqlapi.SQL_nova('create table if not exists benchmark_table (bench_string, bench_num)')

    def tearDown(self):
        logger.info("[SqlApiBenchmark]: drop table benchmark_table...")
        sqlapi.SQL_nova("drop table benchmark_table ")

    def insert_generator(self, num):
        str_len = 10
        for i in range(0, num):
            string_val = "".join(choice(lowercase) for i in range(str_len))
            yield (string_val, i)

    def bench_insert(self):
        logger.info("[SqlApiBenchmark]: bench_insert")

        total = []
        for i in self.insert_generator(self.args['rows']):
            pre_time = time.time()
            sqlapi.SQL_nova("insert into benchmark_table (bench_string, bench_num) values " + str(i))
            post_time = time.time()
            total.append(post_time - pre_time)

        return {"type": "time series", "time": {"val": total, "unit": "seconds"}}

    def bench_update(self):
        logger.info("[SqlApiBenchmark]: bench_update")

        for i in self.insert_generator(self.args['rows']):
            sqlapi.SQL_nova("insert into benchmark_table (bench_string, bench_num) values " + str(i))
        start_time = time.time()
        sqlapi.SQL_nova( "update benchmark_table set bench_num=bench_num*2")
        end_time = time.time()
        total = end_time - start_time
        return {"type": "time", "time": {"val": total, "unit": "seconds"}}


if __name__ == "__main__":
    SqlApiBenchmark().runTests({})
