import logging
# sqlite db
import sqlite3
import time
# for the string generator
from random import choice
from string import lowercase

from pyperf.bench import Bench
from pyperf.timer import Timer

logger = logging.getLogger("[" + __name__ + " - SqliteBenchmark]")


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
        logger.info("create table benchmark_table...")
        self.cur.execute("create table if not exists benchmark_table (bench_string, bench_num)")

    def tearDown(self):
        logger.info("drop table benchmark_table...")
        self.cur.execute("drop table benchmark_table ")

    def insert_generator(self, num):
        """generator for random strings"""
        str_len = 10
        for i in range(0, num):
            string_val = "".join(choice(lowercase) for i in range(str_len))
            yield (string_val, i)

    def do_inserts(self, rows):
        """executes a amount of inserts"""
        total = []
        for i in range(rows):
            with Timer() as t:
                self.cur.executemany("insert into benchmark_table (bench_string, bench_num) values (?, ?)", self.insert_generator(self.args['rows']))
            total.append(t.elapsed.total_seconds())
        self.storeResult(total, type="time series")

    def bench_update(self):
        """test for updates"""
        logger.info("bench_update")
        self.namespace = "bench_update_"
        self.do_inserts(self.args['rows'])
        self.namespace = ""
        total = []
        for i in range(self.args['iterations']):
            with Timer() as t:
                self.cur.execute("update benchmark_table set bench_num=bench_num*2")
            total.append(t.elapsed.total_seconds())
        self.storeResult(total, type="time series")


if __name__ == "__main__":
    SqliteBenchmark().run({})
