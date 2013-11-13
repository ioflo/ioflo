""" app run package"""
#print "\nPackage at%s" % __path__[0]

from ...base.globaling import *
from ...base.consoling import getConsole, Console

def Run( fileName = None,
         period = 0.2,
         real = False, 
         verbose = 0,
         profiling = False):
    """ Run once"""

    console = getConsole(verbosity=Console.Wordage[verbose])

    from ...base import skedding

    if not fileName:
        fileName = "../plan/box1.flo"


    console.terse( "Building ...")
    skedder = skedding.Skedder(name = "TestSkedder",
                               period = period,
                               real = real, 
                               filePath = fileName)
    if skedder.build():
        console.terse( "\n\nStarting mission from file {0}...\n".format(fileName))
        if not profiling:
            skedder.run()
        else:
            import cProfile
            import pstats

            cProfile.runctx('skedder.run()',globals(),locals(), './profiles/skedder')
            p = pstats.Stats('./profiles/skedder')
            p.sort_stats('time').print_stats()
            p.print_callers()
            p.print_callees()


    return skedder