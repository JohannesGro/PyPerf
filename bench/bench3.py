#!c:\ce\trunk\sqlite\bin\powerscript.exe
# Some imports
import logging
import os
import random
import time
import traceback

import requests

from bench import Bench

logger = logging.getLogger(__name__)

payload = os.urandom(100 * 1024)


class LoginBenchmark(Bench):
    def setUpClass(self):
        # 5 attempts
        for _ in range(0, 5):
            try:
                self.rsp = requests.post("http://%s/login" % self.args["server"],
                                         data={"username": "caddok", "password": ""})
                break
            except:
                continue
        if not hasattr(self, "rsp"):
            logger.info("[LoginBenchmark]: No connection could be established")

    def bench_sending_requests(self):
        if not hasattr(self, "rsp"):
            return
        logger.info("[LoginBenchmark]: bench_sending_requests")
        start_time = time.time()
        for _ in range(self.args["iterations"]):
            # 5 attempts
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
            end_time = time.time()
            total = end_time - start_time
            return [total, "seconds"]

    def tearDownClass(self):
        if hasattr(self, "rsp"):
            logger.info("[LoginBenchmark]:  Logging out...")
            requests.get("http://%s/server/__quit__" % self.args["server"], cookies=self.rsp.cookies)


# Guard importing as main module
if __name__ == "__main__":
    LoginBenchmark().runTests({})
