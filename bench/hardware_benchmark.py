#!C:\ce\trunk\win32\release\img\python
import hashlib
import logging
import sys
import time

import numpy as np
from bench import Bench

logger = logging.getLogger("[" + __name__ + " - HardwareBenchmark]")


class HardwareBenchmark(Bench):
    """
    This is a hardware benchmark.
    """

    def setUp(self):
        pass

    def bench_cpu(self):
        logger.info("bench_cpu...")
        total = []
        for i in range(self.args["cpu-iterations"]):
            start_time = time.time()
            dk = hashlib.pbkdf2_hmac('sha256', b'password', b'salt', 100000)
            end_time = time.time()
            total.append(end_time - start_time)
        return {"type": "time series", "time": {"val": total, "unit": "seconds"}}

    def bench_mem(self):
        logger.info("bench_mem...")
        matrix = np.random.rand(self.args["matrix-size"], self.args["matrix-size"])

        total = []
        for i in range(self.args["matrix-iterations"]):
            start_time = time.time()
            np.linalg.inv(matrix)
            end_time = time.time()
            total.append(end_time - start_time)
        return {"type": "time series", "time": {"val": total, "unit": "seconds"}}

    def bench_disk_speed(self):
        logger.info("bench_disk_speed...")
        blocksize = self.args["blocksize"]
        chunk = b'\xff' * 10000
        total = []
        for i in range(self.args["disk-iterations"]):
            with open("test.file", "wb") as f:
                start_time = time.time()
                for _ in range(blocksize // 10000):
                    f.write(chunk)
                end_time = time.time()
            total.append(end_time - start_time)
        return {"type": "time series", "MB/s": [blocksize / i / (1000 * 1000) for i in total if i != 0], "time": {"val": total, "unit": "seconds"}}

if __name__ == "__main__":
    HardwareBenchmark().run({"disk-iterations": 10, "matrix-iterations": 10, "cpu-iterations": 10, "matrix-size": 1000, "blocksize": 10000})
