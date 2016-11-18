"""building.py build frameworks from mission files

"""
from __future__ import division

#print("module {0}".format(__name__))

import time
import re
import importlib
import os

from collections import deque
try:
    from itertools import izip
except ImportError: #python 3 zip is same as izip
    izip = zip

from ..aid.sixing import *
from ..aid.odicting import odict
from .globaling import *

from . import excepting
from . import registering

from . import storing
from . import housing

from . import acting
from . import poking
from . import needing
from . import goaling
from . import doing

from . import traiting
from . import fiating
from . import wanting
from . import completing

from . import tasking
from . import framing
from . import logging
from . import serving

from .. import trim

from ..aid.consoling import getConsole
console = getConsole()

from ..trim import exterior

def Convert2Num(text):
    """converts text to python type in order
       Int, hex, Float, Complex
       ValueError if can't
    """
    #convert to number if possible
    try:
        value = int(text, 10)
        return value
    except ValueError as ex:
        pass

    try:
        value = int(text, 16)
        return value
    except ValueError as ex:
        pass

    try:
        value = float(text)
        return value
    except ValueError as ex:
        pass

    try:
        value = complex(text)
        return value
    except ValueError as ex:
        pass

    raise ValueError("Expected Number got '{0}'".format(text))
    # return None

def Convert2CoordNum(text):
    """converts text to python type in order
       FracDeg, Int, hex, Float, Complex
       ValueError if can't
    """
    #convert to FracDeg Coord if possible
    dm = REO_LatLonNE.findall(text) #returns list of tuples of groups [(deg,min)]
    if dm:
        deg = float(dm[0][0])
        min_ = float(dm[0][1])
        return (deg + min_/60.0)

    dm = REO_LatLonSW.findall(text) #returns list of tuples of groups [(deg,min)]
    if dm:
        deg = float(dm[0][0])
        min_ = float(dm[0][1])
        return (-(deg + min_/60.0))

    try:
        return (Convert2Num(text))
    except ValueError:
        raise ValueError("Expected CoordPointNum got '{0}'".format(text))

def Convert2BoolCoordNum(text):
    """converts text to python type in order
       None, Boolean, Int, Float, Complex
       ValueError if can't
    """
    #convert to None if possible
    if text.lower() == 'none':
        return None

    #convert to boolean if possible
    if text.lower() in ['true', 'yes']:
        return (True)
    if text.lower() in ['false', 'no']:
        return (False)

    try:
        return (Convert2CoordNum(text))
    except ValueError:
        raise ValueError("Expected BoolCoordPointNum got '{0}'".format(text))

    return None

def Convert2StrBoolCoordNum(text):
    """converts text to python type in order
       Boolean, Int, Float, complex or double quoted string
       ValueError if can't

       Need goal wants unitary type not path or point
    """

    if REO_Quoted.match(text): #text is double quoted string
        return text.strip('"')  #strip off quotes

    if REO_QuotedSingle.match(text): #text is single quoted string
        return text.strip("'")  #strip off quotes

    try:
        return (Convert2BoolCoordNum(text))
    except ValueError:
        raise ValueError("Expected StrBoolCoordNum got '{0}'".format(text))

    return None

def Convert2PointNum(text):
    """
    Converts text to python type in order
       Pxy, Pne,Pfs,Pxyz,Pned,Pfsb, Int, hex, Float, Complex
       ValueError if can't
    """
    # convert to on of the Point classes if possible
    match = REO_PointXY.findall(text)
    if match:
        x, y = match[0]
        return Pxy(x=float(x), y=float(y))

    match = REO_PointNE.findall(text)
    if match:
        n, e = match[0]
        return Pne(n=float(n), e=float(e))

    match = REO_PointFS.findall(text)
    if match:
        f, s = match[0]
        return Pfs(f=float(f), s=float(s))

    match = REO_PointXYZ.findall(text)
    if match:
        x, y, z = match[0]
        return Pxyz(x=float(x), y=float(y), z=float(z))

    match = REO_PointNED.findall(text)
    if match:
        n, e, d = match[0]
        return Pned(n=float(n), e=float(e), d=float(d))

    match = REO_PointFSB.findall(text)
    if match:
        f, s, b = match[0]
        return Pfsb(f=float(f), s=float(s), b=float(b))

    try:
        return (Convert2Num(text))
    except ValueError:
        raise ValueError("Expected PointNum got '{0}'".format(text))

def Convert2CoordPointNum(text):
    """converts text to python type in order
       FracDeg, Int, hex, Float, Complex
       ValueError if can't
    """
    #convert to FracDeg Coord if possible
    dm = REO_LatLonNE.findall(text) #returns list of tuples of groups [(deg,min)]
    if dm:
        deg = float(dm[0][0])
        min_ = float(dm[0][1])
        return (deg + min_/60.0)

    dm = REO_LatLonSW.findall(text) #returns list of tuples of groups [(deg,min)]
    if dm:
        deg = float(dm[0][0])
        min_ = float(dm[0][1])
        return (-(deg + min_/60.0))

    try:
        return (Convert2PointNum(text))
    except ValueError:
        raise ValueError("Expected CoordPointNum got '{0}'".format(text))

def Convert2BoolCoordPointNum(text):
    """converts text to python type in order
       None, Boolean, Int, Float, Complex
       ValueError if can't
    """
    #convert to None if possible
    if text.lower() == 'none':
        return None

    #convert to boolean if possible
    if text.lower() in ['true', 'yes']:
        return (True)
    if text.lower() in ['false', 'no']:
        return (False)

    try:
        return (Convert2CoordPointNum(text))
    except ValueError:
        raise ValueError("Expected BoolCoordPointNum got '{0}'".format(text))

    return None

def Convert2PathCoordPointNum(text):
    """converts text to python type in order
       Boolean, Int, Float, Complex
       ValueError if can't
    """
    #convert to path string if possible
    if REO_PathNode.match(text):
        return (text)

    try:
        return (Convert2CoordPointNum(text))
    except ValueError:
        raise ValueError("Expected PathCoordPointNum got '{0}'".format(text))

    return None

def Convert2BoolPathCoordPointNum(text):
    """converts text to python type in order
       Boolean, Int, Float, Complex
       ValueError if can't
    """
    #convert to None if possible
    if text.lower() == 'none':
        return None

    #convert to boolean if possible
    if text.lower() in ['true', 'yes']:
        return (True)
    if text.lower() in ['false', 'no']:
        return (False)

    try:
        return (Convert2PathCoordPointNum(text))
    except ValueError:
        raise ValueError("Expected PathBoolCoordPointNum got '{0}'".format(text))

    return None

def Convert2StrBoolPathCoordPointNum(text):
    """converts text to python type in order
       Boolean, Int, Float, complex or double quoted string
       ValueError if can't
    """

    if REO_Quoted.match(text): #text is double quoted string
        return text.strip('"')  #strip off quotes

    if REO_QuotedSingle.match(text): #text is single quoted string
        return text.strip("'")  #strip off quotes

    try:
        return (Convert2BoolPathCoordPointNum(text))
    except ValueError:
        raise ValueError("Expected StrBoolPathCoordPointNum got '{0}'".format(text))

    return None

def StripQuotes(text):
    """
    Returns text with leading and following quotes (singe or double) stripped
    off if any Otherwise return as is
    """

    if REO_Quoted.match(text): #text is double quoted string
        return text.strip('"')  #strip off quotes

    if REO_QuotedSingle.match(text): #text is single quoted string
        return text.strip("'")  #strip off quotes

    return text

VerbList = ['load', 'house', 'init',
               'server',
               'logger', 'log', 'loggee',
               'framer', 'first',
               'frame', 'over', 'under', 'next', 'done', 'timeout', 'repeat',
               'native', 'benter', 'enter', 'recur', 'exit', 'precur', 'renter', 'rexit',
               'print', 'put', 'inc', 'copy', 'set',
               'aux', 'rear', 'raze',
               'go', 'let',
               'do',
               'bid', 'ready', 'start', 'stop', 'run', 'abort',
               'use', 'flo', 'give', 'take' ]


#reserved tokens
Comparisons = ['==', '<', '<=', '>=', '>', '!=']
Connectives = ['to',  'by', 'with', 'from', 'per', 'for', 'cum', 'qua', 'via',
               'as', 'at', 'in', 'of', 'on', 're', 'is',
               'if', 'be', 'into', 'and', 'not', '+-', ]
Reserved = Connectives + Comparisons  #concatenate to get reserved words
ReservedFrameNames = ['next', 'prev']  # frame names with special meaning as target of goto


class Builder(object):
    """

    """
    def __init__(self, fileName='', mode=None, metas=None, preloads=None, behaviors=None):
        """

        """
        self.fileName = fileName #initial name of file to start building from
        self.mode = mode or []
        self.metas = metas or []
        self.preloads = preloads or []
        self.behaviors = behaviors or []
        self.files = [] #list of open file objects, appended to by load commands
        self.counts = [] #list of linectr s for open file objects

        self.houses = [] #list of houses

        self.currentFile = None
        self.currentCount = 0
        self.currentHuman = ''  # human friendly version of current line
        self.currentMode = None  # None is any
        self.currentHouse = None
        self.currentStore = None
        self.currentLogger = None
        self.currentLog = None
        self.currentFramer = None
        self.currentFrame = None  # current frame
        self.currentContext = NATIVE

    def tokenize(self, line):
        """
        Parse line and read and parse continuation lines if any and return tokens list.
        """
        saveLines = []
        saveLineViews = []

        while line.endswith('\\\n'):  # escaped newline continuation
            line = line.rstrip()
            saveLineViews.append("%04d %s" % (self.currentCount, line))
            saveLines.append(line.rstrip('\\').strip())
            line = self.currentFile.readline() #empty if end of file
            self.currentCount  += 1 #inc line counter

        # process last line read as either only line or continuation line
        line = line.rstrip()
        saveLineViews.append("%04d %s" % (self.currentCount, line))
        saveLines.append(line)

        # join all saved into one line
        lineView = "\n".join(saveLineViews)
        line = " ".join(saveLines)

        console.concise(lineView + '\n')

        line = line.strip() #strips white space both ends

        chunks = REO_Chunks.findall(line)  # also chunks trailing comments
        tokens = []
        for chunk in chunks:
            if chunk[0] == '#':  # throw away chunk as comment
                break
            else:
                tokens.append(chunk)

        return tokens

    def build(self, fileName='', mode=None, metas=None, preloads=None, behaviors=None):
        """
           Allows building from multiple files. Essentially files list is stack of files
           fileName is name of first file. Load commands in any files push (append) file onto files
           until file completed loaded and then popped off

           Each house's store is inited with the meta data in metas
        """
        #overwrite default if truthy argument
        if fileName:
            self.fileName = fileName
        if mode:
            self.mode.extend[mode]
        if metas:
            self.metas.extend[metas]
        if preloads:
            self.preloads.extend[preloads]
        if behaviors:
            self.behaviors.extend[behaviors]

        if self.behaviors: #import behavior package/module
            for behavior in self.behaviors:
                mod = importlib.import_module(behavior)

        housing.House.Clear() #clear house registry
        housing.ClearRegistries() #clear all the other registries

        try: #IOError
            self.fileName = os.path.abspath(self.fileName)
            self.currentFile = open(self.fileName,"r")
            self.currentCount = 0

            try: #ResolveError
                while self.currentFile:
                    line = self.currentFile.readline()  # empty if end of file
                    self.currentCount  += 1  # inc line counter
                    nextTokens = []  # for connective continuation

                    while (line):
                        if nextTokens:  # parsed ahead but not continuation
                            tokens = nextTokens
                            nextTokens = []
                        else:
                            tokens = self.tokenize(line)  # line and any continuations

                        if (not tokens):  #empty line or comment only
                            line = self.currentFile.readline()  # empty if end of file
                            self.currentCount  += 1  # inc line counter
                            continue  # guarantees at least 1 token

                        # verbs like load which change file context can not be continued
                        if tokens[0] not  in ('load'):  # verb allows connective continuation
                            while True:  # iteratively attempt connective continuation
                                # Connective continuation
                                # adds lines that start with connective
                                # skips empty or comment lines
                                # stops on line starting with non connective verb
                                line = self.currentFile.readline()  # empty if end of file
                                self.currentCount  += 1  # inc line counter
                                if not line:  # end of file
                                    break

                                nextTokens = self.tokenize(line)  # parse ahead
                                if nextTokens and nextTokens[0] not in Reserved:  # not connective
                                    break  # do not continue

                                if nextTokens:
                                    tokens.extend(nextTokens)  # add continuation
                                    nextTokens = []

                        self.currentHuman =  ' '.join(tokens)

                        try: #ParseError ParseWarning
                            if not self.dispatch(tokens):  # catches dispatches the return unexpectedly
                                console.terse("Script Parsing stopped at line {0} in file {1}\n".format(
                                    self.currentCount, self.currentFile.name))
                                console.terse(self.currentHuman + '\n')
                                return False

                        except excepting.ParseError as ex:
                            console.terse("\n{0}\n\n".format(ex))
                            console.terse("Script line {0} in file {1}\n".format(
                                self.currentCount, self.currentFile.name))
                            console.terse(self.currentHuman + '\n')
                            raise

                        #dispatch evals commands. self.currentFile may be changed by load command
                        if not nextTokens:
                            line = self.currentFile.readline() #empty if end of file
                            self.currentCount  += 1 #inc line counter

                    self.currentFile.close()
                    if self.files:
                        self.currentFile = self.files.pop()
                        self.currentCount = self.counts.pop()
                        console.terse("Resume loading from file {0}.\n".format(self.currentFile.name))
                    else:
                        self.currentFile = None

                #building done so now resolve links and collect actives inactives
                for house in self.houses:
                    house.orderTaskables()
                    house.resolve()

                    if console._verbosity >= console.Wordage.concise:
                        house.showAllTaskers()
                        #show framework hierarchiy
                        for framer in house.framers:
                            framer.showHierarchy()

                        #show hierarchy of each house's store
                        console.concise( "\nData Store for {0}\n".format(house.name))
                        house.store.expose(valued=(console._verbosity >= console.Wordage.terse))

                return True

            except excepting.ResolveError as ex:
                console.terse("{0}\n".format(ex))
                return False


        except IOError as ex:
            console.terse("Error opening mission file  {0}\n".format(ex))
            return False

        finally:
            for f in self.files:
                if not f.closed:
                    f.close()

    def dispatch(self, tokens):
        """
        Converts declaration verb into build method name  and calls it
        """

        verb = tokens[0]
        index = 1
        if verb not in VerbList:
            msg = "ParseError: Building {0}. Unknown verb {1}, index = {2} tokens = {3}".format(
                     verb, verb, index, tokens)
            raise excepting.ParseError(msg, tokens, index)

        verbMethod = 'build' + verb.capitalize()
        if hasattr(self, verbMethod):
            return(getattr(self, verbMethod )(verb, tokens, index))
        else:
            return self.buildGeneric(verb, tokens, index)

    def buildGeneric(self, verb, tokens, index):
        """
        Called when no build method exists for a verb
        """
        msg = "ParseError: No build method for verb {0}.".format(verb)
        raise excepting.ParseError(msg, tokens, index)

    def buildLoad(self, command, tokens, index):
        """
           load filepathname
        """
        try:
            name = tokens[index]
            index +=1

            self.files.append(self.currentFile) #push currentFile
            self.counts.append(self.currentCount) #push current line ct
            cwd = os.getcwd() #save current working directory
            os.chdir(os.path.split(self.currentFile.name)[0]) # set cwd to current file
            name = os.path.abspath(os.path.expanduser(name)) # resolve name if relpath to cwd
            os.chdir(cwd) #restore old cwd
            self.currentFile = open(name,"r")
            self.currentCount = 0
            console.terse("Loading from file {0}.\n".format(self.currentFile.name))

        except IndexError:
            msg = "ParseError: Building verb '%s'. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building verb '%s'. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        return True

    #House specific builders
    def buildHouse(self, command, tokens, index):
        """Create a new house and make it the current one

           house dreams
        """
        try:
            name = tokens[index]
            index +=1

            self.verifyName(name, command, tokens, index)

            self.currentHouse = housing.House(name = name) #also creates .store
            self.houses.append(self.currentHouse)
            self.currentStore = self.currentHouse.store

            console.terse("   Created House '{0}'. Assigning registries and "
                          "creating instances ...\n".format(name))

            self.currentHouse.assignRegistries()

            console.profuse("     Clearing current Framer, Frame, Log etc.\n")
            #changed store so need to make new frameworks and frames
            self.currentFramer = None #current framer
            self.currentFrame = None #current frame
            self.currentLogger = None #current logger
            self.currentLog = None #current log

            #meta data in metas is list of triples of (name, path, data)
            for name, path, data in self.metas:
                self.currentHouse.metas[name] = self.initPathToData(path, data)

            # set .meta.house to house.name
            self.currentHouse.metas['house'] = self.initPathToData('.meta.house',
                    odict(value=self.currentHouse.name))

            for path, data in self.preloads:
                self.initPathToData(path, data)

        except IndexError:
            msg = "ParseError: Building verb '%s'. Not enough tokens." % (command, )
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building verb '%s'. Unused tokens." % (command, )
            raise excepting.ParseError(msg, tokens, index)

        msg = "   Built House '{0}' with meta:\n".format(self.currentHouse.name)
        for name, share in self.currentHouse.metas.items():
            msg += "       {0}: {1!r}\n".format(name, share)
        console.terse(msg)

        msg = "   Built House '{0}' with preload:\n".format(self.currentHouse.name)
        for path, data in self.preloads:
            share = self.currentHouse.store.fetch(path)
            msg += "       {0}: {1!r}\n".format(path, share)
        console.terse(msg)

        return True

    # Convenience Functions

    def initPathToData(self, path, data):
        """Convenience support function to preload meta data.
           Initialize share given by path with data.
           Assumes self.currentStore is valid
           path is share path string
           data is ordered dict of data
        """
        share = self.currentStore.create(path)
        self.verifyShareFields(share, data.keys(), None, None)

        share.update(data)
        return share

    #Store specific builders

    def buildInit(self, command, tokens, index):
        """Initialize share in current store

           init destination with data
           init indirect from source

           destination:
              absolute
              path

           data:
              direct

           indirect:
              [(value, fields) in] absolute
              [(value, fields) in] path

           source:
              [(value, fields) in] absolute
              [(value, fields) in] path

        """
        if not self.currentStore:
            msg = "ParseError: Building verb '%s'. No current store" % (command)
            raise excepting.ParseError(msg, tokens, index)

        try:

            destinationFields, index = self.parseFields(tokens, index)
            destinationPath, index = self.parsePath(tokens, index)

            if self.currentStore.fetchShare(destinationPath) is None:
                console.terse("     Warning: Init of non-preexistent share {0} ..."
                        " creating anyway\n".format(destinationPath))

            destination = self.currentStore.create(destinationPath)

            connective = tokens[index]
            index += 1

            if connective in ('with', 'to'):  # to form deprecated eventually remove
                if connective == 'to':
                    console.terse("Warning: Connective 'to' in 'init' verb depricated. Use 'with' instead.\n")
                if destinationFields: #fields not allowed so error
                    msg = "ParseError: Building verb '%s'. Unexpected fields '%s in' clause " %\
                        (command, destinationFields)
                    raise excepting.ParseError(msg, tokens, index)

                data, index = self.parseDirect(tokens, index)

                #prevent init value and non value fields in same share
                self.verifyShareFields(destination, data.keys(), tokens, index)

                destination.update(data)
                console.profuse("     Inited share {0} to data = {1}\n".format(destination.name, data))

            elif connective in ('from', ):
                sourceFields, index = self.parseFields(tokens, index)
                sourcePath, index = self.parsePath(tokens, index)

                source = self.currentStore.fetchShare(sourcePath)
                if source is None:
                    msg = "ParseError: Building verb '%s'. Nonexistent source share '%s'" %\
                        (command, sourcePath)
                    raise excepting.ParseError(msg, tokens, index)

                sourceFields, destinationFields = self.prepareSrcDstFields(source,
                                                                           sourceFields,
                                                                           destination,
                                                                           destinationFields,
                                                                           tokens,
                                                                           index)

                data = odict()
                for sf, df in izip(sourceFields, destinationFields):
                    data[df] = source[sf]

                destination.update(data)

                msg = "     Inited share {0} from source {1} with data = {2}\n".format(
                    destination.name, source.name, data)
                console.profuse(msg)

            else:
                msg = "ParseError: Building verb '%s'. Unexpected connective '%s'" %\
                    (command, connective)
                raise excepting.ParseError(msg, tokens, index)

        except IndexError:
            msg = "ParseError: Building verb '%s'. Not enough tokens." % (command, )
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building verb '%s'. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        return True

    def buildServer(self, command, tokens, index):
        """create server tasker in current house
           server has to have name so can  ask stop

           server name [at period] [be scheduled]
           [rx shost:sport] [tx dhost:dport] [in order] [to prefix] [per data]
           [for source]

           scheduled: (active, inactive, slave)

           rx:
              (host:port, :port, host:, host, :)

           tx:
              (host:port, :port, host:, host, :)

           order:
              (front, mid, back)

           prefix
              filepath

           data:
              direct

           source:
              [(value, fields) in] indirect

        """
        if not self.currentHouse:
            msg = "ParseError: Building verb '%s'. No current house" % (command)
            raise excepting.ParseError(msg, tokens, index)

        if not self.currentStore:
            msg = "ParseError: Building verb '%s'. No current store" % (command)
            raise excepting.ParseError(msg, tokens, index)

        try:
            parms = {}
            init = {}
            name = ''
            connective = None
            period = 0.0
            prefix = './'
            schedule = ACTIVE #globaling.py
            order = MID #globaling.py
            rxa = ''
            txa = ''
            sha = ('', 54321) #empty host means any interface on local host
            dha = ('localhost', 54321)

            name = tokens[index]
            index +=1

            while index < len(tokens): #options
                connective = tokens[index]
                index += 1

                if connective == 'at':
                    period = abs(Convert2Num(tokens[index]))
                    index +=1

                elif connective == 'to':
                    prefix = tokens[index]
                    index +=1

                elif connective == 'be':
                    option = tokens[index]
                    index +=1

                    if option not in ['active', 'inactive', 'slave']:
                        msg = "ParseError: Building verb '%s'. Bad server scheduled option got %s" % \
                            (command, option)
                        raise excepting.ParseError(msg, tokens, index)

                    schedule = ScheduleValues[option] #replace text with value

                elif connective == 'in':
                    order = tokens[index]
                    index +=1
                    if order not in OrderValues:
                        msg = "ParseError: Building verb '%s'. Bad order option got %s" % \
                            (command, order)
                        raise excepting.ParseError(msg, tokens, index)

                    order = OrderValues[order] #convert to order value

                elif connective == 'rx':
                    rxa = tokens[index]
                    index += 1

                elif connective == 'tx':
                    txa = tokens[index]
                    index += 1

                elif connective == 'per':
                    data, index = self.parseDirect(tokens, index)
                    init.update(data)

                elif connective == 'for':
                    srcFields, index = self.parseFields(tokens, index)
                    srcPath, index = self.parsePath(tokens, index)
                    if self.currentStore.fetchShare(srcPath) is None:
                        console.terse("     Warning: Init 'with' non-existent share {0}"
                                      " ... creating anyway".format(srcPath))
                    src = self.currentStore.create(srcPath)
                    #assumes src share inited before this line parsed
                    for field in srcFields:
                        init[field] = src[field]

                else:
                    msg = "ParseError: Building verb '%s'. Bad connective got %s" % \
                        (command, connective)
                    raise excepting.ParseError(msg, tokens, index)

        except IndexError:
            msg = "ParseError: Building verb '%s'. Not enough tokens." % (command, )
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building verb '%s'. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        prefix += '/' + self.currentHouse.name #extra slashes are ignored

        if rxa:
            if ':' in rxa:
                host, port = rxa.split(':')
                sha = (host, int(port))
            else:
                sha = (rxa, sha[1])

        if txa:
            if ':' in txa:
                host, port = txa.split(':')
                dha = (host, int(port))
            else:
                dha = (txa, dha[1])

        server = serving.Server(name=name, store = self.currentStore,)
        kw = dict(period=period, schedule=schedule, sha=sha, dha=dha, prefix=prefix,)
        kw.update(init)
        server.reinit(**kw)

        self.currentHouse.taskers.append(server)
        if schedule == SLAVE:
            self.currentHouse.slaves.append(server)
        else: #taskable active or inactive
            if order == FRONT:
                self.currentHouse.fronts.append(server)
            elif order == BACK:
                self.currentHouse.backs.append(server)
            else:
                self.currentHouse.mids.append(server)

        msg = "     Created server named {0} at period {2:0.4f} be {3}\n".format(
            server.name, name, server.period,  ScheduleNames[server.schedule])
        console.profuse(msg)

        return True

    #Logger specific builders
    def buildLogger(self, command, tokens, index):
        """
        Create logger in current house


        logger logname [to prefix] [at period] [be scheduled]
                       [flush interval]  [keep copies] [cycle term] [size bytes]
        scheduled: (active, inactive, slave)
        period seconds
        interval seconds
        term seconds
        copies integer
        bytes bytes

        logger basic at 0.125
        logger basic

        """
        if not self.currentHouse:
            msg = "ParseError: Building verb '{0}'. No current house.".format(
                command, index, tokens)
            raise excepting.ParseError(msg, tokens, index)

        if not self.currentStore:
            msg = "ParseError: Building verb '{0}'. No current store.".format(
                            command, index, tokens)
            raise excepting.ParseError(msg, tokens, index)

        try:
            name = tokens[index]
            index +=1

            period = 0.0 #default
            schedule = ACTIVE #globaling.py
            order = MID #globaling.py
            interval = 30.0
            prefix = './'
            keep = 0
            term = 3600.0
            size = 1024 # default rotate size is 1024 bytes = 1KB
            reuse = False  # non-unique logger directory name if True


            while index < len(tokens): #options
                connective = tokens[index]
                index += 1
                if connective == 'at':
                    period = abs(Convert2Num(tokens[index]))
                    index +=1

                elif connective == 'to':  #  base directory path for log files
                    prefix = tokens[index]  # house name is post pended as sub directory
                    index +=1

                elif connective == 'be':
                    option = tokens[index]
                    index +=1

                    if option not in ['active', 'inactive', 'slave']:
                        msg = "Error building %s. Bad logger scheduled option got %s." %\
                              (command, option)
                        raise excepting.ParseError(msg, tokens, index)

                    schedule = ScheduleValues[option] #replace text with value

                elif connective == 'in':
                    order = tokens[index]
                    index +=1
                    if order not in OrderValues:
                        msg = "Error building %s. Bad order got %s." %\
                              (command, order)
                        raise excepting.ParseError(msg, tokens, index)
                    order = OrderValues[order] #convert to order value

                elif connective == 'flush':
                    interval = max(1.0, abs(Convert2Num(tokens[index])))
                    index +=1

                elif connective == 'keep':
                    keep = max(0, int(Convert2Num(tokens[index])))
                    index +=1

                elif connective == 'cycle':
                    term = max(0.0, abs(Convert2Num(tokens[index])))
                    index +=1

                elif connective == 'size':
                    size = max(0, abs(Convert2Num(tokens[index])))
                    index +=1

                elif connective == 'reuse':
                    reuse = True

                else:
                    msg = "Error building %s. Bad connective got %s." %\
                          (command, connective)
                    raise excepting.ParseError(msg, tokens, index)

            if name in logging.Logger.Names:
                msg = "Error building %s. Task %s already exists." %\
                      (command, name)
                raise excepting.ParseError(msg, tokens, index)

            logger = logging.Logger(name=name,
                                    store=self.currentStore,
                                    period=period,
                                    flushPeriod=interval,
                                    prefix=prefix,
                                    keep=keep,
                                    cyclePeriod=term,
                                    fileSize=size,
                                    reuse=reuse)
            logger.schedule = schedule

            self.currentHouse.taskers.append(logger)

            if schedule == SLAVE:
                self.currentHouse.slaves.append(logger)
            else: #taskable active or inactive
                if order == FRONT:
                    self.currentHouse.fronts.append(logger)
                elif order == BACK:
                    self.currentHouse.backs.append(logger)
                else:
                    self.currentHouse.mids.append(logger)

            self.currentLogger = logger

            console.profuse("     Created logger named {0} at period {1:0.4f} be {2}\n".format(
                logger.name, logger.period,  ScheduleNames[logger.schedule]))

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command, )
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        return True


    def buildLog(self, command, tokens, index):
        """
        Create log in current logger

        log name  [to fileName] [as (text, binary)] [on rule]
        rule: (once, never, always, update, change, streak, deck)
        default fileName is log's name
        default type is text
        default rule  is never

        for manual logging use tout command with rule once or never


        log autopilot text to './logs/' on update
        """
        if not self.currentLogger:
            msg = "Error building %s. No current logger." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if not self.currentStore:
            msg = "Error building %s. No current store." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        try:
            kind = 'text'
            fileName = ''
            rule = NEVER

            name = tokens[index]
            index +=1


            while index < len(tokens): #options
                connective = tokens[index]
                index += 1

                if connective == 'as':
                    kind = tokens[index]
                    index +=1

                    if kind not in ['text', 'binary']:
                        msg = "Error building %s. Bad kind = %s." %\
                              (command, kind)
                        raise excepting.ParseError(msg, tokens, index)

                elif connective == 'to':
                    fileName = tokens[index]
                    index +=1

                elif connective == 'on':
                    rule = tokens[index].capitalize()
                    index +=1

                    if rule not in LogRuleValues:
                        msg = "Error building %s. Bad rule = %s." %\
                              (command, rule)
                        raise excepting.ParseError(msg, tokens, index)

                    rule = LogRuleValues[rule]

                else:
                    msg = "Error building %s. Bad connective got %s." %\
                          (command, connective)
                    raise excepting.ParseError(msg, tokens, index)

            if name in logging.Log.Names:  # check if instance name in Registrar
                msg = "Error building %s. Log named %s already exists." %\
                      (command, name)
                raise excepting.ParseError(msg, tokens, index)

            if fileName:
                for log in self.currentLogger.logs:
                    if fileName == log.baseFilename:
                        msg = ("Error building {0}. Log named {1} file named {2} "
                              "already exists.".format(command, name, fileName))
                        raise excepting.ParseError(msg, tokens, index)

            log = logging.Log(name=name,
                              store=self.currentStore,
                              kind=kind,
                              baseFilename=fileName,
                              rule=rule)
            self.currentLogger.addLog(log)
            self.currentLog = log

            console.profuse("     Created log named {0} kind {1} file {2} rule {3}\n".format(
                name, kind, fileName, LogRuleNames[rule]))

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command, )
            raise excepting.ParseError(msg, tokens, index)

        return True

    def buildLoggee(self, command, tokens, index):
        """
        Add loggee(s) to current log

        Syntax:

        loggee [fields in] path [as tag] [[fields in] path [as tag]] ...

            path: share path
            fields: field list


        If fields not provided use all fields
        If tag not provide use last segment of path as tag

        If log rule is streak then only one loggee per log is allowed and only
        the first field from fields clause is used.

        Syntax:
        log name on streak
          loggee [fields in] path [as tag]


        If log rule is deck then only one loggee per log is allowed and
        fields clause is required.

        Syntax:
        log name on deck
          loggee fields in path [as tag]

        """
        if not self.currentLog:
            msg = "Error building %s. No current log." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if not self.currentStore:
            msg = "Error building %s. No current store." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        try:
            while index < len(tokens):
                tag = ""
                fields, index = self.parseFields(tokens, index)
                path = tokens[index]
                index +=1

                if path in Reserved:
                    msg = "ParseError: Invalid path '{0}' using reserved".format(path)
                    raise excepting.ParseError(msg, tokens, index)

                if not (REO_DotPath.match(path) or REO_RelPath.match(path)):
                    #valid absolute or relative path segment without relation clause
                    msg = "ParseError: Invalid path format'{0}'".format(path)
                    raise excepting.ParseError(msg, tokens, index)

                parts = path.split(".")
                if "me" in parts:
                    msg = "ParseError: Invalid path format'{0}', 'me' undefined".format(path)
                    raise excepting.ParseError(msg, tokens, index)

                if index < len(tokens):
                    connective = tokens[index]
                    if connective == 'as':
                        index += 1  # eat token
                        tag = tokens[index]
                        if tag in Reserved:
                            msg = "ParseError: Invalid tag '{0}' using reserved".format(tag)
                            raise excepting.ParseError(msg, tokens, index)
                        tag = StripQuotes(tag)
                        index += 1

                if not tag:
                    tag = parts[-1]

                share = self.currentStore.create(path) #create so no errors at runtime
                if not isinstance(share, storing.Share): #verify path ends in share not node
                    msg = "Error building %s. Loggee path %s not Share." % (command, path)
                    raise excepting.ParseError(msg, tokens, index)

                if tag in self.currentLog.loggees:
                    msg = "Error building %s. Loggee %s already exists in Log %s." %\
                          (command, tag, self.currentLog.name)
                    raise excepting.ParseError(msg, tokens, index)

                if self.currentLog.rule in (STREAK, DECK) and self.currentLog.loggees:
                    # only one loggee allowed when rule is streak or deck
                    msg = ("Error building {0}. Only one loggee allowed when "
                          "rule is streak or deck.".format(command))
                    raise excepting.ParseError(msg, tokens, index)

                self.currentLog.addLoggee(tag=tag, loggee=share, fields=fields)

                console.profuse("     Added loggee {0} with tag {1} fields {2}\n".format(
                    share.name, tag, fields))

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        return True

    #Framework specific builders

    def buildFramer(self, command, tokens, index):
        """Create a new framer and make it the current one

           framer framername [be (active, inactive, aux, slave)] [at period]
                                [first frame] [via inode]
           framer framername be active at 0.0
           framer framername
        """
        if not self.currentHouse:
            msg = "Error building %s. No current house." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if not self.currentStore:
            msg = "Error building %s. No current store." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        try:
            name = tokens[index]
            index +=1

            self.verifyName(name, command, tokens, index)

            schedule = INACTIVE  #globaling.py
            order = MID #globaling.py
            period = 0.0
            frame = ''
            inode = ''


            while index < len(tokens): #options
                connective = tokens[index]
                index += 1

                if connective == 'at':
                    period = max(0.0, Convert2Num(tokens[index]))
                    index +=1

                elif connective == 'be':
                    option = tokens[index]
                    index +=1

                    if option not in ScheduleValues:
                        msg = "Error building %s. Bad scheduled option got %s." %\
                                (command, option)
                        raise excepting.ParseError(msg, tokens, index)

                    schedule = ScheduleValues[option] #replace text with value

                elif connective == 'in':
                    order = tokens[index]
                    index +=1
                    if order not in OrderValues:
                        msg = "Error building %s. Bad order got %s." %\
                                (command, order,)
                        raise excepting.ParseError(msg, tokens, index)
                    order = OrderValues[order] #convert to order value

                elif connective == 'first':
                    frame = tokens[index]
                    index +=1

                    self.verifyName(frame, command, tokens, index)

                elif connective == 'via':
                    inode, index = self.parseIndirect(tokens, index, node=True)

                else:
                    msg = "Error building %s. Bad connective got %s." %\
                            (command, connective)
                    raise excepting.ParseError(msg, tokens, index)

            if name in framing.Framer.Names:
                msg = "Error building %s. Framer or Task %s already exists." %\
                        (command, name)
                raise excepting.ParseError(msg, tokens, index)
            else:
                framer = framing.Framer(name = name,
                                        store = self.currentStore,
                                        period = period)
                framer.schedule = schedule
                framer.first = frame #need to resolve later
                framer.inode = inode

                self.currentHouse.taskers.append(framer)
                self.currentHouse.framers.append(framer)

                if schedule == SLAVE:
                    self.currentHouse.slaves.append(framer)
                elif schedule == AUX:
                    self.currentHouse.auxes.append(framer)
                elif schedule == MOOT:
                    self.currentHouse.moots.append(framer)
                else: #taskable active or inactive
                    if order == FRONT:
                        self.currentHouse.fronts.append(framer)
                    elif order == BACK:
                        self.currentHouse.backs.append(framer)
                    else:
                        self.currentHouse.mids.append(framer)

                self.currentFramer = framer
                self.currentFramer.assignFrameRegistry()
                self.currentFrame = None #changed current Framer so no current Frame

                console.profuse("     Created Framer named '{0}' at period {1:0.4f} be {2} first {3}\n".format(
                    framer.name, framer.period, ScheduleNames[framer.schedule], framer.first))

                console.profuse("     Added Framer '{0}' to House '{1}', Assigned frame registry\n".format(
                    framer.name, self.currentHouse.name))


        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        return True

    def buildFirst(self, command, tokens, index):
        """set first (starting) frame for current framer

           first framename
        """
        if not self.currentFramer:
            msg = "Error building %s. No current framer." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        try:
            name = tokens[index]
            index +=1

            self.verifyName(name, command, tokens, index)

            self.currentFramer.first = name #need to resolve later

            console.profuse("     Assigned first frame {0} for framework {1}\n".format(
                name, self.currentFramer.name))

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        return True

    #Frame specific builders
    def buildFrame(self, command, tokens, index):
        """Create frame and attach to over frame if indicated

           frame framename [in over] [via inode]


           framename cannot be "next" which is reserved

        """
        if not self.currentStore:
            msg = "Error building %s. No current store." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if not self.currentFramer:
            msg = "Error building %s. No current framer." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        inode = ''

        try:
            name = tokens[index]
            index +=1

            self.verifyName(name, command, tokens, index)

            over = None

            while index < len(tokens): #options
                connective = tokens[index]
                index += 1

                if connective == 'in':
                    over = tokens[index]
                    index +=1

                elif connective == 'via':
                    inode, index = self.parseIndirect(tokens, index, node=True)

                else:
                    msg = "Error building %s. Bad connective got %s." % (command, connective)
                    raise excepting.ParseError(msg, tokens, index)

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if name in ReservedFrameNames:
            msg = "Error building %s in Framer %s. Frame name %s reserved." %\
                    (command, self.currentFramer.name, name)
            raise excepting.ParseError(msg, tokens, index)
        elif name in framing.Frame.Names: #could use Registry Retrieve function
            msg = "Error building %s in Framer %s. Frame %s already exists." %\
                    (command, self.currentFramer.name, name)
            raise excepting.ParseError(msg, tokens, index)
        else:
            frame = framing.Frame(name=name, store = self.currentStore,
                                  framer=self.currentFramer.name,
                                  inode=inode)

            if over:
                frame.over = over #need to resolve later

            #if previous frame did not have explicit next frame then use this new frame
            # ad next lexically
            if self.currentFrame and not self.currentFrame.next_:
                self.currentFrame.next_ = frame.name

                #default first frame is first lexical frame if not assigned otherwise
                #so if startFrame is none then we must be first lexical frame
            if not self.currentFramer.first: #frame.framer.first:
                self.currentFramer.first = frame.name #frame.framer.first = frame

            self.currentFrame = frame
            self.currentContext = NATIVE

        console.profuse("     Created frame {0} with over {1}\n".format(frame.name, over))

        return True

    def buildOver(self, command, tokens, index):
        """Makes frame the over frame of the current frame

           over frame
        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            over = tokens[index]
            index +=1

            self.verifyName(over, command, tokens, index)

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        self.currentFrame.over = over #need to resolve and attach later

        console.profuse("     Assigned over {0} to frame {1}\n".format(
            over,self.currentFrame.name))

        return True


    def buildUnder(self, command, tokens, index):
        """Makes frame the primary under frame of the current frame

           under frame
        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            under = tokens[index]
            index +=1

            self.verifyName(under, command, tokens, index)

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        unders = self.currentFrame.unders

        if not unders: #empty so just append
            unders.append(under)

        elif under != unders[0]: #not already primary
            while under in unders: #remove under (in case multiple copies shouldnt be)
                unders.remove(under)
            if isinstance(unders[0], framing.Frame): #should not be but if valid don't overwrite
                unders.insert(0, under)
            else: #just name so overwrite
                unders[0] = under

        else: #under == unders[0] already so do nothing
            pass

        console.profuse("     Assigned primary under {0} for frame {1}\n".format(
            under,self.currentFrame.name))

        return True

    def buildNext(self, command, tokens, index):
        """Explicitly assign next frame for timeouts and as target of go next

           next frameName
           next

           blank frameName means use lexically next allows override if multiple
           next commands to default of lexical


        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            if index < len(tokens): #next frame optional
                next_ = tokens[index]
                index += 1

                self.verifyName(next_, command, tokens, index)

            else:
                next_ = None

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        self.currentFrame.next_ = next_

        console.profuse("     Assigned next frame {0} for frame {1}\n".format(
            next_, self.currentFrame.name))

        return True


    def buildAux(self, command, tokens, index):
        """Parse 'aux' command  for simple, cloned, or conditional aux of forms

           Simple Auxiliary:
              aux framername

           Cloned Auxiliary:
              aux framername as (mine, clonedauxname) [via (main, mine, inode)]


           Simple Conditional Auxiliary:
              aux framername  if [not] need
              aux framername  if [not] need [and [not] need ...]

           Cloned Conditional Auxiliary:
              aux framername as (mine, clonedauxname) [via inode]
                             if [not] need
              aux framername as (mine, clonedauxname) [via inode]
                             if [not] need [and [not] need ...]

        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            needs = []
            aux = None  #  original
            connective = None
            clone = None
            inode = ''
            insular = False

            aux = tokens[index]
            index +=1 #eat token

            self.verifyName(aux, command, tokens, index)

            while index < len(tokens): #options
                connective = tokens[index]
                index += 1

                if connective == 'as':
                    clone = tokens[index]
                    index += 1
                    self.verifyName(clone, command, tokens, index)

                elif connective == 'via':
                    inode, index = self.parseIndirect(tokens, index, node=True)

                elif connective == 'if':
                    while (index < len(tokens)):
                        act, index = self.makeNeed(tokens, index)
                        if not act:
                            return False # something wrong do not know what
                        needs.append(act)
                        if index < len(tokens):
                            connective = tokens[index]
                            if connective not in ['and']:
                                msg = "ParseError: Building verb '%s'. Bad connective '%s'" % \
                                                        (command, connective)
                                raise excepting.ParseError(msg, tokens, index)
                            index += 1 #otherwise eat token

                else:
                    msg = ("Error building {0}. Invalid connective"
                          " '{1}'.".format(command, connective))
                    raise excepting.ParseError(msg, tokens, index)

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if clone and needs:
            msg = "Error building %s. Conditional auxilary may not be clone." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if clone:
            if clone == 'mine':
                clone = self.currentFramer.newMootTag(base=aux)
                insular = True

            if clone in self.currentFramer.moots:
                msg = ("Error building {0}. Aux/Clone tag '{1}' "
                      "already in use.".format(command, clone))
                raise excepting.ParseError(msg, tokens, index)

            data = odict(original=aux,
                         clone=clone,
                         schedule=AUX,
                         human=self.currentHuman,
                         count=self.currentCount,
                         inode=inode,
                         insular=insular)

            self.currentFramer.moots[clone] = data  # need to resolve early
            aux = odict(tag=clone)  # mapping indicates that its a clone
            # assign aux to mapping with clone tag name as original aux is to be cloned
            # named clone create clone when resolve framer.moots so may be referenced
            # named clones must be resolved before any frames get resolved
            # and are added to the class Framer.names so they can be referenced
            # resolved by house.resolve -> house.presolvePresolvables
            #    -> framer.presolve -> framer.resolveMoots
            # resolveMoots adds new resolveable framers to house.presolvables
            # self.store.house.presolvables.append(clone)

        if needs:  # conditional auxiliary suspender preact
            human = ' '.join(tokens) #recreate transition command string for debugging
            #resolve aux link later
            parms = dict(needs = needs, main = 'me', aux = aux, human = human)
            act = acting.Act(   actor='Suspender',
                                registrar=acting.Actor,
                                parms=parms,
                                human=self.currentHuman,
                                count=self.currentCount)

            self.currentFrame.addPreact(act)

            console.profuse("     Added suspender preact,  '{0}', with aux"
                            " {1} needs:\n".format(command, aux))
            for need in needs:
                console.profuse("       {0} with parms = {1}\n".format(need.actor, need.parms))

        else: # simple auxiliary  if aux is string then regular auz if aux is mapping then clone
            self.currentFrame.addAux(aux) #need to resolve later
            console.profuse("     Added aux framer {0}\n".format(aux))

        return True

    def buildRear(self, command, tokens, index):
        """
        Parse 'rear' verb

        Two Forms: only first form is currently supported

        rear original [as mine] [be aux] in frame framename

                framename cannot be me or in outline of me

        rear original as clonename be schedule

               schedule cannot be aux
               clonename cannot be mine



        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            original = None
            connective = None
            clone = 'mine'  # default is insular clone
            schedule = 'aux' # default schedule is aux
            frame = 'me' # default frame is current

            original = tokens[index]
            index +=1  # eat token
            self.verifyName(original, command, tokens, index)

            while index < len(tokens): #options
                connective = tokens[index]
                index += 1

                if connective == 'as':
                    clone = tokens[index]
                    index += 1

                    self.verifyName(clone, command, tokens, index)

                elif connective == 'be':
                    schedule = tokens[index]
                    index += 1

                elif connective == 'in': #optional in frame or in framer clause
                    place = tokens[index] #need to resolve
                    index += 1  # eat token

                    if place != 'frame':
                        msg = ("ParseError: Building verb '{0}'. Invalid "
                            " '{1}' clause. Expected 'frame' got "
                            "'{2}'".format(command, connective, place))
                        raise excepting.ParseError(msg, tokens, index)

                    if index < len(tokens):
                        frame = tokens[index]
                        index += 1

                else:
                    msg = ("Error building {0}. Invalid connective"
                          " '{1}'.".format(command, connective))
                    raise excepting.ParseError(msg, tokens, index)

        except IndexError:
            msg = "Error building {0}. Not enough tokens.".format(command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building {0}. Unused tokens.".format(command,)
            raise excepting.ParseError(msg, tokens, index)

        # only allow schedule of aux for now
        if schedule not in ScheduleValues or schedule not  in ['aux']:
            msg = "Error building {0}. Bad scheduled option got '{1}'.".format(command, schedule)
            raise excepting.ParseError(msg, tokens, index)

        schedule = ScheduleValues[schedule] #replace text with value

        # when clone is insular and schedule is aux then frame cannot be
        # current frames outline. This is validated in the actor resolve

        if schedule == AUX:
            if clone != 'mine':
                msg = ("Error building {0}. Only insular clonename of"
                       " 'mine' allowed. Got '{1}'.".format(command, clone))
                raise excepting.ParseError(msg, tokens, index)

            if frame == 'me':
                msg = ("Error building {0}. Frame clause required.".format(command, clone))
                raise excepting.ParseError(msg, tokens, index)

        parms = dict(original=original,
                     clone=clone,
                     schedule=schedule,
                     frame=frame)

        actorName = 'Rearer'
        if actorName not in acting.Actor.Registry:
            msg = "Error building '{0}'. No actor named '{1}'.".format(command, actorName)
            raise excepting.ParseError(msg, tokens, index)

        act = acting.Act(actor=actorName,
                         registrar=acting.Actor,
                         parms=parms,
                         human=self.currentHuman,
                         count=self.currentCount)

        context = self.currentContext
        if context == NATIVE:
            context = ENTER  # what is native for this command

        if not self.currentFrame.addByContext(act, context):
            msg = "Error building %s. Bad context '%s'." % (command, context)
            raise excepting.ParseError(msg, tokens, index)

        console.profuse("     Added {0} '{1}' with parms '{2}'\n".format(
            ActionContextNames[context], act.actor, act.parms))

        return True

    def buildRaze(self, command, tokens, index):
        """
        Parse 'raze' verb

        raze (all, last, first) [in frame [(me, framename)]]


        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            connective = None
            who = None  # default is insular clone
            frame = 'me' # default frame is current

            who = tokens[index]
            index +=1  # eat token
            if who not in ['all', 'first', 'last']:
                msg = ("ParseError: Building verb '{0}'. Invalid target of"
                    " raze. Expected one of ['all', 'first', 'last'] but got "
                    "'{2}'".format(command, connective, who))
                raise excepting.ParseError(msg, tokens, index)

            while index < len(tokens): #options
                connective = tokens[index]
                index += 1

                if connective == 'in': #optional in frame or in framer clause
                    place = tokens[index] #need to resolve
                    index += 1  # eat token

                    if place != 'frame':
                        msg = ("ParseError: Building verb '{0}'. Invalid "
                            " '{1}' clause. Expected 'frame' got "
                            "'{2}'".format(command, connective, place))
                        raise excepting.ParseError(msg, tokens, index)

                    if index < len(tokens):
                        frame = tokens[index]
                        index += 1

                else:
                    msg = ("Error building {0}. Invalid connective"
                          " '{1}'.".format(command, connective))
                    raise excepting.ParseError(msg, tokens, index)

        except IndexError:
            msg = "Error building {0}. Not enough tokens.".format(command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building {0}. Unused tokens.".format(command,)
            raise excepting.ParseError(msg, tokens, index)


        parms = dict(who=who,
                     frame=frame)

        actorName = 'Razer'
        if actorName not in acting.Actor.Registry:
            msg = "Error building '{0}'. No actor named '{1}'.".format(command, actorName)
            raise excepting.ParseError(msg, tokens, index)

        act = acting.Act(actor=actorName,
                         registrar=acting.Actor,
                         parms=parms,
                         human=self.currentHuman,
                         count=self.currentCount)

        context = self.currentContext
        if context == NATIVE:
            context = EXIT  # what is native for this command

        if not self.currentFrame.addByContext(act, context):
            msg = "Error building %s. Bad context '%s'." % (command, context)
            raise excepting.ParseError(msg, tokens, index)

        console.profuse("     Added {0} '{1}' with parms '{2}'\n".format(
            ActionContextNames[context], act.actor, act.parms))

        return True

    def buildDone(self, command, tokens, index):
        """
        Creates complete action that indicates tasker(s) completed
        by setting .done state to True

           native context is enter

           done tasker [tasker ...]
           done [me]

           tasker:
              (taskername, me)

        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            kind = 'Done'
            taskers = []

            while index < len(tokens):
                tasker = tokens[index]
                index +=1

                self.verifyName(tasker, command, tokens, index)
                taskers.append(tasker) #resolve later

            if not taskers:
                taskers.append('me')

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        actorName = 'Complete' + kind.capitalize()
        if actorName not in completing.Complete.Registry:
            msg = "Error building complete %s. No actor named %s." %\
                    (kind, actorName)
            raise excepting.ParseError(msg, tokens, index)

        parms = {}
        parms['taskers'] = taskers #resolve later
        act = acting.Act(actor=actorName,
                         registrar=completing.Complete,
                         parms=parms,
                         human=self.currentHuman,
                         count=self.currentCount)

        context = self.currentContext
        if context == NATIVE:
            context = ENTER #what is native for this command

        if not self.currentFrame.addByContext(act, context):
            msg = "Error building %s. Bad context '%s'." % (command, context)
            raise excepting.ParseError(msg, tokens, index)

        console.profuse("     Created done complete {0} with {1}\n".format(act.actor, act.parms))

        return True

    def buildTimeout(self, command, tokens, index):
        """creates implicit transition to next on elapsed >= value

           timeout 5.0
        """
        self.verifyCurrentContext(tokens, index)

        try:
            value =  abs(Convert2Num(tokens[index])) #convert text to number if valid format
            index +=1

            if isinstance(value, str):
                msg = "Error building %s. invalid timeout %s." %\
                      (command, value)
                raise excepting.ParseError(msg, tokens, index)

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        # build need act for transact
        need = self.makeImplicitDirectFramerNeed( name="elapsed",
                                                  comparison='>=',
                                                  goal=float(value),
                                                  tolerance=0)

        needs = []
        needs.append(need)

        # build transact
        human = ' '.join(tokens) #recreate transition command string for debugging
        far = 'next' #resolve far link later
        parms = dict(needs = needs, near = 'me', far = far, human = human)
        act = acting.Act(actor='Transiter',
                         registrar=acting.Actor,
                         parms=parms,
                         human=self.currentHuman,
                         count=self.currentCount)
        self.currentFrame.addPreact(act) #add transact as preact

        console.profuse("     Added timeout transition preact,  '{0}', with far {1} needs:\n".format(
            command, far))
        for act in needs:
            console.profuse("       {0} with parms = {1}\n".format(act.actor, act.parms))

        return True

    def buildRepeat(self, command, tokens, index):
        """creates implicit transition to next on recurred >= value

           repeat 2

           go next if recurred >= 2
        """
        self.verifyCurrentContext(tokens, index)

        try:
            value =  abs(Convert2Num(tokens[index])) #convert text to number if valid format
            index +=1

            if isinstance(value, str):
                msg = "Error building %s. invalid repeat %s." %\
                      (command, value)
                raise excepting.ParseError(msg, tokens, index)

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        # build need act for transact
        need = self.makeImplicitDirectFramerNeed( name="recurred",
                                                  comparison='>=',
                                                  goal=int(value),
                                                  tolerance=0)

        needs = []
        needs.append(need)

        # build transact
        human = ' '.join(tokens) #recreate transition command string for debugging
        far = 'next' #resolve far link later
        parms = dict(needs = needs, near = 'me', far = far, human = human)
        act = acting.Act(    actor='Transiter',
                             registrar=acting.Actor,
                             parms=parms,
                             human=self.currentHuman,
                             count=self.currentCount)

        self.currentFrame.addPreact(act) #add transact as preact

        console.profuse("     Added repeat transition preact,  '{0}', with far {1} needs:\n".format(
            command, far))
        for act in needs:
            console.profuse("       {0} with parms = {1}\n".format(act.actor, act.parms))

        return True


    def buildNative(self, command, tokens, index):
        """ sets context for current frame to

           native
        """
        self.currentContext = NATIVE
        console.profuse("     Changed context to {0}\n".format(
            ActionContextNames[self.currentContext]))
        return True

    def buildBenter(self, command, tokens, index):
        """ sets context for current frame to

           benter
        """
        self.currentContext = BENTER
        console.profuse("     Changed context to {0}\n".format(
            ActionContextNames[self.currentContext]))
        return True

    def buildEnter(self, command, tokens, index):
        """ sets context for current frame to

           enter
        """
        self.currentContext = ENTER
        console.profuse("     Changed context to {0}\n".format(
            ActionContextNames[self.currentContext]))
        return True

    def buildRenter(self, command, tokens, index):
        """ sets context for current frame to

           renter
        """
        self.currentContext = RENTER
        console.profuse("     Changed context to {0}\n".format(
            ActionContextNames[self.currentContext]))
        return True

    def buildPrecur(self, command, tokens, index):
        """ sets context for current frame to

           precur
        """
        self.currentContext = PRECUR
        console.profuse("     Changed context to {0}\n".format(
            ActionContextNames[self.currentContext]))
        return True

    def buildRecur(self, command, tokens, index):
        """ sets context for current frame to

           recur
        """
        self.currentContext = RECUR
        console.profuse("     Changed context to {0}\n".format(
            ActionContextNames[self.currentContext]))
        return True

    def buildExit(self, command, tokens, index):
        """ sets context for current frame to

           exit
        """
        self.currentContext = EXIT
        console.profuse("     Changed context to {0}\n".format(
            ActionContextNames[self.currentContext]))
        return True

    def buildRexit(self, command, tokens, index):
        """ sets context for current frame to

           rexit
        """
        self.currentContext = REXIT
        console.profuse("     Changed context to {0}\n".format(
            ActionContextNames[self.currentContext]))
        return True

    #Frame Action specific builders

    def buildPrint(self, command, tokens, index):
        """prints a string consisting of space separated tokens
           print message

           print hello world

        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            message = ' '.join(tokens[1:])
        except IndexError:
            message = ''

        parms = dict(message = message)
        act = acting.Act(    actor='Printer',
                             registrar=acting.Actor,
                             parms=parms,
                             human=self.currentHuman,
                             count=self.currentCount)

        context = self.currentContext
        if context == NATIVE:
            context = ENTER #what is native for this command

        if not self.currentFrame.addByContext(act, context):
            msg = "Error building %s. Bad context '%s'." % (command, context)
            raise excepting.ParseError(msg, tokens, index)

        console.profuse("     Added {0} '{1}' with parms '{2}'\n".format(
            ActionContextNames[context], act.actor, act.parms))

        return True

    def buildPut(self, command, tokens, index):
        """Build put command to put data into share

           put data into destination

           data:
              direct

           destination:
              [(value, fields) in] indirect

        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            srcData, index = self.parseDirect(tokens, index)
            connective = tokens[index]
            index += 1
            if connective != 'into':
                msg = "ParseError: Building verb '%s'. Unexpected connective '%s'" %\
                    (command, connective)
                raise excepting.ParseError(msg, tokens, index)

            dstFields, index = self.parseFields(tokens, index)
            dstPath, index = self.parseIndirect(tokens, index)

        except IndexError:
            msg = "ParseError: Building verb '%s'. Not enough tokens." % (command, )
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building verb '%s'. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        actorName = 'Poke' + 'Direct' #capitalize second word

        if actorName not in poking.Poke.Registry:
            msg = "ParseError: Can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        parms = {}
        parms['sourceData'] = srcData  # this is dict
        parms['destination'] = dstPath # this is a share path
        parms['destinationFields'] = dstFields  # this is a list
        act = acting.Act(   actor=actorName,
                            registrar=poking.Poke,
                            parms=parms,
                            human=self.currentHuman,
                            count=self.currentCount)

        msg = "     Created Actor {0} parms: data = {1}  destination = {2} fields = {3} ".format(
            actorName, srcData, dstPath, dstFields)
        console.profuse(msg)

        context = self.currentContext
        if context == NATIVE:
            context = ENTER #what is native for this command

        if not self.currentFrame.addByContext(act, context):
            msg = "Error building %s. Bad context '%s'." % (command, context)
            raise excepting.ParseError(msg, tokens, index)

        console.profuse("     Added {0} '{1}' with parms '{2}'\n".format(
            ActionContextNames[context], act.actor, act.parms))

        return True

    def buildInc(self, command, tokens, index):
        """Build inc command to inc share by data or from source

           inc destination with data
           inc destination from source

           destination:
              [(value, field) in] indirect

           data:
              directone

           source:
              [(value, field) in] indirect


        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            dstFields, index = self.parseFields(tokens, index)
            dstPath, index = self.parseIndirect(tokens, index)

            connective = tokens[index]
            index += 1

            if connective in ('with', ):
                srcData, index = self.parseDirect(tokens, index)

                for field, value in srcData.items():
                    if isinstance(value, str):
                        msg = "ParseError: Building verb '%s'. " % (command)
                        msg += "Data value = '%s' in field '%s' not a number" %\
                            (value, field)
                        raise excepting.ParseError(msg, tokens, index)

                act = self.makeIncDirect(dstPath, dstFields, srcData)

            elif connective in ('from', ):
                srcFields, index = self.parseFields(tokens, index)
                srcPath, index = self.parseIndirect(tokens, index)

                act = self.makeIncIndirect(dstPath, dstFields, srcPath, srcFields)

            else:
                msg = "ParseError: Building verb '%s'. Unexpected connective '%s'" %\
                    (command, connective)
                raise excepting.ParseError(msg, tokens, index)

        except IndexError:
            msg = "ParseError: Building verb '%s'. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building verb '%s'. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        context = self.currentContext
        if context == NATIVE:
            context = ENTER #what is native for this command

        if not self.currentFrame.addByContext(act, context):
            msg = "Error building %s. Bad context '%s'." % (command, context)
            raise excepting.ParseError(msg, tokens, index)

        console.profuse("     Added {0} '{1}' with parms '{2}'\n".format(
            ActionContextNames[context], act.actor, act.parms))

        return True

    def buildCopy(self, command, tokens, index):
        """Build copy command to copy from one share to another

           copy source into destination

           source:
              [(value, fields) in] indirect

           destination:
              [(value, fields) in] indirect

        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            srcFields, index = self.parseFields(tokens, index)
            srcPath, index = self.parseIndirect(tokens, index)

            connective = tokens[index]
            index += 1
            if connective != 'into':
                msg = "ParseError: Building verb '%s'. Unexpected connective '%s'" %\
                    (command, connective)
                raise excepting.ParseError(msg, tokens, index)

            dstFields, index = self.parseFields(tokens, index)
            dstPath, index = self.parseIndirect(tokens, index)

        except IndexError:
            msg = "ParseError: Building verb '%s'. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building verb '%s'. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        actorName = 'Poke' + 'Indirect' #capitalize second word

        if actorName not in poking.Poke.Registry:
            msg = "ParseError: Can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        parms = {}
        parms['source'] = srcPath #this is string
        parms['sourceFields'] = srcFields #this is a list
        parms['destination'] = dstPath #this is a string
        parms['destinationFields'] = dstFields #this is a list
        act = acting.Act(   actor=actorName,
                            registrar=poking.Poke,
                            parms=parms,
                            human=self.currentHuman,
                            count=self.currentCount)

        msg = "     Created Actor {0} parms: ".format(actorName)
        for key, value in parms.items():
            msg += " {0} = {1}".format(key, value)
        console.profuse("{0}\n".format(msg))

        context = self.currentContext
        if context == NATIVE:
            context = ENTER #what is native for this command

        if not self.currentFrame.addByContext(act, context):
            msg = "Error building %s. Bad context '%s'." % (command, context)
            raise excepting.ParseError(msg, tokens, index)

        console.profuse("     Added {0} '{1}' with parms '{2}'\n".format(
            ActionContextNames[context], act.actor, act.parms))

        return True

    def buildSet(self, command, tokens, index):
        """Build set command to generate goal actions

           set goal with data
           set goal from source

           goal:
              elapsed
              recurred
              [(value, fields) in] absolute
              [(value, fields) in] relativegoal

           data:
              direct

           source:
              indirect

        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            kind = tokens[index]

            if kind in ['elapsed', 'recurred']: #simple implicit framer relative goals, direct and indirect,
                index +=1 #eat token
                act, index = self.makeFramerGoal(kind, tokens, index)

            else: #basic goals
                #goal is destination dst
                dstFields, index = self.parseFields(tokens, index)
                dstPath, index = self.parseIndirect(tokens, index)

                #required connective
                connective = tokens[index]
                index += 1

                if connective in ('with', ): #data direct
                    srcData, index = self.parseDirect(tokens, index)

                    act = self.makeGoalDirect(dstPath, dstFields, srcData)

                elif connective in ('from', ): #source indirect
                    srcFields, index = self.parseFields(tokens, index)
                    srcPath, index = self.parseIndirect(tokens, index)

                    act = self.makeGoalIndirect(dstPath, dstFields, srcPath, srcFields)

                else:
                    msg = "ParseError: Building verb '%s'. Unexpected connective '%s'" %\
                        (command, connective)
                    raise excepting.ParseError(msg, tokens, index)

            if not act:
                return False

        except IndexError:
            msg = "ParseError: Building verb '%s'. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building verb '%s'. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        context = self.currentContext
        if context == NATIVE:
            context = ENTER #what is native for this command

        if not self.currentFrame.addByContext(act, context):
            msg = "Error building %s. Bad context '%s'." % (command, context)
            raise excepting.ParseError(msg, tokens, index)

        console.profuse("     Added {0} '{1}' with parms '{2}'\n".format(
            ActionContextNames[context], act.actor, act.parms))

        return True

    def buildGo(self, command, tokens, index):
        """Parse 'go' command  transition  with
           transition conditions of forms

           Transitions:
              go far
              go far if [not] need
              go far if [not] need [and [not] need ...]

           Far:
              next
              me
              frame
        """

        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            needs = []
            far = None
            connective = None

            far = tokens[index]  #get target
            index +=1 #eat token

            self.verifyName(far, command, tokens, index)

            if index < len(tokens): #check for optional if connective
                connective = tokens[index]
                if connective not in ['if']: #invalid connective
                    msg = "ParseError: Building verb '%s'. Bad connective '%s'" % \
                        (command, connective)
                    raise excepting.ParseError(msg, tokens, index)
                index += 1 #otherwise eat token

                while (index < len(tokens)):
                    act, index = self.makeNeed(tokens, index)
                    if not act:
                        return False #something wrong do not know what
                    needs.append(act)
                    if index < len(tokens):
                        connective = tokens[index]
                        if connective not in ['and']:
                            msg = "ParseError: Building verb '%s'. Bad connective '%s'" % \
                                                    (command, connective)
                            raise excepting.ParseError(msg, tokens, index)
                        index += 1 #otherwise eat token


        except IndexError:
            msg = "ParseError: Building verb '%s'. Not enough tokens." % (command, )
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building verb '%s'. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if not needs and connective: #if but no needs
            msg = "ParseError: Building verb '%s'. Connective %s but missing need(s)" %\
                (command, connective)
            raise excepting.ParseError(msg, tokens, index)

        # build transact
        human = ' '.join(tokens) #recreate transition command string for debugging
        #resolve far link later
        parms = dict(needs = needs, near = 'me', far = far, human = human)
        act = acting.Act(   actor='Transiter',
                            registrar=acting.Actor,
                            parms=parms,
                            human=self.currentHuman,
                            count=self.currentCount)

        self.currentFrame.addPreact(act)

        console.profuse("     Added transition preact,  '{0}', with far {1} needs:\n".format(
            command, far))
        for act in needs:
            console.profuse("       {0} with parms = {1}\n".format(act.actor, act.parms))

        return True

    def buildLet(self, command, tokens, index):
        """Parse 'let' command  benter action  with entry conditions of forms

           Before Enter:
              let [me] if [not] need
              let [me] if [not] need [and [not] need ...]

           Far:
              next
              me
              frame
        """

        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            needs = []
            connective = None

            connective = tokens[index]  #get me or if
            if connective not in ['me', 'if']: #invalid connective
                msg = "ParseError: Building verb '%s'. Bad connective '%s'" % \
                    (command, connective)
                raise excepting.ParseError(msg, tokens, index)
            index += 1 #otherwise eat token

            if connective == 'me':
                connective = tokens[index] #check for if connective
                if connective not in ['if']: #invalid connective
                    msg = "ParseError: Building verb '%s'. Bad connective '%s'" % \
                        (command, connective)
                    raise excepting.ParseError(msg, tokens, index)
                index += 1 #otherwise eat token

            while (index < len(tokens)):
                act, index = self.makeNeed(tokens, index)
                if not act:
                    return False # something wrong do know what
                needs.append(act)
                if index < len(tokens):
                    connective = tokens[index]
                    if connective not in ['and']:
                        msg = "ParseError: Building verb '%s'. Bad connective '%s'" % \
                                                (command, connective)
                        raise excepting.ParseError(msg, tokens, index)
                    index += 1 #otherwise eat token

        except IndexError:
            msg = "ParseError: Building verb '%s'. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building verb '%s'. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if not needs: # no needs
            msg = "ParseError: Building verb '%s'. Missing need(s)" %\
                (command)
            raise excepting.ParseError(msg, tokens, index)

        # build beact
        for act in needs:
            self.currentFrame.addBeact(act)

        console.profuse("     Added beact,  '{0}', with needs:\n".format(command))
        for act in needs:
            console.profuse("       {0} with {1}\n".format(act.actor, act.parms))

        return True

    def buildDo(self, command, tokens, index):
        """
        Syntax:

        do kind [part ...] [as name [part ...]] [at context] [via inode]
               [with data]
               [from source]
               [per data]
               [for source]
               [cum data]
               [qua source]

        deed:
            name [part ...]

        kind:
            name [part ...]

        context:
            (native, benter, enter, recur, exit, precur, renter, rexit)

        inode:
            indirect

        data:
            direct

        source:
            [(value, fields) in] indirect



        do controller pid depth   --> controllerPIDDepth
        do arbiter switch heading  --> arbiterSwitchHeading

        do controller pid depth with foobar 1
        do controller pid depth from value in .max.depth


        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            kind = "" # deed class key in registry
            name = "" #specific name of deed instance
            inode = None
            parts = []
            parms = odict()
            inits = odict()
            ioinits = odict()
            prerefs = odict([('inits', odict()),
                             ('ioinits', odict()),
                             ('parms', odict()) ])
            connective = None
            context = self.currentContext

            while index < len(tokens):
                if (tokens[index] in ['as', 'at', 'via', 'with', 'from',
                                      'per', 'for', 'cum', 'qua' ]): # end of parts
                    break
                parts.append(tokens[index])
                index += 1 #eat token

            if parts:
                kind = "".join([part.capitalize() for part in parts]) #camel case

            while index < len(tokens): #options
                connective = tokens[index]
                index += 1

                if connective in ('as', ):
                    parts = []
                    while index < len(tokens): # kind parts end when connective
                        if tokens[index] in ['as', 'at', 'with', 'from' 'per',
                                             'for', 'cum', 'qua' ]: # end of parts
                            break
                        parts.append(tokens[index])
                        index += 1 #eat token

                    name =  "".join([part.capitalize() for part in parts]) #camel case
                    if not name:
                        msg = "ParseError: Building verb '%s'. Missing name for connective 'as'" % (command)
                        raise excepting.ParseError(msg, tokens, index)

                elif connective in ('at', ):
                    context = tokens[index]
                    index += 1
                    if context not in ActionContextValues:
                        msg = ("ParseError: Building verb '{0}'. Invalid context"
                        " '{1} for connective 'as'".format(command, context))
                        raise excepting.ParseError(msg, tokens, index)
                    context = ActionContextValues[context]

                elif connective in ('via', ):
                    inode, index = self.parseIndirect(tokens, index, node=True)

                elif connective in ('with', ):
                    data, index = self.parseDirect(tokens, index)
                    parms.update(data)

                elif connective in ('from', ):
                    srcFields, index = self.parseFields(tokens, index)
                    srcPath, index = self.parseIndirect(tokens, index)
                    prerefs['parms'][srcPath] = srcFields

                elif connective in ('per', ):
                    data, index = self.parseDirect(tokens, index)
                    ioinits.update(data)

                elif connective in ('for', ):
                    srcFields, index = self.parseFields(tokens, index)
                    srcPath, index = self.parseIndirect(tokens, index)
                    prerefs['ioinits'][srcPath] = srcFields

                elif connective in ('cum', ):
                    data, index = self.parseDirect(tokens, index)
                    inits.update(data)

                elif connective in ('qua', ):
                    srcFields, index = self.parseFields(tokens, index)
                    srcPath, index = self.parseIndirect(tokens, index)
                    prerefs['inits'][srcPath] = srcFields

                else:
                    msg = ("Error building {0}. Invalid connective"
                          " '{1}'.".format(command, connective))
                    raise excepting.ParseError(msg, tokens, index)

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if not kind:
            msg = "ParseError: Building verb '%s'. Missing kind for Doer." %\
                                (command)
            raise excepting.ParseError(msg, tokens, index)

        if kind not in doing.Doer.Registry: # class registration not exist
            msg = "ParseError: Building verb '%s'. No Deed of kind '%s' in registry" %\
                (command, kind)
            raise excepting.ParseError(msg, tokens, index)

        if inode:
            ioinits.update(inode=inode)  # via argument takes precedence over others
        if name:
            inits['name'] = name
        act = acting.Act(   actor=kind,
                            registrar=doing.Doer,
                            inits=inits,
                            ioinits=ioinits,
                            parms=parms,
                            prerefs=prerefs,
                            human=self.currentHuman,
                            count=self.currentCount)

        #context = self.currentContext
        if context == NATIVE:
            context = RECUR #what is native for this command

        if not self.currentFrame.addByContext(act, context):
            msg = "Error building %s. Bad context '%s'." % (command, context)
            raise excepting.ParseError(msg, tokens, index)

        console.profuse("     Added {0} '{1}' with parms '{2}'\n".format(
            ActionContextNames[context], act.actor, act.parms))

        return True

    def buildBid(self, command, tokens, index):
        """
        bid control tasker [tasker ...] [at period]
        bid control [me] [at period]
        bid control all [at period]

        control:
           (stop, start, run, abort, ready)

        tasker:
           (tasker, me, all)

        period:
            number
            indirectOne

        indirectOne:
            sharepath [of relative]
            (field, value) in sharepath [of relative]

        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            period = None  # no period provided
            sourcePath = None
            sourceField = None
            parms = odict([('taskers', []), ('period', None), ('sources', odict())])
            control = tokens[index]
            index +=1
            if control not in ['start', 'run', 'stop', 'abort', 'ready']:
                msg = "Error building {0}. Bad control = {1}.".format(command, control)
                raise excepting.ParseError(msg, tokens, index)

            taskers = []
            while index < len(tokens):
                if (tokens[index] in ['at']):
                    break  # end of taskers so do not eat yet

                tasker = tokens[index]
                index +=1

                self.verifyName(tasker, command, tokens, index)
                taskers.append(tasker) #resolve later

            if not taskers:
                taskers.append('me')

            while index < len(tokens):  # at option
                connective = tokens[index]
                index += 1

                if connective in ['at']:
                    # parse period direct or indirect
                    try:  #parse direct
                        period = max(0.0, Convert2Num(tokens[index]))  # period is number
                        index += 1  # eat token

                    except ValueError:  # parse indirect
                        sourceField, index = self.parseField(tokens, index)
                        sourcePath, index =  self.parseIndirect(tokens, index)

                else:
                    msg = ("Error building {0}. Invalid connective"
                          " '{1}'.".format(command, connective))
                    raise excepting.ParseError(msg, tokens, index)

            actorName = 'Want' + control.capitalize()
            if actorName not in wanting.Want.Registry:
                msg = "Error building  %s. No actor named %s." % (command, actorName)
                raise excepting.ParseError(msg, tokens, index)

            parms['taskers'] = taskers #resolve later
            parms['period'] = period
            parms['source'] = sourcePath
            parms['sourceField'] = sourceField
            act = acting.Act(   actor=actorName,
                                registrar=wanting.Want,
                                parms=parms,
                                human=self.currentHuman,
                                count=self.currentCount)

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        context = self.currentContext
        if context == NATIVE:
            context = ENTER #what is native for this command

        if not self.currentFrame.addByContext(act, context):
            msg = "Error building %s. Bad context '%s'." % (command, context)
            raise excepting.ParseError(msg, tokens, index)

        console.profuse("     Added {0} want '{1}' with parms '{2}'\n".format(
            ActionContextNames[context], act.actor, act.parms))

        return True

    def buildReady(self, command, tokens, index):
        """
           ready taskName

        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            tasker = tokens[index]
            index +=1

            self.verifyName(tasker, command, tokens, index)

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        native = BENTER
        self.makeFiat(tasker, 'ready', native, command, tokens, index)

        return True

    def buildStart(self, command, tokens, index):
        """
           start taskName

        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            tasker = tokens[index]
            index +=1

            self.verifyName(tasker, command, tokens, index)

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        native = ENTER
        self.makeFiat(tasker, 'start', native, command, tokens, index)

        return True

    def buildStop(self, command, tokens, index):
        """
           stop taskName

        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            tasker = tokens[index]
            index +=1

            self.verifyName(tasker, command, tokens, index)

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        native = EXIT
        self.makeFiat(tasker, 'stop', native, command, tokens, index)

        return True

    def buildRun(self, command, tokens, index):
        """
           run taskName

        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            tasker = tokens[index]
            index +=1

            self.verifyName(tasker, command, tokens, index)

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        native = RECUR
        self.makeFiat(tasker, 'run', native, command, tokens, index)

        return True

    def buildAbort(self, command, tokens, index):
        """
           abort taskName

        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            tasker = tokens[index]
            index +=1

            self.verifyName(tasker, command, tokens, index)

        except IndexError:
            msg = "Error building %s. Not enough tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "Error building %s. Unused tokens." % (command,)
            raise excepting.ParseError(msg, tokens, index)

        native = ENTER
        self.makeFiat(tasker, 'abort', native, command, tokens, index)

        return True

    def buildUse(self, command, tokens, index):
        """
        Not implemented yet
        """
        msg = " ".join(tokens)
        console.concise("{0}\n")
        return True


    def buildFlo(self, command, tokens, index):
        """
        Not implemented yet
        """
        msg = " ".join(tokens)
        console.concise("{0}\n")
        return True

    def buildTake(self, command, tokens, index):
        """
        Not implemented yet
        """
        msg = " ".join(tokens)
        console.concise("{0}\n")
        return True

    def buildGive(self, command, tokens, index):
        """
        Not implemented yet
        """
        msg = " ".join(tokens)
        console.concise("{0}\n")
        return True


#------------------
    def makeIncDirect(self, dstPath, dstFields, srcData):
        """Make IncDirect act

           method must be wrapped in appropriate try excepts
        """
        actorName = 'Inc' + 'Direct' #capitalize second word

        if actorName not in poking.Poke.Registry:
            msg = "ParseError: Can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        parms = {}

        parms['destination'] = dstPath #this is string
        parms['destinationFields'] = dstFields # this is a list
        parms['sourceData'] = srcData #this is an ordered dictionary

        act = acting.Act(   actor=actorName,
                            registrar=poking.Poke,
                            parms=parms,
                            human=self.currentHuman,
                            count=self.currentCount)


        msg = "     Created Actor {0} parms: ".format(actorName)
        for key, value in parms.items():
            msg += " {0} = {1}".format(key, value)
        console.profuse("{0}\n".format(msg))

        return act

    def makeIncIndirect(self, dstPath, dstFields, srcPath, srcFields):
        """Make IncIndirect act

           method must be wrapped in appropriate try excepts
        """
        actorName = 'Inc' + 'Indirect' #capitalize second word

        if actorName not in poking.Poke.Registry:
            msg = "ParseError: Goal can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        #actor = poking.Poke.Names[actorName]

        parms = {}
        parms['destination'] = dstPath #this is a share
        parms['destinationFields'] = dstFields #this is a list
        parms['source'] = srcPath #this is a share
        parms['sourceFields'] = srcFields #this is a list
        act = acting.Act(   actor=actorName,
                            registrar=poking.Poke,
                            parms=parms,
                            human=self.currentHuman,
                            count=self.currentCount)


        msg = "     Created Actor {0} parms: ".format(actorName)
        for key, value in parms.items():
            msg += " {0} = {1}".format(key, value)
        console.profuse("{0}\n".format(msg))

        return act

    def makeFramerGoal(self, name, tokens, index):
        """Goal to set goal name relative to current framer

           method must be wrapped in appropriate try excepts

           goal to data
           goal from source

           goal:
              name

           implied goal is framer.currentframer.goal.name value

           data:
              [value] value
              field value [field value ...]

           source:
              [(value, fields) in] indirect

        """
        #name is used as name of goal relative to current framer
        #create goal relative to current framer destination is goal
        dstPath = 'framer.' + 'me' + '.goal.' + name
        dstField = 'value'
        dstFields = [dstField]
        #required connective
        connective = tokens[index]
        index += 1

        if connective in ['to', 'with']: #data direct
            srcData, index = self.parseDirect(tokens, index)
            act = self.makeGoalDirect(dstPath, dstFields, srcData )

        elif connective in ['by', 'from']: #source indirect
            srcFields, index = self.parseFields(tokens, index)
            srcPath, index = self.parseIndirect(tokens, index)

            act = self.makeGoalIndirect(dstPath, dstFields, srcPath, srcFields)

        else:
            msg = "ParseError:  Unexpected connective '%s'" %\
                (connective)
            raise excepting.ParseError(msg, tokens, index)

        return act, index

    def makeGoalDirect(self, dstPath, dstFields, srcData):
        """Make GoalDirect act

           method must be wrapped in appropriate try excepts
        """
        actorName = 'Goal' + 'Direct' #capitalize second word

        if actorName not in goaling.Goal.Registry:
            msg = "ParseError: Goal can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        parms = {}
        parms['destination'] = dstPath #this is string
        parms['destinationFields'] = dstFields #this is list
        parms['sourceData'] = srcData #this is a dictionary

        act = acting.Act(   actor=actorName,
                            registrar=goaling.Goal,
                            parms=parms,
                            human=self.currentHuman,
                            count=self.currentCount)

        msg = "     Created Actor {0} parms: ".format(actorName)
        for key, value in parms.items():
            msg += " {0} = {1}".format(key, value)
        console.profuse("{0}\n".format(msg))

        return act

    def makeGoalIndirect(self, dstPath, dstFields, srcPath, srcFields):
        """Make GoalIndirect act

           method must be wrapped in appropriate try excepts
        """
        actorName = 'Goal' + 'Indirect' #capitalize second word

        if actorName not in goaling.Goal.Registry:
            msg = "ParseError: Goal can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        parms = {}
        parms['destination'] = dstPath #this is string
        parms['destinationFields'] = dstFields #this is a list
        parms['source'] = srcPath #this is a string
        parms['sourceFields'] = srcFields #this is a list

        act = acting.Act(   actor=actorName,
                            registrar=goaling.Goal,
                            parms=parms,
                            human=self.currentHuman,
                            count=self.currentCount)


        msg = "     Created Actor {0} parms: ".format(actorName)
        for key, value in parms.items():
            msg += " {0} = {1}".format(key, value)
        console.profuse("{0}\n".format(msg))

        return act

    def makeNeed(self, tokens, index):
        """
        Parse a need

        method must be wrapped in try except indexError
        method assumes already checked for currentStore
        method assumes already checked for currentFramer
        method assumes already checked for currentFrame

        Need forms:

        [not] need

        need:

            basic need:
                if state [comparison goal [+- tolerance]]

            simple need:
                if framerstate [re [(me, framername)]] comparison framergoal [+- tolerance]

                if framerstate re [me] is TBD  # not supported yet

            special need:

                if indirect is updated  [in frame (me, framename)]

                if taskername is (readied, started, running, stopped, aborted)

                if taskername is done

                if (aux auxname, any, all)
                   [in frame [(me, framename)][in framer [(me, framername)]]] is done

                if (aux auxname, any, all)
                   [in framer [(me, framername)]] is done

                if ([aux] auxname, any, all)
                   in frame [(me, framename)][in framer [(me, framername)]] is done

                if ([aux] auxname, any, all)
                   in framer [(me, framername)] is done


        state:
            [(value, field) in] indirect


        goal:
            value
            [(value, field) in] indirect

        indirect:
            path [[of relation] ...]

        comparison:
            (==, !=, <, <=, >=, >)

        tolerance:
            number (the absolute value is used)

        framerstate:
            (elapsed, recurred)

        framergoal:
            goal
            value
            [(value, field) in] indirect


        """
        kind = None
        negate = False

        if tokens[index] == 'not':
            negate = True
            index += 1 #eat token

        # find back end of current clause
        if 'and' in tokens[index:]:  # conjunction
            back = tokens[index:].index('and') + index + 1
        else:
            back = len(tokens)

        if 'is' in tokens[index:back]:  # check for 'is participle' form, special needs
            place = tokens[index:back].index('is') # is
            participle = tokens[index + place + 1]  # participle modifier to is

            if participle in ('done', ):
                kind = 'done'
                act, index = self.makeDoneNeed(kind, tokens, index)
            elif participle in ('readied', 'started', 'running', 'stopped', 'aborted'):
                kind = 'status'
                act, index = self.makeStatusNeed(kind, tokens, index)
            elif participle in ('updated', 'changed'):
                kind = participle[:-1]  # remove 'd' suffix
                act, index = self.makeMarkerNeed(kind, tokens, index)
            else:
                msg = "ParseError: Unexpected 'is' participle '%s' for need" %\
                                    (participle)
                raise excepting.ParseError(msg, tokens, index)

        else:  # either simple need  or basic need
            state, framer, index = self.parseFramerState(tokens, index)
            if state is not None:  # 're' clause present,  simple need
                if state not  in  ('elapsed', 'recurred'):
                    msg = "ParseError: Unsupported framer state '%s'" %\
                                        (state)
                    raise excepting.ParseError(msg, tokens, index)

                kind = state
                act, index = self.makeFramerNeed(kind, tokens, index)
                # in the future we could support framer need for a different framer
                # not me or current framer
                # currently ignoring framer, because only allow 'me' or currentFramer

            else:  # basic need with support for deprecated form of simple need
                simple = False  # found deprecated simple need form
                stateField, index = self.parseField(tokens, index)
                if stateField is None:  # no 'in' clause
                    state = tokens[index]  # look for bare framer state
                    if state in ('elapsed', 'recurred'):  # deprecated
                        index += 1
                        kind = state
                        simple = True
                        act, index = self.makeFramerNeed(kind, tokens, index)

                if not simple:  # basic need either path not elapsed,recurred or 'in' clause
                    statePath, index = self.parseIndirect(tokens, index)

                    #parse optional comparison
                    comparison, index = self.parseComparisonOpt(tokens,index)

                    if not comparison: #no comparison so make a boolean need
                        act = self.makeBoolenNeed(statePath, stateField)

                    else: #valid comparison so required goal
                        #parse required goal
                        direct, goal, goalPath, goalField, index = \
                               self.parseNeedGoal(statePath, stateField, tokens, index)

                        #parse optional tolerance
                        tolerance, index = self.parseTolerance(tokens, index)

                        if direct: #make a direct need
                            act = self.makeDirectNeed(statePath,
                                                      stateField,
                                                      comparison,
                                                      goal,
                                                      tolerance)

                        else: #make an indirect need
                            act = self.makeIndirectNeed(statePath,
                                                        stateField,
                                                        comparison,
                                                        goalPath,
                                                        goalField,
                                                        tolerance)

        if negate:
            act = acting.Nact(actor=act.actor,
                              registrar=act.registrar,
                              parms=act.parms,
                              human=self.currentHuman,
                              count=self.currentCount)

        return (act, index)

    def makeDoneNeed(self, kind, tokens, index):
        """
        Need to check if tasker completed by .done truthy
            method must be wrapped in appropriate try excepts

        Syntax:
            if taskername is done

            if (aux auxname, any, all)
                [in frame [(me, framename)][in framer [(me, framername)]]] is done

            if (aux auxname, any, all)
               [in framer [(me, framername)]] is done

            if ([aux] auxname, any, all)
               in frame [(me, framename)][in framer [(me, framername)]] is done

            if ([aux] auxname, any, all)
               in framer [(me, framername)] is done

        """
        frame = ""  # name of frame where aux resides if applicable
        framer = ""  # name of framer where aux resides if applicable
        auxed = False  # one of the auxiliary forms

        tasker = tokens[index]

        if tasker in ('any', 'all'):  # auxilary case applicable so default
            index += 1
            auxed = True
            framer = 'me'
            frame = 'me'

        elif tasker == "aux":
            index += 1
            auxed = True
            framer = 'me'
            tasker = tokens[index]
            self.verifyName(tasker, kind, tokens, index)
            index += 1
        else:
            self.verifyName(tasker, kind, tokens, index)
            index += 1

        # in clause existence means auxilary case
        # optional in clauses followed by is clause
        connective = tokens[index]
        if connective == 'in':  # optional 'in frame [(me, framename)]' clause
            index += 1  # eat 'in' connective
            auxed = True
            framer = 'me'
            place = tokens[index]  # required place frame or framer
            index += 1  # eat place token

            if place == 'framer':
                connective = tokens[index]
                if connective not in Reserved:  # assume must be name
                    framer = connective
                    self.verifyName(framer, kind, tokens, index)
                    index += 1
                    connective = tokens[index]  # set up for next clause

            elif place == 'frame':
                frame = 'me'
                connective = tokens[index]
                if connective not in Reserved:  # assume must be name
                    frame = connective
                    self.verifyName(frame, kind, tokens, index)
                    index += 1
                    connective = tokens[index]  # setup for next clause

                if connective == 'in':  # optional 'in framer [(me, framername)]' clause
                    index += 1  # eat 'in' connective
                    place = tokens[index]  # required place framer
                    index += 1  # eat place token

                    if place != 'framer':
                        msg = ("ParseError: Expected 'framer' got "
                               "'{0}'".format(place))
                        raise excepting.ParseError(msg, tokens, index)

                    connective = tokens[index]
                    if connective not in Reserved:  # assume must be name
                        framer = connective
                        self.verifyName(framer, kind, tokens, index)
                        index += 1
                        connective = tokens[index]  # setup for next clause

            else:
                msg = ("ParseError: Expected 'framer' or frame' got "
                       "'{0}'".format(place))
                raise excepting.ParseError(msg, tokens, index)

        if connective not in ('is', ):  # missing 'is'
            msg = ("ParseError: Expected 'is' connective got "
                                       "'{0}'".format(connective))
            raise excepting.ParseError(msg, tokens, index)
        index += 1  # eat 'is' connective token

        participle = tokens[index]
        index += 1
        if participle not in ('done', ):  # wrong 'participle'
            msg = ("ParseError: Expected 'done' participle got "
                                       "'{0}'".format(participle))
            raise excepting.ParseError(msg, tokens, index)


        # a frame of me is nonsensical if framer is not current framer
        if (frame == 'me' and
                not (framer == 'me' or framer == self.currentFramer.name)):
            msg = ("Error: Frame '{0}' nonsensical given"
                   " Framer '{1}'.".format(frame, framer))
            raise excepting.ParseError(msg, tokens, index)

        actorName = 'Need' + kind.capitalize()
        if auxed:
            actorName += 'Aux'
        if actorName not in needing.Need.Registry:
            msg = "ParseError: Need '%s' can't find actor named '%s'" %\
                (  kind, actorName)
            raise excepting.ParseError(msg, tokens, index)

        parms = {}
        parms['tasker'] = tasker
        parms['framer'] = framer
        parms['frame'] = frame
        act = acting.Act(actor=actorName,
                         registrar=needing.Need,
                         parms=parms,
                         human=self.currentHuman,
                         count=self.currentCount)

        return (act, index)

    def makeStatusNeed(self, kind, tokens, index):
        """
        Need to check if tasker named tasker status' is status

        method must be wrapped in appropriate try excepts

        Syntax:
            if taskername is (readied, started, running, stopped, aborted)

        """
        tasker = tokens[index]
        if not REO_IdentPub.match(tasker):
            msg = "ParseError: Invalid format of tasker name '%s'" % (tasker)
            raise excepting.ParseError(msg, tokens, index)
        index += 1

        connective = tokens[index]
        index += 1
        if connective not in ('is', ):
            msg = "ParseError: Need status invalid connective '%s'" %\
                (kind, connective)
            raise excepting.ParseError(msg, tokens, index)

        status = tokens[index]  # participle
        index += 1
        if status.capitalize() not in StatusValues:
            msg = "ParseError: Need status invalid status '%s'" %\
                (kind, status)
            raise excepting.ParseError(msg, tokens, index)
        status = StatusValues[status.capitalize()] #replace name with value

        actorName = 'Need' + kind.capitalize()

        if actorName not in needing.Need.Registry:
            msg = "ParseError: Need '%s' can't find actor named '%s'" %\
                (kind, actorName)
            raise excepting.ParseError(msg, tokens, index)

        parms = {}
        parms['tasker'] = tasker  #need to resolve this
        parms['status'] = status
        act = acting.Act(   actor=actorName,
                            registrar=needing.Need,
                            parms=parms,
                            human=self.currentHuman,
                            count=self.currentCount)
        return (act, index)

    def makeUpdateNeed(self, kind, tokens, index):
        """
        Need to check if share updated in frame

        method must be wrapped in appropriate try excepts

        Syntax:
            if path [[of relation] ...] is updated [in frame [(me, framename)]]
                    [by marker]

        """
        return (self.makeMarkerNeed(kind, tokens, index))

    def makeChangeNeed(self, kind, tokens, index):
        """
        Need to check if share updated in frame

        method must be wrapped in appropriate try excepts

        Syntax:
            if path [[of relation] ...] is changed [in frame [(me, framename)]]
                    [by marker]

        """
        return (self.makeMarkerNeed(kind, tokens, index))

    def makeMarkerNeed(self, kind, tokens, index):
        """
        Support method to make either NeedUpdate or NeedChange
            as determined by kind

        Syntax:
            if path [[of relation] ...] is (updated, changed)
                    [in frame [(me, framename)]] [by marker]

            sharepath:
                path [[of relation] ...]

            marker:
                string

        """
        frame = ""  # name of marked frame when empty resolve uses "me"" but no enact
        marker = ""

        sharePath, index = self.parseIndirect(tokens, index)

        connective = tokens[index]
        if connective not in ('is', ):
            msg = ("ParseError: Unexpected connective '{0}' not 'is', "
                    "while building need".format(connective))
            raise excepting.ParseError(msg, tokens, index)
        index += 1

        participle = tokens[index]
        if participle not in ('updated', 'changed' ):
            msg = ("ParseError: Unexpected 'is' participle '{0}', "
                    " not 'updated' or 'changed', "
                    "while building need".format(participle))
            raise excepting.ParseError(msg, tokens, index)
        index += 1

        # ensure kind and participle match
        if participle[:-1] != kind:  # remove 'd' suffix
            msg = ("ParseError: Mismatching participle. Expected '{0}' got "
                                       "'{1}'".format(kind + 'd', participle))
            raise excepting.ParseError(msg, tokens, index)

        while index < len(tokens):  # optional 'in frame'  clause
            connective = tokens[index]
            if connective not in ('in', 'by'):  # next need clause started
                break
            index += 1  # eat token for connective

            if connective == 'in':
                place = tokens[index] #need to resolve
                index += 1  # eat place token

                if place != 'frame':
                    msg = ("ParseError: Invalid "
                           " '{0}' clause. Expected 'frame' got "
                           "'{1}'".format(connective, place))
                    raise excepting.ParseError(msg, tokens, index)

                frame = "me"  # default if just frame but no framename

                if index < len(tokens): # frame name is optional
                    connective = tokens[index] #need to resolve
                    if connective not in Reserved:  # assume must be name
                        frame = connective  # only
                        if not REO_IdentPub.match(frame):
                            msg = "ParseError: Invalid format of frame name '%s'" % (frame)
                            raise excepting.ParseError(msg, tokens, index)
                        index += 1  # consume frame name token

            elif connective == 'by':
                marker = tokens[index]
                index += 1  # eat marker token
                marker = StripQuotes(marker)


        # assign marker type actual marker Act created in need's resolve
        markerKind = 'Marker' + kind.capitalize()

        actorName = 'Need' + kind.capitalize()
        if actorName not in needing.Need.Registry:
            msg = "ParseError: Need '%s' can't find actor named '%s'" %\
                (kind, actorName)
            raise excepting.ParseError(msg, tokens, index)

        parms = {}
        parms['share'] = sharePath
        parms['frame'] = frame  # marked frame name resolved in resolvelinks
        parms['kind'] = markerKind  # marker kind resolved in resolvelinks
        parms['marker'] = marker
        act = acting.Act(   actor=actorName,
                            registrar=needing.Need,
                            parms=parms,
                            human=self.currentHuman,
                            count=self.currentCount)
        return (act, index)

    def makeImplicitDirectFramerNeed(self, name, comparison, goal, tolerance):
        """Make implicit need, ie the need is not parsed but implied by the command
           such as timeout

           method must be wrapped in appropriate try excepts

           state comparison goal [+- tolerance]

           goal:
              value (direct number or string)

           state:
              name

           implied state is framer.currentframer.state.name value
        """
        console.profuse("     Making implicit direct framer need {0}\n".format(name))
        #name is used as name of state relative to current framer
        # and if implicit goal the name of goal relative to current framer
        #create state relative to framer
        statePath = 'framer.' + 'me' + '.state.' + name
        stateField = 'value'
        act = self.makeDirectNeed(statePath, stateField, comparison, goal, tolerance)

        return act

    def makeFramerNeed(self, name, tokens, index):
        """Need that checks if framer state name for current framer satisfies comparison

           method must be wrapped in appropriate try excepts

           state comparison goal [+- tolerance]

           state:
              name

           implied state is framer.currentframer.state.name value

           goal:
              goal
              from path [key]
              value
              dotpath [key]

           elapsed >= 25.0
           elapsed >= goal
           elapsed == goal +- 0.1

        """
        console.profuse("     Making framer need {0}\n".format(name))
        #name is used as name of state relative to current framer
        # and if implicit goal the name of goal relative to current framer
        #create state relative to framer
        statePath = 'framer.' + 'me' + '.state.' + name
        stateField = 'value'

        #parse required comparison
        comparison, index = self.parseComparisonReq(tokens,index)

        #parse required goal
        direct, goal, goalPath, goalField, index = \
                self.parseFramerNeedGoal(statePath, stateField, tokens, index)

        #parse optional tolerance
        tolerance, index = self.parseTolerance(tokens, index)

        if direct: #make a direct need
            act = self.makeDirectNeed(statePath,
                                      stateField,
                                      comparison,
                                      goal,
                                      tolerance)

        else: #make an indirect need
            act = self.makeIndirectNeed(statePath,
                                        stateField,
                                        comparison,
                                        goalPath,
                                        goalField,
                                        tolerance)

        return (act, index)

    def makeBoolenNeed(self, statePath, stateField):
        """Make booleanNeed act

           method must be wrapped in appropriate try excepts
        """
        actorName = 'Need' + 'Boolean' #capitalize second word

        if actorName not in needing.Need.Registry:
            msg = "ParseError: Need can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        parms = {}
        parms['state'] = statePath #this is a string
        parms['stateField'] = stateField #this is string
        act = acting.Act(   actor=actorName,
                            registrar=needing.Need,
                            parms=parms,
                            human=self.currentHuman,
                            count=self.currentCount)

        msg = "     Created Actor {0} parms: ".format(actorName)
        for key, value in parms.items():
            msg += " {0} = {1}".format(key, value)
        console.profuse("{0}\n".format(msg))

        return act

    def makeDirectNeed(self, statePath, stateField, comparison, goal, tolerance):
        """Make directNeed act

           method must be wrapped in appropriate try excepts
        """
        actorName = 'Need' + 'Direct' #capitalize second word

        if actorName not in needing.Need.Registry:
            msg = "ParseError: Need can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        parms = {}
        parms['state'] = statePath #this is a string
        parms['stateField'] = stateField #this is a string
        parms['comparison'] = comparison #this is a string
        parms['goal'] = goal  #this is a value: boolean number or string
        parms['tolerance'] = tolerance #this is a number
        act = acting.Act(   actor=actorName,
                            registrar=needing.Need,
                            parms=parms,
                            human=self.currentHuman,
                            count=self.currentCount)
        msg = "     Created Actor {0} parms: ".format(actorName)
        for key, value in parms.items():
            msg += " {0} = {1}".format(key, value)
        console.profuse("{0}\n".format(msg))

        return act

    def makeIndirectNeed(self,
                         statePath,
                         stateField,
                         comparison,
                         goalPath,
                         goalField,
                         tolerance):
        """Make indirectNeed act

           method must be wrapped in appropriate try excepts
        """
        actorName = 'Need' + 'Indirect' #capitalize second word

        if actorName not in needing.Need.Registry:
            msg = "ParseError: Need can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        parms = {}
        parms['state'] = statePath #this is string
        parms['stateField'] = stateField #this is a string
        parms['comparison'] = comparison #this is a string
        parms['goal'] = goalPath #this is a string
        parms['goalField'] = goalField #this is a string
        parms['tolerance'] = tolerance #this is a number

        msg = "     Created Actor {0} parms: ".format(actorName)
        for key, value in parms.items():
            msg += " {0} = {1}".format(key, value)
        console.profuse("{0}\n".format(msg))

        act = acting.Act(   actor=actorName,
                            registrar=needing.Need,
                            parms=parms,
                            human=self.currentHuman,
                            count=self.currentCount)

        return act

    def makeFiat(self, name, kind, native, command, tokens, index):
        """
           Assumes wrapped in currentFrame etc checks

           make a fiat action given the tasker name and fiat kind

        """
        actorName = 'Fiat' +  kind.capitalize()
        if actorName not in fiating.Fiat.Registry:
            msg = "Error building fiat %s. No actor named %s." % (kind, actorName)
            raise excepting.ParseError(msg, tokens, index)

        parms = {}
        parms['tasker'] = name #resolve later
        act = acting.Act(   actor=actorName,
                            registrar=fiating.Fiat,
                            parms=parms,
                            human=self.currentHuman,
                            count=self.currentCount)

        context = self.currentContext
        if context == NATIVE:
            context = native #The native context for this command

        if not self.currentFrame.addByContext(act, context):
            msg = "Error building %s. Bad context '%s'." % (command, context)
            raise excepting.ParseError(msg, tokens, index)

        console.profuse("     Added {0} fiat '{1}' with parms '{2}'\n".format(
            ActionContextNames[context], act.actor, act.parms))

        return True

    #----------------------------

    def parseDirect(self, tokens, index):
        """Parse Direct data address
           returns ordered dictionary of fields (keys) and values
           if no field provided then uses default field = 'value'

           parms:
              tokens = list of tokens for command
              index = current index into tokens

           returns:
              data ordered dict
              index

           method must be wrapped in appropriate try excepts

           Syntax:

           data:
              [value] value
              field value [field value ...]


           possible parsing end conditions:
              no more tokens (init,  set)
              token 'into'  (put)

        """
        data = odict()
        if index == (len(tokens) - 1): #only one more token so it must be value
            value = tokens[index]
            if value in Reserved:  # ending token not valid value
                msg = "ParseError: Encountered reserved '{0}' instead of value." % (value)
                raise excepting.ParseError(msg, tokens, index)
            index +=1 #eat token
            field = 'value' #default field

        else: #more than one so first may be field and second token may be value
            field = tokens[index]
            if field in Reserved:  # ending token not valid field
                msg = "ParseError: Encountered reserved '{0}' instead of field." % (field)
                raise excepting.ParseError(msg, tokens, index)
            index += 1
            value = tokens[index]
            if value in Reserved: #second reserved token so first token was value
                value = field
                field = 'value' #default field
            else: #first token was field and second value
                field = StripQuotes(field)
                index += 1 #eat token

        data[field] = Convert2StrBoolPathCoordPointNum(value) #convert to BoolNumStr, load data

        #parse rest if any
        while index < len(tokens): #must be in pairs unless first is ending token
            field = tokens[index]
            if field in Reserved: #ending token so break
                break

            field = StripQuotes(field)
            index += 1 #eat token

            value = tokens[index]
            if value in Reserved:  # ending token before valid value
                msg = "ParseError: Encountered reserved '{0}' instead of value." % (value)
                raise excepting.ParseError(msg, tokens, index)
            index += 1
            data[field] = Convert2StrBoolPathCoordPointNum(value) #convert to BoolNumStr, load data

        #prevent using multiple fields if one of them is 'value'
        if (len(data) > 1) and ('value' in data):
            msg = "ParseError: Direct data field = 'value' must be only field '%s'" % (data.keys)
            raise excepting.ParseError(msg, tokens, index)

        #prevent using incorrect format for fields
        for field in data:  # keys
            if not REO_IdentPub.match(field): #invalid format
                msg = "ParseError: Invalid field  = '%s'" % (field)
                raise excepting.ParseError(msg, tokens, index)

        return (data, index)


    def parseFields(self, tokens, index):
        """
        Parse optional field list for Indirect address

        parms:
           tokens = list of tokens for command
           index = current index into tokens

        returns:
           (fields,index)


        method must be wrapped in appropriate try excepts

        Syntax:

        [(value, fields) in] indirect

        fields:
           field [field ...]

        valid fields only when encounter token 'in' after fields
        consumes fields and the 'in' so subsequent parsePath starts with indirect path

        parsing end conditions that signify no fields
        if encounter before 'in':
           no more tokens
           reserved token

        """
        indexSave = index #save it since welookahead to see if "in"
        fields = []
        found = False #flag to indicate found 'in' wich indicates fields clause

        while index < len(tokens):  # provisionall parse for fields
            field = tokens[index]
            if field == 'in': #field list present and completed now we know
                index +=1
                found = True
                break

            if field in Reserved: #field list not present
                break

            index += 1 #eat token
            field = StripQuotes(field)
            fields.append(field)  # provisional

        if not found:  # no fields clause so we ignore
            index = indexSave #so restore index
            fields = [] #empty fields list

        #prevent using multiple fields if one of them is 'value'
        if (len(fields) > 1) and ('value' in fields):
            msg = "ParseError: Field = 'value' with multiple fields = '%s'" % (fields)
            raise excepting.ParseError(msg, tokens, index)

        for i, field in enumerate(fields):  # now we check if valid format
            if not REO_IdentPub.match(field):
                msg = "ParseError: Invalid format of field '%s'" % (field)
                raise excepting.ParseError(msg, tokens, index)

        return (fields, index)

    def parseField(self, tokens, index):
        """
        Parse optional field  for Indirect address

        parms:
           tokens = list of tokens for command
           index = current index into tokens

        returns:
           (field, index)

        method must be wrapped in appropriate try excepts

        Syntax:

        [(value, field) in] indirect

        valid field only when encounter token 'in' after first field
        consumes field and the 'in' so subsequent parsePath starts with indirect path

        parsing end conditions that signify no fields
        if encounter before 'in':
           no more tokens
           reserved token

        """
        indexSave = index #save it since welookahead to see if "in"
        fields = []
        found = False #flag to indicate found 'in' which indicates fields clause

        while index < len(tokens):
            field = tokens[index]
            if field == 'in': #field list present and completed
                index +=1
                found = True
                break

            if field in Reserved: #field list not present
                break

            index += 1 #eat token
            field = StripQuotes(field)
            fields.append(field)

        if not found: #no fields clause
            index = indexSave #so restore index
            fields = [] #empty fields list

        #prevent using multiple fields
        if (len(fields) > 1):
            msg = "ParseError: More than one field = '%s'" % (fields)
            raise excepting.ParseError(msg, tokens, index)

        if fields:
            field = fields[0]
            if not REO_IdentPub.match(field):
                msg = "ParseError: Invalid format of field '%s'" % (field)
                raise excepting.ParseError(msg, tokens, index)

        else:
            field = None

        return (field, index)

    def parsePath(self, tokens, index):
        """Parse required (path or dotpath) path
           Does not support relative path processing for verbs such as init or
           server which are not inside a framer context
           method must be wrapped in appropriate try excepts
        """
        path = tokens[index]
        index +=1

        if not REO_Path.match(path): #check if valid path
            msg = "ParseError: Invalid path '%s'" % (path)
            raise excepting.ParseError(msg, tokens, index)

        #path = path.lstrip('.') #remove leading dot if any

        return (path, index)


    def parseIndirect(self, tokens, index, node=False):
        """
        Parse Indirect data address
        If node then allow trailing dot in path


        parms:
           tokens = list of tokens for command
           index = current index into tokens

        returns:
           path
           index

        method must be wrapped in appropriate try excepts

        Syntax:

        indirect:
           absolute
           relative

        absolute:
           dotpath

        relative:
           root
           inode
           framer
           frame
           actor

        root:
           path [of root]

        inode:
           path of me

        framer:
           path of framer [name]

        frame:
           path of frame [name]

        actor:
           path of actor [name]

        """
        if node:
            reoDotPath = REO_DotPathNode
            reoRelPath = REO_RelPathNode
        else:
            reoDotPath = REO_DotPath
            reoRelPath = REO_RelPath

        path = tokens[index]
        index +=1

        if path in Reserved:
            msg = "ParseError: Invalid path '%s' using reserved" % (path)
            raise excepting.ParseError(msg, tokens, index)

        if reoDotPath.match(path): #valid absolute path segment
            #check for optional relation clause
            #if 'of relation' clause then allows relative but no
            #implied relation clauses
            relation, index = self.parseRelation(tokens, index)
            # dotpath starts with '.' no need to add

        elif reoRelPath.match(path): #valid relative path segment
            #get optional relation clause, default is root
            relation, index = self.parseRelation(tokens, index)

            chunks = path.split('.')
            if relation:  # check for relation conflict
                if chunks[0] in ['framer', 'frame', 'actor']:
                    if (chunks[0] == 'framer' or
                            (chunks[0] == 'frame' and  '.frame.' in relation) or
                            (chunks[0] == 'actor' and  '.actor.' in  relation)):
                        msg = ("ParseError: Relation conflict in path '{0}'"
                               " with relation '{1}'".format(path, relation))
                        raise excepting.ParseError(msg, tokens, index)
                    if relation == 'me':
                        msg = ("ParseError: Relation conflict in path '{0}'"
                              " with relation '{1}'".format(path, relation))
                        raise excepting.ParseError(msg, tokens, index)

            else: # prepend missing relations if partial relation in path
                if chunks[0] == 'actor':
                    if len(chunks) < 3: # actor name or share name missing
                        msg = ("ParseError: Incomplete path '{0}'. Actor name"
                               " or Share name missing given inline actor "
                               "relation".format(path))
                        raise excepting.ParseError(msg, tokens, index)
                    relation = 'framer.me.frame.me'
                elif chunks[0] == 'frame':
                    if len(chunks) < 3: # frame name or share name missing
                        msg = ("ParseError: Incomplete path '{0}'. Frame name"
                               " or Share name missing given inline frame "
                               "relation".format(path))
                        raise excepting.ParseError(msg, tokens, index)
                    framername = 'me'
                    if chunks[1] == 'main':
                        framername = 'main'
                    relation = 'framer.' + framername

            if relation:
                relation += '.' # add dot since not dotpath

        else: #invalid path format
            msg = "ParseError: Invalid path '{0}'".format(path)
            raise excepting.ParseError(msg, tokens, index)

        path = relation + path

        return (path, index)

    def parseRelation(self, tokens, index, framername=''):
        """
        Parse optional relation clause of relative data address

        parms:
            tokens = list of tokens for command
            index = current index into tokens
            framername = default framer name if not provided such as 'main'

        returns:
            relation
            index

        method must be wrapped in appropriate try excepts

        Syntax:

        relative:
            root
            inode
            framer
            frame
            actor

        root:
            path [of root]

        inode:
            path of me

        framer:
            path of framer [(me, main, name)]

        frame:
            path of frame [(me, main, name)]

        actor:
            path of actor [(me, name)]


        """
        relation = '' #default relation if none given
        if index < len(tokens): #are there more tokens
            connective = tokens[index]
            if connective == 'of': #of means relation given
                index += 1 #eat token
                relation = tokens[index]
                index +=1

                if relation not in ['root', 'me', 'framer', 'frame', 'actor']:
                    msg = "ParseError: Invalid relation '%s'" % (relation)
                    raise excepting.ParseError(msg, tokens, index)

                if relation == 'root':
                    relation = '' #nothing gets prepended for root relative
                elif relation == 'me':
                    pass # do nothing

            if relation in ['framer']: #may be optional name for framer
                name = '' #default name is empty
                if index < len(tokens): #more tokens to check for optional name
                    name = tokens[index]
                    if name not in Reserved: #name given
                        index += 1 #eat token

                        if not REO_IdentPub.match(name): #check if valid name
                            msg = "ParseError: Invalid relation %s name '%s'" %\
                                (relation, name)
                            raise excepting.ParseError(msg, tokens, index)
                    else:
                        name = ''

                if not name: #no name given so substitute default
                    name = framername or 'me'

                relation += '.' + name  #append name

            if relation in ['frame']: #may be optional name of frame
                name = '' #default name is empty
                if index < len(tokens): #more tokens to check for optional name
                    name = tokens[index]
                    if name not in Reserved: #name given
                        index += 1 #eat token

                        if not REO_IdentPub.match(name): #check if valid name
                            msg = "ParseError: Invalid relation %s name '%s'" %\
                                (relation, name)
                            raise excepting.ParseError(msg, tokens, index)
                    else:
                        name = ''

                if not name: #no name given so substitute default
                    name = 'me'

                relation += '.' + name  #append name

                # parse optional of framer relation
                framername = ''
                if name == 'main': # default framer for frame main is framer main
                    framername = 'main'

                framerRelation, index = self.parseRelation(tokens,
                                                           index,
                                                           framername=framername)

                # check if spurious, of frame or, of actor
                if (framerRelation and
                        ('.frame.' in framerRelation or
                         '.actor.' in framerRelation )):
                    msg = "ParseError: Invalid relation '%s' following frame relation" %\
                                                    (framerRelation)
                    raise excepting.ParseError(msg, tokens, index)

                if framerRelation:
                    relation = framerRelation + '.' + relation

                else: #use default framer
                    framername = framername or 'me'
                    relation = ('framer.' + framername + '.' + relation)

            if relation in ['actor']: #may be optional name of actor
                name = '' #default name is empty
                if index < len(tokens): #more tokens to check for optional name
                    name = tokens[index]
                    if name not in Reserved: #name given
                        index += 1 #eat token

                        if not REO_IdentPub.match(name): #check if valid name
                            msg = "ParseError: Invalid relation %s name '%s'" %\
                                (relation, name)
                            raise excepting.ParseError(msg, tokens, index)
                    else:
                        name = ''

                if not name: #no name given so substitute default
                    name = 'me'

                relation += '.' + name  #append name

                # parse optional of frame and hence framer relation
                frameRelation, index = self.parseRelation(tokens, index)

                # check if spurious, of framer or, of actor
                if (frameRelation and
                         '.actor.' in frameRelation ):
                    msg = "ParseError: Invalid relation '%s' following actor relation" %\
                                                    (frameRelation)
                    raise excepting.ParseError(msg, tokens, index)

                if frameRelation:
                    relation = frameRelation + '.' + relation

                else: #use default frame and framer
                    relation = ('framer.' + 'me.' + 'frame.' + 'me' + '.' + relation)

        return (relation, index)

    def parseComparisonOpt(self, tokens, index):
        """Parse a optional comparison

           method must be wrapped in appropriate try excepts
        """
        comparison = None
        if index < len(tokens): #at least one more token
                #if at least one more token could be connective or comparision
            comparison = tokens[index]
            if comparison in Comparisons: #
                index +=1 #so eat token
            else:
                comparison = None

        return (comparison, index)

    def parseComparisonReq(self, tokens, index):
        """Parse a required comparison

           method must be wrapped in appropriate try excepts
        """
        comparison = tokens[index]
        index +=1 #so eat token

        if comparison not in Comparisons: #
            msg = "ParseError: Need has invalid comparison '%s'" % (comparison)
            raise excepting.ParseError(msg, tokens, index)

        return (comparison, index)

    def parseFramerState(self, tokens, index):
        """Parse framer state expression

           parms:
              tokens = list of tokens for command
              index = current index into tokens

           returns:
              (state, framer, index)

           method must be wrapped in appropriate try excepts

           Syntax:

           state re [(me, framername)]

           valid state only when encounter token 're' after first state

           parsing end conditions that signify no state
           if encounter before 're':
              no more tokens
              reserved token
              multiple states

        """
        indexSave = index  # save it since we lookahead to see if "re"
        states = []
        found = False  # tag to indicate found 're'
        framer = None

        while index < len(tokens):
            connective = tokens[index]
            if connective == 're':  # state list completed
                index += 1  # eat 're' token
                found = True
                break  # do not append state == 're' to states

            if connective in Reserved: #field list not present
                break  # do not append state == reserved to states

            index += 1  # eat last state token
            state = StripQuotes(connective)  # candidate state since re os quotes ok
            states.append(state)  # save it

        if not found:  # no state clause 're'
            index = indexSave #so restore index
            states = [] #empty states list

        #prevent using multiple fields
        if (len(states) > 1):
            msg = "ParseError: More than one state = '%s'" % (states)
            raise excepting.ParseError(msg, tokens, index)

        if states:
            state = states[0]
            if not REO_IdentPub.match(state):
                msg = "ParseError: Invalid format of state '%s'" % (state)
                raise excepting.ParseError(msg, tokens, index)

        else:
            state = None

        if state is not None:  # get optional framer
            framer = 'me'
            while index < len(tokens):
                connective = tokens[index]
                if connective in Reserved:  # framer not present
                    break

                framer = connective
                if not REO_IdentPub.match(framer):
                    msg = "ParseError: Invalid format of framer name '%s'" % (framer)
                    raise excepting.ParseError(msg, tokens, index)

                if framer != 'me' and framer != self.currentFramer.name:
                    msg = "ParseError: Framer name '%s' for state need not current framer" % (framer)
                    raise excepting.ParseError(msg, tokens, index)

                index += 1

        return (state, framer, index)

    def parseNeedState(self, tokens, index):
        """Parse required need state

           method must be wrapped in appropriate try excepts
        """
        stateField, index = self.parseField(tokens, index)
        statePath, index = self.parseIndirect(tokens, index)
        return (statePath, stateField, index)

    def parseNeedGoal(self, statePath, stateField, tokens, index):
        """Parse required goal

           method must be wrapped in appropriate try excepts
        """
        goalPath = None #default
        goalField = None #default
        direct = False

        goal = tokens[index]
        #parse required goal
        try:
            goal = Convert2StrBoolCoordNum(tokens[index]) #goal is quoted string, boolean, or number
            index += 1 #eat token
            direct = True

        except ValueError: #means text is not (quoted string, bool, or number) so indirect
            goalField, index = self.parseField(tokens, index)
            goalPath, index =  self.parseIndirect(tokens, index)

        return (direct, goal, goalPath, goalField, index)

    def parseFramerNeedGoal(self, statePath, stateField, tokens, index):
        """
        Parse required goal for special framer need such as
           elapsed or recurred

        method must be wrapped in appropriate try excepts
        """
        goalPath = None #default
        goalField = None #default
        direct = False

        goal = tokens[index]
        #parse required goal
        try:
            goal = Convert2StrBoolCoordNum(tokens[index]) #goal is quoted string, boolean, or number
            index += 1 #eat token
            direct = True

        except ValueError: #means text is not (quoted string, bool, or number) so indirect
            if goal == 'goal': #means goal inferred by relative statePath
                index += 1 #eat token

                #now create goal path as inferred from state path
                #check if statePath can be interpreted  as  framer state relative
                chunks = statePath.strip('.').split('.')
                try:
                    if ((chunks[0] == 'framer') and
                         (chunks[2] == 'state')): #framer relative
                        chunks[2] = 'goal' # .framer.me.state becomes .framer.me.goal

                    else:
                        msg = "ParseError: Goal = 'goal' without framer state path '%s'" %\
                            (statePath)
                        raise excepting.ParseError(msg, tokens, index)

                except IndexError:
                    msg = "ParseError: Goal = 'goal' without framer state path '%s'" %\
                        (statePath)
                    raise excepting.ParseError(msg, tokens, index)

                goalPath = ".".join(chunks)
                goalField = stateField #goal field is the same as the given state field

            else: #not 'goal' so parse as indirect
                #is 'field in' clause present
                goalField, index = self.parseField(tokens, index)
                goalPath, index =  self.parseIndirect(tokens, index)

        return (direct, goal, goalPath, goalField, index)

    def parseTolerance(self, tokens, index):
        """Parse a optional tolerance

           method must be wrapped in appropriate try excepts
        """
        tolerance = 0

        if index < len(tokens): #at least one more token
                #if at least one more token could be connective
            connective = tokens[index]
            if connective == '+-': #valid tolerance connective
                index +=1 #so eat token
                tolerance = tokens[index] #get tolerance
                index += 1
                tolerance = Convert2Num(tolerance) #convert to value
                if isinstance(tolerance, str):
                    msg = "ParseError: Need has invalid tolerance '%s'" % (tolerance)
                    raise excepting.ParseError(msg, tokens, index)

        return (tolerance, index)

    def prepareSrcDstFields(self, src, srcFields, dst, dstFields, tokens, index):
        """
        Prepares and verifys a transfer of data
            from sourceFields in source
            to dstFields in dst
        Handles default conditions when fields are empty
            src and dst are shares
            fields are lists

        Ensure Actor._prepareSrcDstFields is the same
        """
        if not srcFields: #no source fields so assign defaults
            if src:
                if 'value' in src:
                    srcFields = ['value'] #use value field

                elif dstFields: #use destination fields for source fields
                    srcFields = dstFields

                else: #use pre-existing source fields
                    srcFields = src.keys()
                #else: #ambiguous multiple source fields
                #msg = "ParseError: Can't determine source field"
                #raise excepting.ParseError(msg, tokens, index)

            else:
                srcFields = ['value'] #use value field

        self.verifyShareFields(src, srcFields, tokens, index)

        if not dstFields: #no destination fields so assign defaults
            if 'value' in dst:
                dstFields = ['value'] #use value field

            else: #use source fields for destination fields
                dstFields = srcFields

        self.verifyShareFields(dst, dstFields, tokens, index)

        if len(srcFields) != len(dstFields):
            msg = "ParseError: Unequal number of source %s and destination %s fields" %\
                (srcFields, dstFields)
            raise excepting.ParseError(msg, tokens, index)

        for dstField, srcField in izip(dstFields, srcFields):
            if (dstField != srcField) and (srcField != 'value'):
                console.profuse("     Warning: Field names mismatch. '{0}' in {1} "
                                "from '{2}' in {3}  ... creating anyway".format(
                                    dstField, dst.name, srcField, src.name))

        #create any non existent source or destination fields
        for field in srcFields: #use source fields for source data
            if field not in src:
                console.profuse("     Warning: Transfer from non-existent field '{0}' "
                        "in share {1} ... creating anyway".format(field, src.name))
                src[field] = None #create

        for field in dstFields: #use destination fields for destination data
            if field not in dst:
                console.profuse("     Warning: Transfer into non-existent field '{0}' "
                        "in share {1} ... creating anyway\n".format(field, dst.name))
                dst[field] = None #create

        return (srcFields, dstFields)

    def prepareDataDstFields(self, data, dataFields, dst, dstFields, tokens, index):
        """
        Prepares and verifys a transfer of data
            from dataFields in data
            to dstFields in dst
        Handles default conditions when fields are empty
            data is dict
            dst is share
            fields are lists

        Ensure Actor._prepareDstFields is similar
        """

        if not dstFields: #no destinationField so use default rules
            if 'value' in dst:
                dstFields = ['value'] #use value field

            else: #use dataField
                dstFields = dataFields

        self.verifyShareFields(dst, dstFields, tokens, index)

        if len(dataFields) != len(dstFields):
            msg = "ParseError: Unequal number of source %s and destination %s fields" %\
                (dataFields, dstFields)
            raise excepting.ParseError(msg, tokens, index)

        for dstField, dataField in izip(dstFields, dataFields):
            if (dstField != dataField) and (dataField != 'value'):
                console.profuse("     Warning: Field names mismatch. '{0}' in {1} "
                                "from '{2}' ... creating anyway".format(
                                  dstField, dst.name, dataField))

        #create any non existent destination fields
        for field in dstFields: #use destination fields for destination data
            if field not in dst:
                console.profuse("     Warning: Transfer into non-existent field '{0}' in "
                       "share {1} ... creating anyway\n".format(field, dst.name))
                dst[field] = None #create

        return (dataFields, dstFields)

    def verifyShareFields(self, share, fields, tokens, index):
        """
        Verify that updating fields in share won't violate the
           condition that when a share has field == 'value'
           it will be the only field

           fields is list of field names
           share is  share

        raises exception if condition would be violated

        Ensure Actor._verifyShareFields is same
        """
        if (len(fields) > 1) and ('value' in fields):
            msg = "ParseError: Field = 'value' within fields = '%s'" % (fields)
            raise excepting.ParseError(msg, tokens, index)

        if share: #does share have fields already
            for field in fields:
                if field not in share: #so this field could be added to share
                    if ('value' in share) or (field == 'value'):
                        msg = "ParseError: Candidate field '%s' when fields = '%s' exist" %\
                            (field, share.keys())
                        raise excepting.ParseError(msg, tokens, index)

        return

    def validShareFields(self, share, fields):
        """Validates that updating fields in share won't violate the
           condition that when a share has field = 'value'
           it will be the only field

           fields is list of field names
           share is share

           returns False if condition would be violated
           return True otherwise
        """
        if (len(fields) > 1) and ('value' in fields):
            return False

        if share: #does share have fields already
            for field in fields:
                if field  not in share: #so this field could be added to share
                    if ('value' in share) or (field == 'value'):
                        return False

        return True

    def verifyCurrentContext(self, tokens, index):
        """Verify that parse context has
           currentStore
           currentFramer
           currentFrame

           If not raises ParseError
        """
        if not self.currentStore:
            msg = "ParseError: Building verb '%s'. No current store" % (tokens)
            raise excepting.ParseError(msg, tokens, index)

        if not self.currentFramer:
            msg = "ParseError: Building verb '%s'. No current framer" % (tokens)
            raise excepting.ParseError(msg, tokens, index)

        if not self.currentFrame:
            msg = "ParseError: Building verb '%s'. No current frame" % (tokens)
            raise excepting.ParseError(msg, tokens, index)

        return

    def verifyName(self, name, command, tokens, index):
        """Verify that name is a valid public identifyer
           Used for Tasker, Framer, and Frame names
        """
        if not REO_IdentPub.match(name) or name in Reserved: #bad name
            msg = "ParseError: Building verb '%s'. Invalid entity name '%s'" %\
                (command, name)
            raise excepting.ParseError(msg, tokens, index)

    #------------------------

def DebugShareFields(store, name):
    """ prints out  fields of share named name from store for debugging """

    share = store.fetch(name)
    if share is not None:
        console.terse("++++++++ Debug share fields++++++++\n{0} = {1}\n".format(
                share.name, share.items))


def Test(fileName = None, verbose = False):
    """Module self test



    """
    import globaling
    import aiding

    import excepting
    import registering

    import storing
    import skedding
    import tasking

    import acting
    import poking
    import needing
    import goaling

    import traiting
    import fiating
    import wanting
    import completing
    import doing
    import arbiting
    import controlling

    import framing
    import logging
    import interfacing
    import housing
    #import building
    import monitoring
    import testing

    allModules = [globaling, aiding, excepting, registering,  storing, skedding,
                  acting, poking, goaling, needing, traiting,
                  fiating, wanting, completing,
                  doing, arbiting, controlling,
                  tasking, framing, logging, interfacing, serving,
                  housing, monitoring, testing]


    if not fileName:
        fileName = "mission.txt"

    b = Builder()
    if b.build(fileName = fileName):
        houses = b.houses
        for house in houses:
            house.store.changeStamp(0.0)
            for framer in house.actives:
                status = framer.runner.send(START)
            for tasker in house.taskers:
                status = tasker.runner.send(START) #prepares logs and reopens files


        done = False
        while not done:
            done = True
            for house in houses:
                actives = []
                for framer in house.actives:
                    #status = framer.status
                    desire = framer.desire
                    if desire is not None:
                        control = desire
                    else:
                        control = RUN

                    status = framer.runner.send(control)
                    console.terse("Framer {0} control {1} resulting status = {2}\n".format(
                            framer.name, ControlNames[control], StatusNames[status]))
                    if not (status == STOPPED or status == ABORTED):
                        actives.append(framer)
                        done = False

                house.actives = actives
                for tasker in house.taskers:
                    status = tasker.runner.send(RUN)
                house.store.advanceStamp(0.125)


        for house in houses:
            for tasker in house.taskers:
                status = tasker.runner.send(STOP) # closes files

    return b

if __name__ == "__main__":
    Test()
