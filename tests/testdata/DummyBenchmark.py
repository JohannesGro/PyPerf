from pyperf.bench import Bench


class DummyBenchmark(Bench):
    def setUpClass(self):
        print("setUpClass called")

    def tearDownClass(self):
        print("tearDownClass called")

    def setUp(self):
        print("setUp called")

    def tearDown(self):
        print("tearDown called")

    def bench_func1(self):
        self.storeResult(1)

    def bench_func2(self):
        self.storeResult(2)
