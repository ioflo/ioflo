""" support for ioflo CLI """
#print "\Module at%s" % __path__[0]

import argparse

from ..base import skedding, consoling

def parseArgs():
    """ Parse command line arguments"""
    
    d = "Runs ioflo. "
    d += "Example: ioflo -f filename -p period -v level -r -h -b 'mybehaviors.py'\n"
    p = argparse.ArgumentParser(description = d)
    p.add_argument('-v','--verbose',
            action='store', 
            default='concise',
            choices=['0', '1', '2', '3', '4'].extend(consoling.VERBIAGE_NAMES),
            help="Verbosity level.")
    p.add_argument('-p','--period',
            action='store',
            default='0.125',
            help="Period per skedder run in seconds.")
    p.add_argument('-r','--realtime',
            action='store_const',
            const=True, 
            default=False,
            help="Run skedder at realtime.")
    p.add_argument('-V','--version',
            action='store_const',
            const=True, 
            default=False,
            help="Prints out version of ioflo.")    
    p.add_argument('-n','--name',
            action='store', 
            default='Skedder',
            help="Skedder name.")    
    p.add_argument('-f','--filename',
            action='store',
            default='../plan/box1.flo',
            help="File path to FloScript file.")
    p.add_argument('-b','--behaviors',
            action='store',
            nargs='*', 
            default=None,
            help="Module name strings to external behavior packages.")
    p.add_argument('-U','--username',
            action='store',
            default='',
            help="Username.")
    p.add_argument('-P','--password',
            action='store',
            default='',
            help="Password.")
    args = p.parse_args()
    
    if args.verbose in consoling.VERBIAGE_NAMES:
        verbosage = consoling.VERBIAGE_NAMES.index(args.verbose)
    else:
        verbosage = int(args.verbose)

    console = consoling.getConsole(verbosity=consoling.Console.Wordage[verbosage])
    console.profuse( "ioflo arguments: \n{0}".format(args))    
    args.verbose = verbosage #converted value
    return args

def run(    name="Skedder", 
            filename="../plan/box1.flo",
            period=0.2,
            realtime=False, 
            verbose=0,
            behaviors=None,
            username="",
            password="", 
            profiling = False):
    """ Run Skedder"""
    console = consoling.getConsole(verbosity=consoling.Console.Wordage[verbose])
    console.terse( "\n----------------------\n")
    console.terse( "Building ...\n")
    
    skedder = skedding.Skedder(name=name,
                               period=period,
                               real=realtime, 
                               filePath=filename,
                               behaviors=behaviors,
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
    else:
        console.terse( "\n\n**********************************\n")
        console.terse( "Failure building mission from file:\n{0}\n".format(filename))
        console.terse( "************************************\n\n")

    console.terse( "\n----------------------\n")
    return skedder

Run = run # alias for backwards compat