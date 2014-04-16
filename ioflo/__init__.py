""" ioflo package

"""
#print("\nPackage at {0}".format( __path__[0]))

from __future__ import division

import importlib

__version__ = "0.9.30"
__author__ = "Samuel M. Smith"
__license__ =  "MIT"


#from .base.consoling import getConsole
#console = getConsole()
#console.profuse("{0} version {1}\n".format(__path__[0], __version__))

__all__ = ['base', 'trim']

for m in __all__:
    importlib.import_module(".{0}".format(m), package='ioflo')

