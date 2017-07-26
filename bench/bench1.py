#!C:\ce\trunk\win32\release\img\python
import sqlite3
from random import choice
from string import lowercase
import time
from bench import Bench
import logging
logger = logging.getLogger(__name__)


class SqliteBenchmark(Bench):
    """
    This is an example for building a test case.
    """
    def setUpClass(self):
        self.conn = sqlite3.connect('benchmark_db.db')
        self.cur = self.conn.cursor()

    def tearDownClass(self):
        self.conn.close()

    def setUp(self):
        logger.info("[SqliteBenchmark]: create table benchmark_table...")
        self.cur.execute("create table if not exists benchmark_table (bench_string, bench_num)")

    def tearDown(self):
        logger.info("[SqliteBenchmark]: drop table benchmark_table...")
        self.cur.execute("drop table benchmark_table ")

    def insert_generator(self, num):
        str_len = 10
        for i in range(0, num):
            string_val = "".join(choice(lowercase) for i in range(str_len))
            yield (string_val, i)

    def test_insert(self):
        logger.info("[SqliteBenchmark]: test_insert")

        start_time = time.time()
        self.cur.executemany("insert into benchmark_table (bench_string, bench_num) values (?, ?)", self.insert_generator(self.args['rows']))
        end_time = time.time()

        total = end_time - start_time
        return {"type": "time", "time": {"val": total, "unit": "seconds"}}

    def test_update(self):
        logger.info("[SqliteBenchmark]: test_update")

        self.cur.executemany("insert into benchmark_table (bench_string, bench_num) values (?, ?)", self.insert_generator(self.args['rows']))
        start_time = time.time()
        self.cur.execute("update benchmark_table set bench_num=bench_num*2")
        end_time = time.time()
        total = end_time - start_time
        return {"type": "time", "time": {"val": total, "unit": "seconds"}}


if __name__ == "__main__":
    SqliteBenchmark().runTests({})
