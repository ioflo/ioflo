# -*- coding: utf-8 -*-
"""
ioflo
base test package

To run all the unittests:

from ioflo.base import test
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

def run(start="."):
    '''
    Run unittests starting at directory given by start
    Default start is the location of the ioflo.base package
    '''
    if __name__ == '__main__':
        top = os.path.dirname(os.getcwd())
    else:
        top = os.path.dirname(os.path.dirname(os.path.abspath(
            sys.modules.get(__name__).__file__)))

    console.terse("\nRunning all ioflo.base tests in '{0}', starting at '{1}'\n".format(top, start))
    loader = unittest.TestLoader()
    suite = loader.discover(start, 'test*.py', top )
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    run()
