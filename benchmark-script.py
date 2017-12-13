#!c:\ce\trunk\win32\debug\img\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'benchmarktool','console_scripts','benchmark'
__requires__ = 'benchmarktool'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('benchmarktool', 'console_scripts', 'benchmark')()
    )
