# -*- coding: utf-8 -*-
"""
http  io test package

To run all the unittests:

from ioflo import test
test.run()

"""
import sys
import unittest
import os

from ioflo import test
from ioflo.aid.consoling import getConsole
console = getConsole()
console.reinit(verbosity=console.Wordage.concise)

top = os.path.dirname(os.path.abspath(sys.modules.get(__name__).__file__))

if __name__ == "__main__":
    test.run(top)
