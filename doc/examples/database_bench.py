"""
This benchmarks measures the performance of inserting values into a database
"""

import logging
import fictional_database_module as database

from pyperf.bench import Bench
from pyperf.timer import Timer

logger = logging.getLogger(__name__)


class DatabaseBench(Bench):
    def setUpClass(self):
        self.db_name = self.args.get("db_name", "my_db")
        self.db = database.connect(self.db_name)
        logger.info("Connected to database %s", self.db_name)

    def tearDownClass(self):
        self.db.disconnect()
        logger.info("Disconnected from database %s.", self.db_name)

    def setUp(self):
        self.db.execute("CREATE TABLE test ( testnumber Integer );")
        logger.info("Table created.")

    def tearDown(self):
        self.db.execute("DROP TABLE test;")
        logger.info("Table dropped.")

    def bench_insert(self):
        measurements = []
        for i in range(0, self.args["iterations"]):
            with Timer() as t:
                self._insert(i)
            measurements.append(t.elapsed.total_seconds())

        self.storeResult(measurements, name="bench_insert", type="time_series")

    def _insert(self, i):
        self.db.execute("INSERT INTO test VALUES %d" % i)
