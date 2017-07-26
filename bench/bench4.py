#!C:\ce\trunk\win32\release\img\python
import hashlib
import logging
import sys
import time

import numpy as np
from bench import Bench

logger = logging.getLogger(__name__)


class HardwareBenchmark(Bench):
    """
    This is an example for building a test case.
    """

    def setUp(self):
        pass

    def bench_cpu(self):
        logger.info("[HardwareBenchmark]: bench_cpu...")
        start_time = time.time()
        dk = hashlib.pbkdf2_hmac('sha256', b'password', b'salt', self.args["iterations"])
        end_time = time.time()
        total = end_time - start_time
        return {"type": "time", "time": {"val": total, "unit": "seconds"}}

    def bench_mem(self):
        logger.info("[HardwareBenchmark]: bench_mem...")
        matrix = np.random.rand(self.args["matrix-size"], self.args["matrix-size"])
        start_time = time.time()
        np.linalg.inv(matrix)
        end_time = time.time()
        total = end_time - start_time
        return {"type": "time", "time": {"val": total, "unit": "seconds"}}

    def bench_disk_speed(self):
        logger.info("[HardwareBenchmark]: bench_disk_speed...")
        blocksize = self.args["blocksize"]
        chunk = b'\xff' * 10000
        with open("test.file", "wb") as f:
            start_time = time.time()
            for _ in range(blocksize // 10000):
                f.write(chunk)
            end_time = time.time()
        total = end_time - start_time
        return {"type": "time", "MB/s": blocksize / total / (1000 * 1000), "time": {"val": total, "unit": "seconds"}}

if __name__ == "__main__":
    HardwareBenchmark().runTests({})
