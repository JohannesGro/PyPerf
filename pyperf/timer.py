# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

import datetime
import timeit


class Timer():
    def __init__(self):
        self.start = None
        self.elapsed = None

    def __enter__(self):
        self.start = timeit.default_timer()
        return self

    def __exit__(self, *exc):
        self.elapsed = datetime.timedelta(seconds=timeit.default_timer() - self.start)
        # logger.info(u"elapsed time: %s", self.elapsed)
        return False
