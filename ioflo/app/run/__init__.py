""" app run package"""
#print "\nPackage at%s" % __path__[0]

from ...base.globaling import *
from ...base.consoling import getConsole, Console

def Run(    name="Skedder", 
            filename="../plan/box1.flo",
            period=0.2,
            realtime=False, 
            verbose=0,
            behavior="",
            username="",
            password="", 
            profiling = False):
    """ Run Skedder"""
    console = getConsole(verbosity=Console.Wordage[verbose])
    console.terse( "Building ...")
    
    from ...base import skedding
    skedder = skedding.Skedder(name=name,
                               period=period,
                               real=realtime, 
                               filePath=filename,
                               behavior=behavior,
                               username=username,
                               password=password, )
    if skedder.build():
        console.terse( "\n\nStarting mission from file {0}...\n".format(filename))
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