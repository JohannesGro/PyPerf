#!c:\ce\trunk\sqlite\bin\powerscript.exe
# Some imports
import logging
import os
import random
import sys
import time
import traceback

import requests

from bench import Bench
from timer import Timer

logger = logging.getLogger("[" + __name__ + " - LoginBenchmark]")

payload = os.urandom(100 * 1024)


class LoginBenchmark(Bench):
    def setUpClass(self):
        self.establishConnection()

    def establishConnection(self):
        logger.info("Connecting to http://%s/login ..." % self.args["server"])
        with Timer() as t:
            # 5 attempts
            for _ in range(0, 5):
                try:
                    self.rsp = requests.post("http://%s/login" % self.args["server"],
                                             data={"username": "caddok", "password": ""})
                    break
                except:
                    continue
        if not hasattr(self, "rsp"):
            logger.error("No connection could be established")
            raise Exception("No connection could be established")
        else:
            self.storeResult(t.elapsed.total_seconds())

    def bench_sending_requests(self):
        logger.info("bench_sending_requests")

        total = []
        for _ in range(self.args["iterations"]):
            start_time = time.time()
            with Timer() as t:
                # 5 attempts to establish a connection
                for _ in range(0, 5):
                    try:
                        url = "http://%s%s" % (self.args["server"], self.args["self"].args["testpath"])
                        if payload:
                            print "POST ", url
                            self.rsp = requests.post(url, data=payload, cookies=self.rsp.cookies)
                        else:
                            print "GET ", url
                            self.rsp = requests.get(url, cookies=self.rsp.cookies)
                        break
                    except:
                        continue

                # next_request_after = random.choice(range(5))
                # print("Next request after %i seconds!" % next_request_after)
                # time.sleep(next_request_after)
            total.append(t.elapsed.total_seconds())
        self.storeResult(total, type="time_series")

    def tearDownClass(self):
        logger.info(" Logging out...")
        requests.get("http://%s/server/__quit__" % self.args["server"], cookies=self.rsp.cookies)


# Guard importing as main module
if __name__ == "__main__":
    print LoginBenchmark().run({
                               "server": "127.0.0.1:7000",
                               "testpath": "/server/__keep_alive__",
                               "iterations": 100
                               })
