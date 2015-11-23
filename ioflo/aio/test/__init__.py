# -*- coding: utf-8 -*-
"""
ioflo.aio asynchronous io  test package

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

#top = os.path.dirname(os.path.abspath(sys.modules.get(__name__).__file__))
start = os.path.dirname(os.path.dirname
                      (os.path.abspath
                       (sys.modules.get(__name__).__file__)))

# need top to be above root for relative imports to not go above top level
top = os.path.dirname(os.path.dirname(start))

if __name__ == "__main__":
    test.run(top, start)
