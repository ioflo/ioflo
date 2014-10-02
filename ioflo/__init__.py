""" ioflo package

"""
from __future__ import division

import importlib

__version__ = "1.0.0"
__author__ = "Samuel M. Smith"
__license__ =  "Apache 2.0"


__all__ = ['base', 'trim']

for m in __all__:
    importlib.import_module(".{0}".format(m), package='ioflo')

