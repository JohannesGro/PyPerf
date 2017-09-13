#!c:\ce\trunk\sqlite\bin\powerscript.exe
# -*- mode: python; coding: utf-8 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# https://www.contact-software.com/

"""Provides serveral system information.
"""

import ctypes
import datetime
import getpass
import logging
import multiprocessing
import platform
import subprocess
import sys

from cdb import rte, sqlapi, version
from cdb.uberserver import usutil

logger = logging.getLogger("[" + __name__ + " - sysEnv]")


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
        ("sullAvailupdateedVirtual", ctypes.c_ulonglong),
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
    res = {}
    res['Memory Load in %'] = stat.dwMemoryLoad
    res['Memory Total Phys in MB'] = stat.ullTotalPhys / mega
    res['Memory Available Phys in MB'] = stat.ullAvailPhys / mega
    res['Memory Total Virtual in MB'] = stat.ullTotalVirtual / mega
    return res


def getMac():
    from uuid import getnode as get_mac
    return hex(get_mac())


def getMacInfo():
    logger.info("MAC-Adress: %s" % (getMac()))
    return {"MAC-Adress": getMac()}


def getAllHostnames():
    return usutil.gethostnames()


def getAllHostnamesInfo():
    logger.info("Hostnames: {}".format(usutil.gethostnames()))
    return {"Hostnames": getAllHostnames()}


def getSysInfo():
    logger.info("Elements Version: %s", version.getVersionDescription())
    logger.info("Current Time (UTC): %s", datetime.datetime.utcnow().isoformat())
    logger.info("Current User: %s", getpass.getuser())
    logger.info("OS-Platform: %s", sys.platform)
    logger.info("OS-Platform version: %s", platform.platform())
    logger.info("Processor: %s", platform.processor())
    logger.info("CPU Count: %d", multiprocessing.cpu_count())
    res = {}
    res["Elements Version"] = version.getVersionDescription()
    res["Current Time (UTC)"] = datetime.datetime.utcnow().isoformat()
    res["Current User"] = getpass.getuser()
    res["OS-Platform"] = sys.platform
    res["OS-Platform version"] = platform.platform()
    res["Processor"] = platform.processor()
    res["CPU Count"] = multiprocessing.cpu_count()
    return res


def getCADDOKINfos():
    res = {}

    for var in ('CADDOK_FLS_SOED',
                'CADDOK_DB_RETRY',
                'CADDOK_DEFAULT',
                'CADDOK_TMPDIR',
                'CADDOK_SERVER',
                'CADDOK_LOGDIR',
                'CADDOK_DBMODE',
                'CADDOK_ARCH',
                'CADDOK_AUTH_PERSNO',
                'CADDOK_DEBUG',
                'CADDOK_TOPDIR',
                'CADDOK_DBDRIVER',
                'CADDOK_WWWSERVICE_URL',
                'CADDOK_SQLDBMS_STRLEN',
                'CADDOK_DBNAME',
                'CADDOK_BASE',
                'CADDOK_RUNTIME',
                'CADDOK_LANGUAGE',
                'CADDOK_DBSYS',
                'CADDOK_SQLDBMS',
                'CADDOK_AUTH_LOGIN',
                'CADDOK_ISOLANG',
                'CADDOK_AUTH_FULLNAME',
                'CADDOK_HOME',
                'CADDOK_SOED_PLACES',
                'CADDOK_DBCNCT',
                'CADDOK_MAX_USER_SESSIONS',
                'CADDOK_SML_SHOWID',
                'CADDOK_AUTH_REAL_LOGIN',
                'CADDOK_APP_CONF',
                'CADDOK_AUTH_SOURCE',
                'CADDOK_REPLICATION_DOMAIN',
                'CADDOK_DB3',
                'CADDOK_DB2',
                'CADDOK_DB1',
                'CADDOK_CDBPKG_HOST',
                'CADDOK_INSTALLDIR',
                'CADDOK_PACKAGE_REPOSITORY_DIR',
                'CADDOK_TOOL',
                'CADDOK_SCRIPTDIR'):
        if var in rte.environ:
            logger.info("%s: %s", var, rte.environ[var])
            res[var] = rte.environ[var]
    return res


def isVMware():
    prefix = ['0x000569', '0x000c29', '0x001c14', '0x005056']
    mac = getMac()
    for str in prefix:
        if str in mac:
            return True
    return False


def VMWareInfo():
    logger.info("Probalby running in VM: {}".format("Yes" if isVMware() else "No"))
    return {"Probalby running in VM": "Yes" if isVMware() else "No"}


def traceroute(dest):
    output = subprocess.check_output(["tracert", "-w", "100", dest], stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = output.decode('cp852')

    logger.info("Route to server: {}".format(output))
    return {"Route to server:": output}
    # output = subprocess.check_output(["traceroute", "-w", "100", "localhost"], stdin=subprocess.PIPE, stderr=subprocess.STDOUT)


def getAllSysInfos():
    logger.info("SYSINFOS:\n")
    res = {}
    res.update(getSysInfo())
    res.update(getCADDOKINfos())
    if 'CADDOK_CDBPKG_HOST' in res:
        res.update(traceroute(res['CADDOK_CDBPKG_HOST']))
    res.update(VMWareInfo())
    res.update(getAllHostnamesInfo())
    res.update(getMacInfo())
    res.update(getMemoryInfos())
    return res
