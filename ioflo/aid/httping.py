"""
httping.py

nonblocking http classes
"""
#print("module {0}".format(__name__))

from __future__ import division


import sys
import os
import socket
import errno
from collections import deque

try:
    import win32file
except ImportError:
    pass

# Import ioflo libs
from ..base.globaling import *
from ..base.odicting import odict
from ..base import excepting

from ..base.consoling import getConsole
console = getConsole()


