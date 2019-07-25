import fictional_database_module as database

from pyperf.bench import Bench
from pyperf.timer import Timer


class DatabaseBench(Bench):
    def bench_insert(self):
        db = database.connect("bench_database")
        db.execute("CREATE TABLE test ( testnumber Integer );")

        measurements = []
        for i in range(0, 10):
            with Timer() as t:
                db.execute("INSERT INTO test VALUES 42")
            measurements.append(t.elapsed.total_seconds())
        self.storeResult(measurements, name="bench_insert", type="time_series")
