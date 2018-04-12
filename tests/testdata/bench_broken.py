from pyperf.bench import Bench


class Benchmark(Bench):
    def setUpClass(self):
        boom  # noqa

    def bench_func1(self):
        boom  # noqa
