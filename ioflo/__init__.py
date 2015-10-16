""" ioflo package

"""
from __future__ import division

import importlib

_modules = ['base', 'trim']  # register behaviors

for m in _modules:
    importlib.import_module(".{0}".format(m), package='ioflo')

from .__metadata__ import *

