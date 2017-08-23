#!c:\ce\trunk\sqlite\bin\powerscript.exe
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/
import ctypes
import getpass
import multiprocessing
import platform
import sys

from cdb import sqlapi
from cdb import rte
from cdb.uberserver import usutil
from cdb import version


class SystemInfos(object):
    """Provides system information.
    """
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

        def __init__(self):
            # have to initialize this to the size of MEMORYSTATUSEX
            self.dwLength = ctypes.sizeof(self)
            super(MEMORYSTATUSEX, self).__init__()

    def getMemoryInfos():
        # working for windows only
        mega = 1024 * 1024
        stat = MEMORYSTATUSEX()
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))

        logger.info("MemoryLoad: %d%%" % (stat.dwMemoryLoad))
        logger.info("TotalPhys: %dMB" % (stat.ullTotalPhys / mega))
        logger.info("AvailPhys: %dMB" % (stat.ullAvailPhys / mega))
        logger.info("TotalVirtual: %dMB" % (stat.ullTotalVirtual / mega))

    def getMac():
        from uuid import getnode as get_mac
        logger.info("MAC: %x" % hex(get_mac()))

    def getAllHostnames():
        logger.info("Hostnames: %s" % usutil.gethostnames())

    def sys_info():
        logger.info("SYSINFOS:\n")
        logger.info("Elements Version: %s", version.getVersionDescription())
        logger.info("Script Version: %s", __revision__)
        logger.info("Hostname: %s", usutil.getfqdn())
        logger.info("Current Time (UTC): %s", datetime.datetime.utcnow().isoformat())
        logger.info("Current User: %s", getpass.getuser())
        logger.info("OS-Platform: %s", sys.platform)
        logger.info("OS-Platform version: %s", platform.platform())
        logger.info("Processor: %s", platform.processor())
        logger.info("CPU Count: %d", multiprocessing.cpu_count())

        for var in ("CADDOK_SERVER", "CADDOK_DBNAME", "CADDOK_DBSYS",
                    "CADDOK_DBCNCT", "CADDOK_DBMODE", "CADDOK_DBDRIVER",
                    "CADDOK_DB1", "CADDOK_DB2", "CADDOK_DB3"):
            logger.info("%s: %s", var, rte.environ[var])
        logger.info(72 * "-")
        results['Sysinfos'] = {"Elements Version": version.getVersionDescription(),
                               "Script Version": __revision__,
                               "Hostname": usutil.getfqdn(),
                               "Current Time (UTC)": datetime.datetime.utcnow().isoformat(),
                               "Current User": getpass.getuser(),
                               "OS-Platform": sys.platform,
                               "OS-Platform version:": platform.platform(),
                               "Processor": platform.processor(),
                               "CPU Count": multiprocessing.cpu_count()}

        for var in ("CADDOK_SERVER", "CADDOK_DBNAME", "CADDOK_DBSYS",
                    "CADDOK_DBCNCT", "CADDOK_DBMODE", "CADDOK_DBDRIVER",
                    "CADDOK_DB1", "CADDOK_DB2", "CADDOK_DB3"):
                results['Sysinfos'][var] = rte.environ[var]
    pass
