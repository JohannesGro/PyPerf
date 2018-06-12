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
import platform
import subprocess
import sys
import os
import psutil

cdb = None
try:
    import cdb
    from cdb import version  # noqa
    from cdb import rte  # noqa
    from cdb.uberserver import usutil  # noqa
except ImportError:
    pass


logger = logging.getLogger("[Sysinfos]")


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


def getMemoryInfos(verbose=True):
    # working for windows only
    mb = 1024 * 1024
    res = {}
    mem = psutil.virtual_memory()
    res['mem_total'] = mem.total / mb
    res['mem_percent'] = mem.percent

    if verbose:
        if psutil.WINDOWS:
            stat = MEMORYSTATUSEX()
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            res['mem_total_virtual'] = stat.ullTotalVirtual / mb

        res['mem_used'] = mem.used / mb
        res['mem_free'] = mem.free / mb
        res['mem_available'] = mem.available / mb
        if psutil.POSIX:
            res['mem_active'] = mem.active / mb
            res['mem_inactive'] = mem.inactive / mb

        if(psutil.POSIX or psutil.BSD):
            res['mem_buffers'] = mem.buffers / mb
            res['mem_shared'] = mem.shared / mb
            res['mem_cached'] = mem.cached / mb
        if(psutil.OSX or psutil.BSD):
            res['mem_wired'] = mem.wired / mb

    if verbose:
        swap = psutil.swap_memory()
        res['swap_total'] = swap.total / mb
        res['swap_used'] = swap.used / mb
        res['swap_free'] = swap.free / mb
        res['swap_percent'] = swap.percent
        if not psutil.WINDOWS:
            res['swapped_in'] = swap.sin / mb
            res['swapped_out'] = swap.sout / mb
    return res


def getMac():
    from uuid import getnode as get_mac
    # '0x' + 6bytes  = len 14
    return "{0:#0{1}x}".format(get_mac(), 14)


def getMacInfo():
    return {"mac_adress": getMac()}


def getAllHostnamesInfo(verbose=True):
    hostnames = cdb.uberserver.usutil.gethostnames() if cdb and verbose else [platform.node()]
    return {"hostnames": hostnames}


def diskIOCounter():
    # Disk IO counter: sdiskio(read_count=3919547, write_count=1767118, read_bytes=84891013632L,
    # write_bytes=137526756352L, read_time=355414861L, write_time=260233546L)
    res = {}
    diskcounters = psutil.disk_io_counters(perdisk=False)
    if diskcounters:
        res['io_read_count'] = diskcounters.read_count
        res['io_write_count'] = diskcounters.write_count
        res['io_read_mb'] = diskcounters.read_bytes
        res['io_write_mb'] = diskcounters.write_bytes
        res['io_read_time'] = diskcounters.read_time
        res['io_write_time'] = diskcounters.write_time
    return res


def getSysInfo():
    """Get the general infos like time, OS etc.

    :returns: dict with the infos"""
    res = {}
    res["time"] = datetime.datetime.utcnow().isoformat()
    res["user"] = getpass.getuser()
    res["os"] = sys.platform
    res["os_version"] = platform.platform()
    res["cpu"] = platform.processor()
    if cdb:
        res["ce_version"] = cdb.version.getVersionDescription()

    return res


def getCPUInfo(verbose=True):
    res = {}

    # 1. CPU utilisation by mode (user, system, idle).
    #    TODO: platform specific modes (irq, softirq etc.) would probably be useful too.
    if verbose:
        cpu_times = psutil.cpu_times()
        res["cpu_user"] = cpu_times.user
        res["cpu_system"] = cpu_times.system
        res["cpu_idle"] = cpu_times.idle

        cpu_percent = psutil.cpu_percent(interval=0.5, percpu=False)
        res['cpu_percent'] = cpu_percent

        cpu_time_percent = psutil.cpu_times_percent(interval=0.5, percpu=False)
        res["cpu_load_user"] = cpu_time_percent.user
        res["cpu_load_system"] = cpu_time_percent.system
        res["cpu_load_idle"] = cpu_time_percent.idle

    # 2. CPU core counts
    cores_logical = psutil.cpu_count()
    cores_physical = psutil.cpu_count(logical=False)
    res['cpu_cores_logical'] = cores_logical
    res['cpu_cores_physical'] = cores_physical

    # 3. Current CPU frequency
    if hasattr(psutil, "cpu_freq"):
        cpu_freq_curr = psutil.cpu_freq(percpu=False).current
        res['cpu_frequency'] = cpu_freq_curr

    return res


def getCADDOKInfos():
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
        environ = cdb.rte.environ if cdb else os.environ
        if var in environ:
            res[var] = environ[var]
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
    prefix = ['0x000569', '0x000c29', '0x001c14', '0x005056', "0x0003ff",
              "0x001c42", "0x000f4b", "0x00163e", "0x080027"]

    mac = getMac()
    for str in prefix:
        if str in mac:
            return True
    return False


def VMInfo():
    return {"vm": ("Yes" if isVM() else "No")}


def msinfo32():
    """Executes MSINFO32.exe on windows systems and saves the file. Reads the xml and filters useful informations.

    :returns: dict with infos
    """
    res = {}
    if psutil.WINDOWS:
        import io
        from lxml import etree

        fileName = "msinfo32.xml"
        subprocess.check_call(['msinfo32', "/nfo", fileName],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        with io.open(fileName, encoding="UTF-16le") as fd:
            xml_string = fd.read().encode("utf-8", "ignore")

        root = etree.fromstring(xml_string)

        cat_list = ['Systemübersicht', 'Datenträger']
        for cat in root.findall("Category"):
            if cat.get('name') in cat_list:
                for data in cat.findall("Data"):
                    res[data.find('Element').text] = data.find('Wert').text
        os.unlink(fileName)
    return res


def traceroute(dest):
    """Executes tracert on windows and traceroute on linux systems.

    :returns: dict with infos."""

    import re

    m = re.search(r"\/\/(.*):", dest)
    if m is None:
        dest = "localhost"
    else:
        dest = m.group(1)
    if psutil.WINDOWS:
        # find encoding
        from . import encodingService
        cp = encodingService.guess_console_encoding()

        output = subprocess.check_output(["tracert", "-w", "100", dest],
                                         stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = output.decode(cp).replace("\r\n", "")

        # shorten en/de tracert msg
        regex = r".*(Routenverfolgung\szu|Tracing\sroute\sto)\s(.*?\[.*?\]).*?:(.*)"
        m = re.match(regex, output)
        if m is not None:
            server = m.group(2)
            route = m.group(3)
            tracertString = "{}: {}".format(server, route)
            return {"route": tracertString}
    elif psutil.POSIX:
        # traceroute to google.com (172.217.23.14),
        output = subprocess.check_output(["traceroute", "-w", "100", dest],
                                         stdin=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = output.replace("\n", "")

        # shorten traceroute msg
        regex = r".*(traceroute\sto)\s(.*?\(.*?\)).*?packets(.*)"
        m = re.match(regex, output)
        if m is not None:
            server = m.group(2)
            route = m.group(3)
            tracertString = "{}: {}".format(server, route)
            return {"route": tracertString}
    else:
        return {}


def getAllSysInfos(verbose=True):
    """Collects all system infos and returns a dict.

    :param verbose: 'True' for gathering more/deeper sysinfos, 'False' otherwise.
    :returns: dict with all system infos."""

    logger.info("Fetching system infos (verbose: %s, CONTACT Elements available: %s)",
                verbose, cdb is not None)

    res = {}
    res.update(getSysInfo())
    res.update(getCADDOKInfos())
    res.update(getCPUInfo(verbose))
    res.update(VMInfo())
    res.update(getAllHostnamesInfo(verbose))
    res.update(getMemoryInfos(verbose))
    if verbose:
        if 'CADDOK_SERVER' in res:
            res.update(traceroute(res['CADDOK_SERVER']))
        res.update(diskIOCounter())
        res.update(getMacInfo())
        res.update(msinfo32())

    return res
