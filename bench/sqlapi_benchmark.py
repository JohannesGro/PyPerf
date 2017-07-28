#!c:\ce\trunk\sqlite\bin\powerscript.exe
import logging
import time
from random import choice
from string import lowercase

from bench import Bench
from cdb import sqlapi

logger = logging.getLogger("[" + __name__ + " - SqlApiBenchmark]")


class SqlApiBenchmark(Bench):
    """

    """
    def setUpClass(self):
        pass

    def tearDownClass(self):
        pass

    def setUp(self):
        logger.info("create table benchmark_table...")
        sqlapi.SQL('create table if not exists benchmark_table (bench_string, bench_num)')

    def tearDown(self):
        logger.info("drop table benchmark_table...")
        sqlapi.SQL("drop table benchmark_table ")

    def insert_generator(self, num):
        str_len = 10
        for i in range(0, num):
            string_val = "".join(choice(lowercase) for i in range(str_len))
            yield (string_val, i)

    def bench_insert(self):
        logger.info("bench_insert")
        res = []
        for i in range(self.args['iterations']):
            total = []
            start = time.time()
            for i in self.insert_generator(self.args['rows']):
                pre_time = time.time()
                sqlapi.SQL("insert into benchmark_table (bench_string, bench_num) values " + str(i))
                post_time = time.time()
                total.append(post_time - pre_time)
            end = time.time()
            res.append({"type": "time series", "time": {"val": total, "unit": "seconds"}, "totalTime": end - start})
        self.storeResult(res)

    def bench_SQLinsert(self):
        logger.info("bench_insert")
        res = []
        for i in range(self.args['iterations']):
            total = []
            start = time.time()
            for i in self.insert_generator(self.args['rows']):
                pre_time = time.time()
                sqlapi.SQLinsert("into benchmark_table (bench_string, bench_num) values " + str(i))
                post_time = time.time()
                total.append(post_time - pre_time)
            end = time.time()
            res.append({"type": "time series", "time": {"val": total, "unit": "seconds"}, "totalTime": end - start})
        self.storeResult(res)

    def bench_update(self):
        logger.info("bench_update")

        for i in self.insert_generator(self.args['rows']):
            sqlapi.SQL("insert into benchmark_table (bench_string, bench_num) values " + str(i))
        total = []
        for i in range(self.args['iterations']):
            start_time = time.time()
            sqlapi.SQL("update benchmark_table set bench_num=bench_num*2")
            end_time = time.time()
            total.append(end_time - start_time)
        self.storeResult({"type": "time series", "time": {"val": total, "unit": "seconds"}})

    def bench_SQLupdate(self):
        logger.info("bench_update")

        for i in self.insert_generator(self.args['rows']):
            sqlapi.SQL("insert into benchmark_table (bench_string, bench_num) values " + str(i))
        total = []
        for i in range(self.args['iterations']):
            start_time = time.time()
            sqlapi.SQLupdate("benchmark_table set bench_num=bench_num*2")
            end_time = time.time()
            total.append(end_time - start_time)
        self.storeResult({"type": "time series", "time": {"val": total, "unit": "seconds"}})


if __name__ == "__main__":
    print SqlApiBenchmark().run({"rows": 1000, "iterations": 10})
