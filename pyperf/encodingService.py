#!/usr/bin/env python
# -*- mode: python; coding: iso-8859-1 -*-
#
# Copyright (C) 1990 - 2017 CONTACT Software GmbH
# All rights reserved.
# http://www.contact.de/
#
"""
Detect the console encoding in use on the machine based on Windows APIs
or POSIX locale environment variables.
"""
import codecs
import sys


def guess_console_encoding():
    """
    Try a best guess at the console encoding
    to use for output to stdout/stderr.
    """
    if sys.platform == "win32":
        cp = _WinCtypesGetOutputCP()
        if not cp:
            cp = _WinGetOutputCP()
        if not cp:
            cp = _WinRegistryGetCP()
        if not cp:
            cp = _WinJustGuess()
    else:
        cp = _UnixJustGuess()

    return cp


def encoding_exists(name):
    """
    Test if an encoding name is valid and available to python
    """
    try:
        codecs.lookup(name)
    except LookupError:
        return False
    return True

###############################################################################
#
# Guessing the console encoding for Windows
#
###############################################################################


def _WinGetOutputCP():
    """Get the codepage via win32 module"""
    try:
        import win32console
    except ImportError:
        return None
    try:
        cp = win32console.GetConsoleOutputCP()
    except Exception:
        return None
    name = "cp%d" % int(cp)
    if encoding_exists(name):
        return name
    else:
        return None


def _WinCtypesGetOutputCP():
    """Get the codepage via ctypes"""
    try:
        import ctypes
    except ImportError:
        return None
    try:
        cp = ctypes.windll.kernel32.GetConsoleOutputCP()
    except Exception:
        return None
    name = "cp%d" % int(cp)
    if encoding_exists(name):
        return name
    else:
        return None


def _WinRegistryGetCP():
    """Look into the registry"""
    # The codepage for the console can be found in
    # HKLM\SYSTEM\CurrentControlSet\Control\Nls\CodePage
    # The needed key is OEMCP

    try:
        import _winreg as wreg
    except ImportError:
        return None

    keyname = r"SYSTEM\CurrentControlSet\Control\Nls\CodePage"
    try:
        key = wreg.OpenKey(wreg.HKEY_LOCAL_MACHINE, keyname)
        cp, _t = wreg.QueryValueEx(key, "OEMCP")
        wreg.CloseKey(key)
    except Exception:
        return None
    name = "cp%s" % (cp)
    if encoding_exists(name):
        return name
    else:
        return None


def _WinJustGuess():
    return "cp850"


def _UnixJustGuess():
    return 'utf-8'
