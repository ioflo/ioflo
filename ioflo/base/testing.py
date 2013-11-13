"""testing.py unit test module


"""
#print "module %s" % __name__


import cProfile
import pstats
import time
import struct


from .globaling import *
from .consoling import getConsole


def Test(fileName = None, period = 0.2, real = False, 
         verbose = 0, profiling = False):
    """Module self test

    """
    console = getConsole(verbosity=console.Wordage[verbose])

    import building
    import tasking

    if not fileName:
        fileName = "../plan/box1.flo"

    console.terse( "Building ...")
    skedder = tasking.Skedder(name = "TestSkedder",
                              period = period,
                              real = real, 
                              filePath = fileName)
    if skedder.build():
        console.terse( "\n\nStarting mission from file 0}...\n".format(fileName))
        if not profiling:
            skedder.run()
        else:
            cProfile.runctx('skedder.run()',globals(),locals(), './profiles/skedder')

            p = pstats.Stats('./profiles/skedder')
            p.sort_stats('time').print_stats()
            p.print_callers()
            p.print_callees()


    return skedder


if __name__ == "__main__":
    import sys
    import getopt

    from ioflo.base.consoling import getConsole

    console = getConsole(verbosity=console.Wordage.profuse)
    console.profuse(str(sys.argv) + "\n")

    filename = '../plan/box1.flo'
    period = 0.125
    verbose = 0
    real = False

    usage = "python wradia/testing.py -f filename -p period -v level -r -h"

    try:
        (opts, pargs) = getopt.getopt(sys.argv[1:], "hrv:f:p:") #format 
    except getopt.GetoptError:
        console.profuse(str(opts) + "usage\n")
        console.concise( usage)

        sys.exit(2)

    console.profuse(str(opts) + "\n")

    help = False

    if not opts:
        opts.append(('-h',''))

    for x in opts:
        if x[0] == '-f':  
            filename = x[1]
        if x[0] == '-p':
            period = float(x[1])
        if x[0] == '-v':
            verbose = int(x[1])
        if x[0] == '-r':
            real = True
        if x[0] == '-h':
            print usage
            help = True

    if not help:
        msg = "fileName = {0}, period = {1:0.3f} verbose = {2:d} real = {3}".format(
            filename, period, verbose, real)
        console.profuse(msg)

        Test(fileName = filename, period = period, verbose = verbose, real = real)

