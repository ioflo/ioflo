# -*- coding: utf-8 -*-
"""
tcp io  test package

To run all the unittests:

from ioflo import test
test.run()

"""
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import os

from ioflo import test
from ioflo.aid.consoling import getConsole
console = getConsole()
console.reinit(verbosity=console.Wordage.concise)

top = os.path.dirname(os.path.abspath(sys.modules.get(__name__).__file__))

if __name__ == "__main__":
    test.run(top)
