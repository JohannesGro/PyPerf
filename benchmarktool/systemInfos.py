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

import psutil


CDB_AVAILABLE = True
try:
    from cdb import rte, version
    from cdb.uberserver import usutil
except ImportError:
    CDB_AVAILABLE = False

logger = logging.getLogger("[" + __name__ + " - sysEnv]")


# windows memory information
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

        logger.info("Memory Total Virtual: {}MB".format(stat.ullTotalVirtual / mb))
        res['Memory Total Virtual (MB)'] = stat.ullTotalVirtual / mb

    mem = psutil.virtual_memory()
    logger.info("Memory Total: {}MB".format(mem.total / mb))
    res['Memory Total (MB)'] = mem.total / mb

    logger.info("Memory Percent: {}%".format(mem.percent))
    res['Memory Percent'] = mem.percent

    logger.info("Memory Used: {}MB".format(mem.used / mb))
    res['Memory Used (MB)'] = mem.used / mb

    logger.info("Memory Free: {}MB".format(mem.free / mb))
    res['Memory Free (MB)'] = mem.free / mb

    logger.info("Memory Available: {}MB".format(mem.available / mb))
    res['Memory Available (MB)'] = mem.available / mb
    if(psutil.POSIX):
        logger.info("Memory Active: {}MB".format(mem.active / mb))
        res['Memory Active (MB)'] = mem.active / mb

        logger.info("Memory Inactive: {}MB".format(mem.inactive / mb))
        res['Memory Inactive (MB)'] = mem.inactive / mb

    if(psutil.POSIX or psutil.BSD):
        logger.info("Memory Buffers: {}MB".format(mem.buffers / mb))
        res['Memory Buffers (MB)'] = mem.buffers / mb

        logger.info("Memory Shared: {}MB".format(mem.shared / mb))
        res['Memory Shared (MB)'] = mem.shared / mb

        logger.info("Memory Cached: {}MB".format(mem.cached / mb))
        res['Memory Cached (MB)'] = mem.cached / mb
    if(psutil.OSX or psutil.BSD):
        logger.info("Memory Wired {}MB".format(mem.wired / mb))
        res['Memory Wired (MB)'] = mem.wired / mb

    swap = psutil.swap_memory()
    logger.info('Swap Total: {}MB'.format(swap.total / mb))
    res['Swap Total (MB)'] = swap.total / mb
    logger.info('Swap Used: {}MB'.format(swap.used / mb))
    res['Swap Used (MB)'] = swap.used / mb
    logger.info('Swap Free: {}MB'.format(swap.free / mb))
    res['Swap (Free MB)'] = swap.free / mb
    logger.info('Swap Percent: {}'.format(swap.percent))
    res['Swap Percent'] = swap.percent
    if not psutil.WINDOWS:
        logger.info('Swap In: {}MB'.format(swap.sin / mb))
        res['Swap In (MB)'] = swap.sin / mb

        logger.info('Swaped Out: {}MB'.format(swap.sout / mb))
        res['Swaped Out (MB)'] = swap.sout / mb
    return res


def getMac():
    from uuid import getnode as get_mac
    # '0x' + 6bytes  = len 14
    return "{0:#0{1}x}".format(get_mac(), 14)


def getMacInfo():
    logger.info("MAC-Adress: {}".format(getMac()))
    return {"MAC-Adress": getMac()}


def getAllHostnames():
    if CDB_AVAILABLE:
        return usutil.gethostnames()
    else:
        import socket
        return [socket.gethostname()]

def getAllHostnamesInfo():
    logger.info("Hostnames: {}".format(getAllHostnames()))
    return {"Hostnames": getAllHostnames()}


def diskIOCounter():
    # Disk IO counter: sdiskio(read_count=3919547, write_count=1767118, read_bytes=84891013632L, write_bytes=137526756352L, read_time=355414861L, write_time=260233546L)
    res = {}
    diskcounters = psutil.disk_io_counters(perdisk=False)
    logger.info('Disk IO read (count): {}'.format(diskcounters.read_count))
    res['Disk IO read (count)'] = diskcounters.read_count
    logger.info('Disk IO write (count): {}'.format(diskcounters.write_count))
    res['Disk IO write (count)'] = diskcounters.write_count
    logger.info('Disk IO read (MB): {}'.format(diskcounters.read_bytes / 1024))
    res['Disk IO read (MB)'] = diskcounters.read_bytes
    logger.info('Disk IO write (MB): {}'.format(diskcounters.write_bytes / 1024))
    res['Disk IO write (MB)'] = diskcounters.write_bytes
    logger.info('Disk IO read (time): {}'.format(diskcounters.read_time))
    res['Disk IO read (time)'] = diskcounters.read_time
    logger.info('Disk IO write (time): {}'.format(diskcounters.write_time))
    res['Disk IO write (time)'] = diskcounters.write_time
    return res


def getSysInfo():
    """Get the general infos like time, OS etc.

    :returns: dict with the infos"""
    logger.info("Current Time (UTC): %s", datetime.datetime.utcnow().isoformat())
    logger.info("Current User: %s", getpass.getuser())
    logger.info("OS-Platform: %s", sys.platform)
    logger.info("OS-Platform Version: %s", platform.platform())
    logger.info("Processor: %s", platform.processor())
    res = {}
    res["Current Time (UTC)"] = datetime.datetime.utcnow().isoformat()
    res["Current User"] = getpass.getuser()
    res["OS-Platform"] = sys.platform
    res["OS-Platform Version"] = platform.platform()
    res["Processor"] = platform.processor()

    if CDB_AVAILABLE:
        logger.info("Elements Version: %s", version.getVersionDescription())
        res["Elements Version"] = version.getVersionDescription()

    return res


def getCPUInfo():
    res = {}
    cpu_times = psutil.cpu_times()
    logger.info("CPU Time (spent by processes in user mode): {}".format(cpu_times.user))
    res["CPU Time (spent by processes in user mode)"] = cpu_times.user
    logger.info("CPU Time (spent by processes in kernel mode): {}".format(cpu_times.system))
    res["CPU Time (spent by processes executing in kernel mode)"] = cpu_times.system
    logger.info("CPU Time (spent doing nothing): {}".format(cpu_times.idle))
    res["CPU Time (spent doing nothing)"] = cpu_times.idle

    logger.info('CPU Percent: {}'.format(psutil.cpu_percent(interval=1, percpu=False)))
    res['CPU Percent'] = psutil.cpu_percent(interval=1, percpu=False)

    cpu_time_percent = psutil.cpu_times_percent(interval=1.1, percpu=False)
    logger.info("CPU Time Percent (spent by processes in user mode): {}".format(cpu_time_percent.user))
    res["CPU Time Percent (spent by processes in user mode)"] = cpu_time_percent.user
    logger.info("CPU Time Percent (spent by processes in kernel mode): {}".format(cpu_time_percent.system))
    res["CPU Time Percent (spent by processes executing in kernel mode)"] = cpu_time_percent.system
    logger.info("CPU Time Percent (spent doing nothing): {}".format(cpu_time_percent.idle))
    res["CPU Time Percent (spent doing nothing)"] = cpu_time_percent.idle

    logger.info('CPU Count (locial CPUs): {}'.format(psutil.cpu_count()))
    res['CPU Count (locial CPUs)'] = psutil.cpu_count()
    logger.info('CPU Count (physical CPUs): {}'.format(psutil.cpu_count(logical=False)))
    res['CPU Count (physical CPUs)'] = psutil.cpu_count(logical=False)

    try:
        cpu_freq = psutil.cpu_freq(percpu=False).current
    except AttributeError:
        pass  # Used psutil version doesnt support that. Ignore.
    else:
        logger.info("CPU Frenquency: {}".format(cpu_freq))
        res['CPU Frenquency'] = cpu_freq

    return res


def getCADDOKINfos():
    """Looking for CADDOK enviroment variables.

    :returns: dict with the infos."""
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


def isVM():
    """Detect virtual mashines by their mac address.
    It is not completely sure that the running system is vm. These MAC are known
    for being used for VMs.

    :returns: True if a MAC was found. Otherwise False.
    """

    # list with macs
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


def VMInfo():
    logger.info("VM running?: (probably) {}".format("Yes" if isVM() else "No"))
    return {"VM running?: (probably) ": ("Yes" if isVM() else "No")}


def msinfo32():
    """Executes MSINFO32.exe on windows systems and saves the file. Reads the xml and filters useful informations.

    :returns: dict with infos
    """
    res = {}
    if(psutil.WINDOWS):
        import io
        import os
        import xml.etree.ElementTree as ElementTree
        from lxml import etree

        fileName = "msinfo32.xml"
        proc = subprocess.Popen(['msinfo32', "/nfo", fileName], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = proc.stdout.read()

        with io.open(fileName, encoding="UTF-16le") as fd:
            xml_string = fd.read().encode("utf-8", "ignore")

        root = etree.fromstring(xml_string)

        cat_list = [u'Systemübersicht', u'Datenträger']
        for cat in root.findall("Category"):
            if cat.get('name') in cat_list:
                for data in cat.findall("Data"):
                    res[data.find('Element').text] = data.find('Wert').text
                    logger.info("{}: {}".format(data.find('Element').text, data.find('Wert').text))
        os.unlink(fileName)
    return res


def traceroute(dest):
    """Executes tracert on windows and traceroute on linux systems.

    :returns: dict with infos."""

    import re

    m = re.search("\/\/(.*):", dest)
    if m is None:
        dest = "localhost"
    else:
        dest = m.group(1)
    if(psutil.WINDOWS):
        # find encoding
        import encodingService
        cp = encodingService.guess_console_encoding()

        output = subprocess.check_output(["tracert", "-w", "100", dest], stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = output.decode(cp).replace("\r\n", "")

        # shorten en/de tracert msg
        regex = '.*(Routenverfolgung\szu|Tracing\sroute\sto)\s(.*?\[.*?\]).*?:(.*)'
        m = re.match(regex, output)
        if m is not None:
            server = m.group(2)
            route = m.group(3)
            logger.info("Route to server: {} - {}".format(server, route))
            tracertString = "{}: {}".format(server, route)
            return {"Route to server:": tracertString}
    elif(psutil.POSIX):
        # traceroute to google.com (172.217.23.14),
        output = subprocess.check_output(["traceroute", "-w", "100", dest], stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = output.replace("\n", "")

        # shorten traceroute msg
        regex = '.*(traceroute\sto)\s(.*?\(.*?\)).*?packets(.*)'
        m = re.match(regex, output)
        if m is not None:
            server = m.group(2)
            route = m.group(3)
            logger.info("Route to server: {} - {}".format(server, route))
            tracertString = "{}: {}".format(server, route)
            return {"Route to server:": tracertString}
    else:
        return {}


def getAllSysInfos():
    """Collects all system infos and returns a dict.

    :returns: dict with all system infos."""

    logger.info("SYSINFOS:\n")
    res = {}
    res.update(getSysInfo())
    if CDB_AVAILABLE:
        res.update(getCADDOKINfos())
    res.update(getCPUInfo())
    if 'CADDOK_SERVER' in res:
        res.update(traceroute(res['CADDOK_SERVER']))
    res.update(VMInfo())
    res.update(getAllHostnamesInfo())
    res.update(getMacInfo())
    res.update(getMemoryInfos())
    res.update(diskIOCounter())
    res.update(msinfo32())
    return res
