# -*- coding: utf-8 -*-
"""
ioflo test package

To run all the unittests:

from ioflo import test
test.run()

"""
#print("\nPackage at {0}".format( __path__[0]))

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import os


from ioflo.base.consoling import getConsole
console = getConsole()
console.reinit(verbosity=console.Wordage.concise)

def run(start=None):
    """
    Run unittests starting at directory given by start
    Default start is the location of the ioflo.base package
    """
    top = os.path.dirname(os.path.dirname(os.path.abspath(
    sys.modules.get(__name__).__file__)))

    if not start:
        start = os.path.join(top, "base")

    console.terse("\nRunning ioflo tests starting at '{0}' from '{1}', \n".format(start, top))
    loader = unittest.TestLoader()
    suite = loader.discover(start, 'test_*.py', top )
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    run()
