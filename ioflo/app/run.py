""" support for ioflo CLI """
#print("\Module at%s" % __path__[0])

import argparse
import os

from ..__metadata__ import __version__
from ..aid import  consoling
from ..base import skedding


def parseArgs(version=__version__):
    """
    Parse command line arguments

    version parameter defaults to ioflo version
    allows different version if parseArgs is embedded in another script

    """

    d = "Runs ioflo. "
    d += "Example: ioflo -f filename -p period -v level -r -h -b 'mybehaviors.py'\n"
    p = argparse.ArgumentParser(description=d)
    p.add_argument('-V', '--version',
            action='version',
            version=version,
            help="Prints out version of ioflo script runner.")
    p.add_argument('-v', '--verbose',
            action='store',
            default='concise',
            choices=['0', '1', '2', '3', '4'].extend(consoling.VERBIAGE_NAMES),
            help="Verbosity level.")
    p.add_argument('-c', '--console',
            action='store',
            default='',
            help="File path name to console log file.")
    p.add_argument('-p', '--period',
            action='store',
            default='0.125',
            help="Period per skedder run in seconds.")
    p.add_argument('-r', '--realtime',
            action='store_const',
            const=True,
            default=False,
            help="Run skedder at realtime.")
    p.add_argument('-R', '--retrograde',
            action='store_const',
            const=True,
            default=True,
            help="Shift skedder timers when retrograde clock detected.")
    p.add_argument('-n', '--name',
            action='store',
            default='skedder',
            help="Skedder name.")
    p.add_argument('-f', '--filename',
            action='store',
            required=True,
            help="File path to FloScript file.")
    p.add_argument('-b', '--behaviors',
            action='store',
            nargs='*',
            default=None,
            help="Module name strings to external behavior packages.")
    p.add_argument('-m', '--parsemode',
            action='store',
            default='',
            help="FloScript parsing mode.")
    p.add_argument('-U', '--username',
            action='store',
            default='',
            help="Username.")
    p.add_argument('-P', '--password',
            action='store',
            default='',
            help="Password.")
    p.add_argument('-S', '--statistics',
            action='store',
            nargs='?',
            const=True,
            default=False,
            help=("Profile and compute performance statistics. "
            "Put statistics into file path given by optional argument. "
            "Default statistics file path is /tmp/ioflo/profile/NAME. "))
    args = p.parse_args()

    if args.verbose in consoling.VERBIAGE_NAMES:
        verbosage = consoling.VERBIAGE_NAMES.index(args.verbose)
    else:
        verbosage = int(args.verbose)

    console = consoling.getConsole(verbosity=consoling.Console.Wordage[verbosage],
                                   path=args.console)
    console.profuse('ioflo arguments: \n{0}'.format(args))
    args.verbose = verbosage  # converted value
    return args


def run(name="skedder",
        period=0.1,
        real=False,
        retro=True,
        stamp=0.0,
        filepath="",
        behaviors=None,
        mode=None,
        username="",
        password="",
        verbose=0,
        consolepath="",
        statistics="",
        houses=None,
        metas=None,
        preloads=None,        ):
    """ Run Skedder"""
    console = consoling.getConsole(verbosity=consoling.Console.Wordage[verbose],
                                   path=consolepath)
    console.terse("\n----------------------\n")
    console.terse("Building Skeddar '{0}' ...\n".format(name))

    skedder = skedding.Skedder(name=name,
                               period=period,
                               real=real,
                               retro=retro,
                               stamp=stamp,
                               filepath=filepath,
                               behaviors=behaviors,
                               mode=mode,
                               username=username,
                               password=password,
                               houses=houses,
                               metas=metas,
                               preloads=preloads)
    if skedder.build():
        console.terse("\n----------------------\n")
        console.terse("Starting mission plan '{0}' from file:\n    {1}\n".format(
                skedder.plan, skedder.filepath))
        if not statistics:
            skedder.run()
        else:
            import cProfile
            import pstats
            if isinstance(statistics, bool):  # use default
                statistics = os.path.join('/tmp', 'ioflo', 'profiles', 'name')
            try:
                statfilepath = os.path.abspath(os.path.expanduser(statistics))
                if not os.path.exists(statfilepath):
                    os.makedirs(os.path.dirname(statfilepath))
            except OSError as ex:
                console.terse("Error: creating server profile statistics file"
                              " '{0}'\n{1}'\n".format(statfilepath, ex))
                raise

            cProfile.runctx('skedder.run()', globals(), locals(), statfilepath)
            p = pstats.Stats(statfilepath)
            p.sort_stats('time').print_stats()
            p.print_callers()
            p.print_callees()
    else:
        console.terse("\n\n**********************************\n")
        console.terse("Failure building mission from file:\n{0}\n".format(
                skedder.filepath))
        console.terse("************************************\n\n")

    console.terse("\n----------------------\n")
    return skedder

Run = run  # alias for backwards compat
start = run  # alias for backwards compat
