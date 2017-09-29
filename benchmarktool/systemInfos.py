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
import psutil
import subprocess
import sys

from cdb import rte, version
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
    mb = 1024 * 1024
    res = {}
    if psutil.WINDOWS:
        stat = MEMORYSTATUSEX()
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))

        logger.info("Memory total virtual: %dMB" % (stat.ullTotalVirtual / mb))
        res['Memory total virtual in MB'] = stat.ullTotalVirtual / mb

    mem = psutil.virtual_memory()
    logger.info("Memory total {}MB".format(mem.total / mb))
    res['Memory total memory in MB'] = mem.total / mb

    logger.info("Memory percent used: {}%".format(mem.percent))
    res['Memory percent used'] = mem.percent

    logger.info("Memory used {}MB".format(mem.used / mb))
    res['Memory used in MB'] = mem.used / mb

    logger.info("Memory free {}MB".format(mem.free / mb))
    res['Memory free in MB'] = mem.free / mb

    logger.info("Memory available {}MB".format(mem.available / mb))
    res['Memory available in MB'] = mem.available / mb
    if(psutil.POSIX):
        logger.info("Memory active {}MB".format(mem.active / mb))
        res['Memory active in MB'] = mem.active / mb

        logger.info("Inactive {}MB".format(mem.inactive / mb))
        res['Memory inactive in MB'] = mem.inactive / mb

    if(psutil.POSIX or psutil.BSD):
        logger.info("Memory buffers {}MB".format(mem.buffers / mb))
        res['Memory buffers in MB'] = mem.buffers / mb

        logger.info("Memory shared {}MB".format(mem.shared / mb))
        res['Memory shared in MB'] = mem.shared / mb

        logger.info("Memory cached {}MB".format(mem.cached / mb))
        res['Memory cached in MB'] = mem.cached / mb
    if(psutil.OSX or psutil.BSD):
        logger.info("Memory wired {}MB".format(mem.wired / mb))
        res['Memory wired in MB'] = mem.wired / mb

    swap = psutil.swap_memory()
    logger.info('Swap total memory {}MB'.format(swap.total / mb))
    res['Swap total memory in MB'] = swap.total / mb
    logger.info('Swap used memory {}MB'.format(swap.used / mb))
    res['Swap total used in MB'] = swap.used / mb
    logger.info('Swap free memory {}MB'.format(swap.free / mb))
    res['Swap free memory in MB'] = swap.free / mb
    logger.info('Swap percent memory {}'.format(swap.percent))
    res['Swap percent memory'] = swap.percent
    if not psutil.WINDOWS:
        logger.info('Swap in memory {}MB'.format(swap.sin / mb))
        res['Swap in memory in MB'] = swap.sin / mb

        logger.info('Swaped out memory {}MB'.format(swap.sout / mb))
        res['Swaped out memory'] = swap.sout / mb
    return res


def getMac():
    from uuid import getnode as get_mac
    # '0x' + 6bytes  = len 14
    return "{0:#0{1}x}".format(get_mac(), 14)


def getMacInfo():
    logger.info("MAC-Adress: %s" % (getMac()))
    return {"MAC-Adress": getMac()}


def getAllHostnames():
    return usutil.gethostnames()


def getAllHostnamesInfo():
    logger.info("Hostnames: {}".format(usutil.gethostnames()))
    return {"Hostnames": getAllHostnames()}


def diskIOCounter():
    # Disk IO counter: sdiskio(read_count=3919547, write_count=1767118, read_bytes=84891013632L, write_bytes=137526756352L, read_time=355414861L, write_time=260233546L)
    res = {}
    diskcounters = psutil.disk_io_counters(perdisk=False)
    logger.info('Disk IO read_count: {}'.format(diskcounters.read_count))
    res['Disk IO read_count'] = diskcounters.read_count
    logger.info('Disk IO write_count: {}'.format(diskcounters.write_count))
    res['Disk IO write_count'] = diskcounters.write_count
    logger.info('Disk IO read_bytes: {}'.format(diskcounters.read_bytes))
    res['Disk IO read_bytes'] = diskcounters.read_bytes
    logger.info('Disk IO write_bytes: {}'.format(diskcounters.write_bytes))
    res['Disk IO write_bytes'] = diskcounters.write_bytes
    logger.info('Disk IO read_time: {}'.format(diskcounters.read_time))
    res['Disk IO read_time'] = diskcounters.read_time
    logger.info('Disk IO write_time: {}'.format(diskcounters.write_time))
    res['Disk IO write_time'] = diskcounters.write_time
    return res


def getSysInfo():
    logger.info("Elements Version: %s", version.getVersionDescription())
    logger.info("Current Time (UTC): %s", datetime.datetime.utcnow().isoformat())
    logger.info("Current User: %s", getpass.getuser())
    logger.info("OS-Platform: %s", sys.platform)
    logger.info("OS-Platform version: %s", platform.platform())
    logger.info("Processor: %s", platform.processor())
    res = {}
    res["Elements Version"] = version.getVersionDescription()
    res["Current Time (UTC)"] = datetime.datetime.utcnow().isoformat()
    res["Current User"] = getpass.getuser()
    res["OS-Platform"] = sys.platform
    res["OS-Platform version"] = platform.platform()
    res["Processor"] = platform.processor()
    return res


def getCPUInfo():
    res = {}
    cpu_times = psutil.cpu_times()
    logger.info("CPU time spent by processes in user mode: {}".format(cpu_times.user))
    res["CPU time spent by processes in user mode"] = cpu_times.user
    logger.info("CPU time spent by processes in kernel mode: {}".format(cpu_times.system))
    res["CPU time spent by processes executing in kernel mode"] = cpu_times.system
    logger.info("CPU time spent  doing nothing: {}".format(cpu_times.idle))
    res["CPU time spent doing nothing"] = cpu_times.idle

    logger.info('CPU Percent: {}'.format(psutil.cpu_percent(interval=1, percpu=False)))
    res['CPU Percent'] = psutil.cpu_percent(interval=1, percpu=False)
    logger.info('CPU Percent Time Spent: {}'.format(psutil.cpu_times_percent(interval=1.1, percpu=False)))
    res['CPU Percent Time Spent'] = psutil.cpu_times_percent(interval=1.1, percpu=False)

    logger.info('CPU count locial CPUs: {}'.format(psutil.cpu_count()))
    res['CPU count locial CPUs'] = psutil.cpu_count()
    logger.info('CPU count physical CPUs: {}'.format(psutil.cpu_count(logical=False)))
    res['CPU count physical CPUs'] = psutil.cpu_count(logical=False)

    logger.info("CPU Frenquency: {}".format(psutil.cpu_freq(percpu=False)))
    res['CPU Frenquency'] = psutil.cpu_freq(percpu=False)
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
    """ VMware ESX 3, Server, Workstation, Player	00-50-56, 00-0C-29, 00-05-69, 0x001c14
        Microsoft Hyper-V, Virtual Server, Virtual PC	00-03-FF
        Parallells Desktop, Workstation, Server, Virtuozzo	00-1C-42
        Virtual Iron 4	00-0F-4B
        Red Hat Xen	00-16-3E
        Oracle VM	00-16-3E
        XenSource	00-16-3E
        Novell Xen	00-16-3E
        Sun xVM VirtualBox	08-00-27"""
    prefix = ['0x000569', '0x000c29', '0x001c14', '0x005056', "0x0003ff", "0x001c42", "0x000f4b", "0x00163e", "0x080027"]

    mac = getMac()
    for str in prefix:
        if str in mac:
            return True
    return False


def VMWareInfo():
    logger.info("VM running?: (probably) {}".format("Yes" if isVMware() else "No"))
    return {"VM running?: (probably) ": ("Yes" if isVMware() else "No")}


def msinfo32():
    res = {}
    if(psutil.WINDOWS):
        import xml.etree.ElementTree as ElementTree
        import os

        fileName = "msinfo.xml"
        proc = subprocess.Popen(['msinfo32', "/nfo", fileName], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = proc.stdout.read()

        root = ElementTree.parse(fileName).getroot()

        cat_list = ['Systemübersicht', 'Datenträger']
        for cat in root.iter("Category"):
            if cat.get('name') in cat_list:
                for data in cat.findall("Data"):
                    res[data.find('Element').text] = data.find('Wert').text
        os.unlink(fileName)
    return res


def traceroute(dest):
    import re
    m = re.search("\/\/(.*):", dest)
    if m is None:
        dest = "localhost"
    else:
        dest = m.group(1)
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
    res.update(getCPUInfo())
    if 'CADDOK_SERVER' in res:
        res.update(traceroute(res['CADDOK_SERVER']))
    res.update(VMWareInfo())
    res.update(getAllHostnamesInfo())
    res.update(getMacInfo())
    res.update(getMemoryInfos())
    res.update(diskIOCounter())
    res.update(msinfo32())
    return res
