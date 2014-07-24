"""testing.py unit test module


"""
#print("module {0}".format(__name__))

import time
import struct
import argparse


def Run(fileName = None, period = 0.2, real = False,
        verbose = 0, profiling = False):
    """Run once """

    import ioflo.base.skedding as skedding

    if not fileName:
        fileName = "../../app/plan/meta.flo"


    print("Building ...")
    skedder = tasking.Skedder(name = "TestTasker",
                              period = period,
                              real = real,
                              filepath = fileName)
    if skedder.build():
        print("\n\nStarting mission from file %s...\n" % (fileName))
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


if __name__ == "__main__":
    import sys
    import getopt


    sys.stderr.write(str(sys.argv) + "\n") #joins list items with space separator

    filename = '../../app/plan/meta.flo'
    period = 0.125
    verbose = 0
    real = False

    usage = "python testmeta.py -f filename -p period -v level -r -h"


    try:
        (opts, pargs) = getopt.getopt(sys.argv[1:], "hrv:f:p:") #format
    except getopt.GetoptError:
        #print help info and exit
        sys.stderr.write(str(opts) + "usage\n") #joins list items with space separator

        print(usage)

        sys.exit(2)


    sys.stderr.write(str(opts) + "\n") #joins list items with space separator

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
            print(usage)
            help = True

    if not help:
        print("fileName = %s, period = %0.3f verbose = %d real = %s" %\
              (filename, period, verbose, real))
        Run(fileName = filename, period = period, verbose = verbose, real = real)
