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
from .globaling import *
from .odicting import odict
from . import excepting

from .consoling import getConsole
console = getConsole()

