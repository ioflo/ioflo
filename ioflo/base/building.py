"""building.py build frameworks from mission files

"""
from __future__ import with_statement

#print "module %s" % __name__

import time
import re
import importlib

from collections import deque
from itertools import izip


from .odicting import odict
from .globaling import *

from . import excepting
from . import registering

from . import storing 
from . import housing

from . import acting
from . import poking
from . import needing
from . import goaling
from . import deeding

from . import traiting
from . import fiating
from . import wanting
from . import completing

from . import tasking
from . import framing
from . import logging
from . import serving

from .. import trim

from .consoling import getConsole
console = getConsole()


def Convert2Num(text):
    """converts text to python type in order
       Int, hex, Float, Complex
       ValueError if can't
    """
    #convert to number if possible
    try:
        value = int(text, 10)
        return value
    except ValueError, ex1:
        pass

    try:
        value = int(text, 16)
        return value
    except ValueError, ex1:
        pass

    try:
        value = float(text)
        return value
    except ValueError, ex1:
        pass

    try:
        value = complex(text)
        return value
    except ValueError, ex1:
        pass

    raise ValueError, "Expected Number got '%s'" % (text) 

    return None 


def Convert2CoordNum(text):
    """converts text to python type in order
       FracDeg, Int, hex, Float, Complex
       ValueError if can't
    """
    #convert to FracDeg Coord if possible
    dm = REO_LatLonNE.findall(text) #returns list of tuples of groups [(deg,min)]
    if dm:
        deg = float(dm[0][0])
        min = float(dm[0][1])
        return (deg + min/60.0)

    dm = REO_LatLonSW.findall(text) #returns list of tuples of groups [(deg,min)]
    if dm:
        deg = float(dm[0][0])
        min = float(dm[0][1])
        return (-(deg + min/60.0))

    try:
        return (Convert2Num(text))
    except ValueError:
        raise ValueError, "Expected CoordNum got '%s'" % (text) 


def Convert2BoolCoordNum(text):
    """converts text to python type in order
       Boolean, Int, Float, Complex
       ValueError if can't
    """
    #convert to boolean if possible
    if text.lower() in ['true', 'yes']:
        return (True)
    if text.lower() in ['false', 'no']:
        return (False)

    try:
        return (Convert2CoordNum(text))
    except ValueError:
        raise ValueError, "Expected BoolCoordNum got '%s'" % (text) 

    return None 


def Convert2StrBoolCoordNum(text):
    """converts text to python type in order
       Boolean, Int, Float, complex or double quoted string
       ValueError if can't
    """

    if REO_Quoted.match(text): #text is double quoted string
        return text.strip('"')  #strip off quotes

    try:
        return (Convert2BoolCoordNum(text))
    except ValueError:
        raise ValueError, "Expected StrBoolNum got '%s'" % (text)

    return None 

CommandList = ['load', 'house', 'init', 
               'tasker', 'server', 'logger', 'log', 'loggee',
               'framer', 'first', 
               'frame', 'over', 'under', 'next', 'done', 'timeout', 'repeat', 
               'native', 'benter', 'enter', 'recur', 'exit', 'precur', 'renter', 'rexit',
               'print', 'put', 'inc', 'copy', 'set',
               'aux',
               'go', 'let', 
               'do', 
               'bid', 'ready', 'start', 'stop', 'run', 'abort', 
               'use', 'flo', 'give', 'take' ]



Comparisons = ['==', '<', '<=', '>=', '>', '!='] #reserved tokens
Connectives = ['to', 'from', 'per', 'with', 'as', 'into', 'by', 'and', 'not',
                '+-', 'go', 'in', 'of', 'on'] #reserved tokens
Reserved = Connectives + Comparisons #concatenate to get reserved words
ReservedFrameNames = ['next'] #these frame names have special meaning as goto target


class Builder(object):
    """

    """
    def __init__(self, fileName='', mode=None, metaData=None, behavior=''):
        """

        """
        self.fileName = fileName #initial name of file to start building from
        self.mode = mode or []
        self.metaData = metaData or {}
        self.behavior = behavior
        self.files = [] #list of open file objects, appended to by load commands
        self.counts = [] #list of linectr s for open file objects

        self.houses = [] #list of houses

        self.currentFile = None
        self.currentCount = 0
        self.currentMode = None #None is any
        self.currentHouse = None
        self.currentStore = None
        self.currentLogger = None
        self.currentLog = None
        self.currentFramer = None
        self.currentFrame = None #current frame
        self.currentContext = NATIVE
        


    def build(self, fileName='', mode=None, metaData=None, behavior=''):
        """
           Allows building from multiple files. Essentially files list is stack of files
           fileName is name of first file. Load commands in any files push (append) file onto files
           until file completed loaded and then popped off

           Each house's store is inited with the metaData
        """
        #overwrite default if truthy argument
        if fileName: 
            self.fileName = fileName
        if mode:
            self.mode = mode
        if metaData:
            self.metaData = metaData
        if behavior:
            self.behavior = behavior
            
        if self.behavior: #import exterior behavior package/modules
            pass

        housing.House.Clear() #clear house registry
        housing.ClearRegistries() #clear all the other registries

        lineView = ''

        try: #IOError
            self.currentFile = open(self.fileName,"r+")
            self.currentCount = 0

            try: #ResolveError
                while self.currentFile:
                    line = self.currentFile.readline() #empty if end of file
                    self.currentCount  += 1 #inc line counter

                    while (line):
                        saveLines = []
                        saveLineViews = []

                        while line.endswith('\\\n'): #continuation
                            line = line.rstrip()
                            saveLineViews.append("%04d %s" % (self.currentCount, line))
                            saveLines.append(line.rstrip('\\').strip())
                            line = self.currentFile.readline() #empty if end of file
                            self.currentCount  += 1 #inc line counter                     

                        line = line.rstrip()
                        saveLineViews.append("%04d %s" % (self.currentCount, line))
                        saveLines.append(line)
                        lineView = "\n".join(saveLineViews)
                        line = " ".join(saveLines)               

                        console.concise(lineView + '\n')

                        line = line.strip() #strips white space both ends

                        chunks = REO_Chunks.findall(line) # removes trailing comments
                        tokens = []
                        for chunk in chunks:
                            if chunk[0] == '#': #throw out whole line as comment
                                break
                            else:
                                tokens.append(chunk)

                        if (not tokens):  #empty line or comment only
                            line = self.currentFile.readline() #empty if end of file
                            self.currentCount  += 1 #inc line counter
                            continue
                        #above guarantees at least 1 token

                        try: #ParseError ParseWarning
                            if not self.dispatch(tokens):
                                console.terse("Script Parsing stopped at line {0} in file {1}\n".format(
                                    self.currentCount, self.currentFile.name))
                                console.terse(lineView + '\n')
                                return False

                        except excepting.ParseError as ex1:
                            console.terse("\n{0}\n\n".format(ex1))
                            console.terse("Script line {0} in file {1}\n".format(
                                self.currentCount, self.currentFile.name))
                            console.terse(lineView + '\n')
                            raise

                        #dispatch evals commands. self.currentFile may be changed by load command
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
                    console.terse("Ordering taskable taskers for house {0}\n".format(house.name))
                    house.orderTaskables()

                    console.terse("Resolving links for house %s".format(house.name))
                    house.resolveLinks()

                    console.terse("Tracing outlines for house {0}".format(house.name))
                    house.traceOutlines() #traces the outlines in each frame

                    if console._verbosity >= console.Wordage.concise:
                        house.showAllTaskers()

                        #show framework hierarchiy
                        for framer in house.framers:
                            framer.showHierarchy()

                        #show hierarchy of each house's store
                        console.concise( "\nData Store for {0}\n".format(house.name))
                        house.store.expose() 

                return True

            except excepting.ResolveError, ex1:
                console.terse("{0}\n".format(ex1))
                return False


        except IOError as ex1:
            console.terse("Error opening mission file  {0}\n".format(ex1))
            return False

        finally:
            for f in self.files:
                if not f.closed:
                    f.close()


    def dispatch(self, tokens):
        """Converts command into build method name  and calls it"""

        command = tokens[0]
        index = 1
        if command not in CommandList:
            msg = "ParseError: Building {0}. Unknown command {1}, index = {2} tokens = {3}".format(
                     command, command, index, tokens)
            raise excepting.ParseError(msg, tokens, index)
        
        commandMethod = 'build' + command.capitalize()
        if hasattr(self, commandMethod):
            return(getattr(self, commandMethod )(command, tokens, index))
        else:
            return self.buildGeneric(command, tokens, index)


    def buildGeneric(self, command, tokens, index):
        """Called with no build method exists for a command """
        msg = "ParseError: No build method for command {0}.".format(command)
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

            self.currentFile = open(name,"r+")
            self.currentCount = 0
            console.terse("Loading from file (0).\n".format(self.currentFile.name))

        except IndexError:
            msg = "ParseError: Building command '%s'. Not enough tokens" % (command)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building command '%s'. Unused tokens after index" %\
                (command)
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

            console.terse("     Created house {0}. Assigning registries, "
                          "creating instances ...\n".format(name))

            self.currentHouse.assignRegistries()

            from .. import CreateAllInstances, _InstanceModules # ioflo/__init__.py
            CreateAllInstances(self.currentHouse.store, _InstanceModules)

            console.profuse("     Clearing current Framer, Frame, Log etc.\n")
            #changed store so need to make new frameworks and frames
            self.currentFramer = None #current framer
            self.currentFrame = None #current frame
            self.currentLogger = None #current logger
            self.currentLog = None #current log

            #metaData here triples of name, path, data
            for name, path, data in self.metaData:
                self.currentHouse.meta[name] = self.initPathToData(path, data)
            
            # set meta.name to house.name
            self.currentHouse.meta['name'] = self.initPathToData('.meta.name',
                    odict(value=self.currentHouse.name))
            
        except IndexError:
            msg = "ParseError: Building command '%s'. Not enough tokens" % (command)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building command '%s'. Unused tokens after index" %\
                (command)
            raise excepting.ParseError(msg, tokens, index)            
        
        msg = "     Built house {0} with meta:\n".format(self.currentHouse.name)
        for name, share in self.currentHouse.meta.items():
            msg += "       {0}: {1!r}\n".format(name, share)
        console.terse(msg)        

        return True

    # Convenince Functions

    def initPathToData(self, path, data):
        """Convenience support function to preload metadata.
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

           init destination to data

           destination:
              absolute
              path

           data:
              direct

           init destination from source

           destination:
              [(value, fields) in] absolute
              [(value, fields) in] path

           source:
              [(value, fields) in] absolute
              [(value, fields) in] path

        """
        if not self.currentStore:
            msg = "ParseError: Building command '%s'. No current store" % (command)
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

            if connective == 'to':
                if destinationFields: #fields not allowed so error
                    msg = "ParseError: Building command '%s'. Unexpected fields '%s in' clause " %\
                        (command, destinationFields)
                    raise excepting.ParseError(msg, tokens, index)

                data, index = self.parseDirect(tokens, index)

                #prevent init value and non value fields in same share
                self.verifyShareFields(destination, data.keys(), tokens, index)

                destination.update(data)
                console.profuse("     Inited share {0} to data = {1}\n".format(destination.name, data))

            elif connective == 'from':
                sourceFields, index = self.parseFields(tokens, index)
                sourcePath, index = self.parsePath(tokens, index)

                source = self.currentStore.fetchShare(sourcePath)
                if source is None:
                    msg = "ParseError: Building command '%s'. Nonexistent source share '%s'" %\
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
                msg = "ParseError: Building command '%s'. Unexpected connective '%s'" %\
                    (command, connective)
                raise excepting.ParseError(msg, tokens, index)

        except IndexError:
            msg = "ParseError: Building command '%s'. Not enough tokens" % (command)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building command '%s'. Unused tokens after index" %\
                (command)
            raise excepting.ParseError(msg, tokens, index)

        return True

    def buildTasker(self, command, tokens, index):
        """create tasker in current house
           tasker has to have name so can  ask stop

           tasker name [modifier ...] [as kind [modifier ...]][at period] [be scheduled]
              [in order][with [field] value] [from field [field ...] in share]

           scheduled: (active, inactive, slave)

           order:
              (front, mid, back)

           data:
              direct

           source:
              [(value, fields) in] indirect
        """
        if not self.currentHouse:
            msg = "ParseError: Building command '%s'. No current house" % (command)
            raise excepting.ParseError(msg, tokens, index)      

        if not self.currentStore:
            msg = "ParseError: Building command '%s'. No current store" % (command)
            raise excepting.ParseError(msg, tokens, index)

        try:
            parms = {}
            init = {}
            parts = []
            name = ''
            kind = None
            connective = None
            period = 0.0 
            prefix = './'
            schedule = ACTIVE #globaling.py
            order = MID #globaling.py

            name = tokens[index]
            index +=1         

            while index < len(tokens): # name parts end when connective
                if tokens[index] in ['as', 'at', 'be', 'in', 'with', 'per']: # end of parts
                    break
                parts.append(tokens[index])
                index += 1 #eat token

            name += "".join(part.capitalize() for part in parts)

            while index < len(tokens): #options 
                connective = tokens[index]
                index += 1

                if connective == 'as':
                    parts = []
                    while index < len(tokens): # kind parts end when connective
                        if tokens[index] in ['as', 'at', 'be', 'in', 'with', 'per']: # end of parts
                            break
                        parts.append(tokens[index])
                        index += 1 #eat token

                    #kind = "".join(part.capitalize() for part in parts)
                    kind =  "".join(parts[0:1] + [part.capitalize() for part in parts[1:]]) #camel case lower first
                    if not kind:
                        msg = "ParseError: Building command '%s'. Missing kind for connective 'as'" % (command)
                        raise excepting.ParseError(msg, tokens, index)                                     

                elif connective == 'at':
                    period = abs(Convert2Num(tokens[index]))
                    index +=1

                elif connective == 'be':
                    option = tokens[index]
                    index +=1

                    if option not in ['active', 'inactive', 'slave']:
                        msg = "ParseError: Building command '%s'. Bad server scheduled option got %s" % \
                            (command, option)
                        raise excepting.ParseError(msg, tokens, index)                   

                    schedule = ScheduleValues[option] #replace text with value

                elif connective == 'in':
                    order = tokens[index]
                    index +=1
                    if order not in OrderValues:
                        msg = "ParseError: Building command '%s'. Bad order option got %s" % \
                            (command, order)
                        raise excepting.ParseError(msg, tokens, index)                   

                    order = OrderValues[order] #convert to order value

                elif connective == 'per':
                    data, index = self.parseDirect(tokens, index)
                    init.update(data)

                elif connective == 'with': 
                    srcFields, index = self.parseFields(tokens, index)
                    srcPath, index = self.parsePath(tokens, index)
                    if self.currentStore.fetchShare(srcPath) is None:
                        console.terse("     Warning: Do 'with' non-existent share {0} ..."
                                      " creating anyway".format(srcPath))
                    src = self.currentStore.create(srcPath)
                    #assumes src share inited before this line parsed
                    for field in srcFields:
                        init[field] = src[field]

                else:
                    msg = "ParseError: Building command '%s'. Bad connective got %s" % \
                        (command, connective)
                    raise excepting.ParseError(msg, tokens, index)                   

        except IndexError:
            msg = "ParseError: Building command '%s'. Not enough tokens" % (command)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building command '%s'. Unused tokens after index" %\
                (command)
            raise excepting.ParseError(msg, tokens, index)      

        if kind: # Create new instance from kind class with name
            if name in tasking.Tasker.Names:
                msg = "ParseError: Building command '%s'. Task named %s of kind %s already exists" % \
                    (command, name, kind)
                raise excepting.ParseError(msg, tokens, index)

            if kind not in tasking.Tasker.Names: # expect instance of same name as kind
                msg = "ParseError: Building command '%s'. No tasker kind of %s" %\
                    (command, kind)
                raise excepting.ParseError(msg, tokens, index)

            kinder = tasking.Tasker.Names[kind]
            #create new instance as the same type as kinder
            tasker = type(kinder)(name=name, store=self.currentStore, period=period,
                                  schedule=schedule)
            kw = dict()
            kw.update(init)
            tasker.reinit(**kw)         

        else: # Use an existing instance
            if name not in tasking.Tasker.Names: #instance not exist
                msg = "ParseError: Building command '%s'. No tasker named %s" %\
                    (command, name)
                raise excepting.ParseError(msg, tokens, index)

            tasker = tasking.Tasker.Names[name] #fetch existing instance
            kind = tasker.__class__.__name__

            if tasker in self.currentHouse.taskers: #tasker already used somewhere else
                msg = "ParseError: Building command '%s'. Task named %s of kind %s already scheduled" %\
                    (command, name, kind)
                raise excepting.ParseError(msg, tokens, index)             

            kw = dict(period=period, schedule=schedule)
            kw.update(init)
            tasker.reinit(**kw)

        self.currentHouse.taskers.append(tasker)
        if schedule == SLAVE:
            self.currentHouse.slaves.append(tasker)
        else: #taskable active or inactive
            if order == FRONT:
                self.currentHouse.fronts.append(tasker)
            elif order == BACK:
                self.currentHouse.backs.append(tasker)
            else:
                self.currentHouse.mids.append(tasker)

        msg = "     Created tasker named {0} of kind {1} at period {2:0.4f} be {3}\n".format(
            tasker.name, kind, tasker.period,  ScheduleNames[tasker.schedule])
        console.profuse(msg)       

        return True

    def buildServer(self, command, tokens, index):
        """create server tasker in current house
           server has to have name so can  ask stop

           server name [part ...] [as kind [part ...]] [at period] [be scheduled]
           [rx shost:sport] [tx dhost:dport] [in order] [to prefix] [with data]
           [from source]

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
            msg = "ParseError: Building command '%s'. No current house" % (command)
            raise excepting.ParseError(msg, tokens, index)      

        if not self.currentStore:
            msg = "ParseError: Building command '%s'. No current store" % (command)
            raise excepting.ParseError(msg, tokens, index)

        try:
            parms = {}
            init = {}
            parts = []
            name = ''
            kind = None
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

            while index < len(tokens): # name parts end when connective
                if tokens[index] in ['as', 'at', 'to', 'be', 'in', 'rx', 'tx', 'with', 'per']: # end of parts
                    break
                parts.append(tokens[index])
                index += 1 #eat token

            name += "".join(part.capitalize() for part in parts)

            while index < len(tokens): #options 
                connective = tokens[index]
                index += 1

                if connective == 'as':
                    parts = []
                    while index < len(tokens): # kind parts end when connective
                        if tokens[index] in ['as', 'at', 'to', 'be', 'in', 'rx', 'tx', 'with', 'per']: # end of parts
                            break
                        parts.append(tokens[index])
                        index += 1 #eat token

                    #kind = "".join(part.capitalize() for part in parts)
                    kind =  "".join(parts[0:1] + [part.capitalize() for part in parts[1:]]) #camel case lower first
                    if not kind:
                        msg = "ParseError: Building command '%s'. Missing kind for connective 'as'" % (command)
                        raise excepting.ParseError(msg, tokens, index)                                     

                elif connective == 'at':
                    period = abs(Convert2Num(tokens[index]))
                    index +=1

                elif connective == 'to':
                    prefix = tokens[index]
                    index +=1

                elif connective == 'be':
                    option = tokens[index]
                    index +=1

                    if option not in ['active', 'inactive', 'slave']:
                        msg = "ParseError: Building command '%s'. Bad server scheduled option got %s" % \
                            (command, option)
                        raise excepting.ParseError(msg, tokens, index)                   

                    schedule = ScheduleValues[option] #replace text with value

                elif connective == 'in':
                    order = tokens[index]
                    index +=1
                    if order not in OrderValues:
                        msg = "ParseError: Building command '%s'. Bad order option got %s" % \
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

                elif connective == 'with':
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
                    msg = "ParseError: Building command '%s'. Bad connective got %s" % \
                        (command, connective)
                    raise excepting.ParseError(msg, tokens, index)                   

        except IndexError:
            msg = "ParseError: Building command '%s'. Not enough tokens" % (command)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building command '%s'. Unused tokens after index" %\
                (command)
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

        if kind: # Create new instance from kind class with name
            if name in serving.Server.Names:
                msg = "ParseError: Building command '%s'. Task named %s of kind %s already exists" % \
                    (command, name, kind)
                raise excepting.ParseError(msg, tokens, index)

            if kind not in serving.Server.Names: # expect instance of same name as kind
                msg = "ParseError: Building command '%s'. No tasker kind of %s" %\
                    (command, kind)
                raise excepting.ParseError(msg, tokens, index)

            kinder = serving.Server.Names[kind]
            #create new instance as the same type as kinder
            tasker = type(kinder)(name=name, store=self.currentStore, period=period,
                                  schedule=schedule, sha=sha, dha=dha, prefix=prefix)
            kw = dict()
            kw.update(init)
            tasker.reinit(**kw)         

        else: # Use an existing instance
            if name not in serving.Server.Names: #instance not exist
                msg = "ParseError: Building command '%s'. No tasker named %s" %\
                    (command, name)
                raise excepting.ParseError(msg, tokens, index)

            tasker = serving.Server.Names[name] #fetch existing instance
            kind = tasker.__class__.__name__

            if tasker in self.currentHouse.taskers: #tasker already used somewhere else
                msg = "ParseError: Building command '%s'. Task named %s of kind %s already scheduled" %\
                    (command, name, kind)
                raise excepting.ParseError(msg, tokens, index)             

            kw = dict(period=period, schedule=schedule, sha=sha, dha=dha, prefix=prefix,)
            kw.update(init)
            tasker.reinit(**kw)

        self.currentHouse.taskers.append(tasker)
        if schedule == SLAVE:
            self.currentHouse.slaves.append(tasker)
        else: #taskable active or inactive
            if order == FRONT:
                self.currentHouse.fronts.append(tasker)
            elif order == BACK:
                self.currentHouse.backs.append(tasker)
            else:
                self.currentHouse.mids.append(tasker)

        msg = "     Created tasker named {0} of kind {1} at period {2:0.4f} be {3}\n".format(
            tasker.name, kind, tasker.period,  ScheduleNames[tasker.schedule])
        console.profuse(msg)

        return True

    #Logger specific builders
    def buildLogger(self, command, tokens, index):
        """create logger in current house


           logger logname [to prefix] [at period] [be scheduled] [flush interval]
           scheduled: (active, inactive, slave)

           logger basic at 0.125
           logger basic

        """
        if not self.currentHouse:
            msg = "ParseError: Building command '{0}'. No current house.".format(
                command, index, tokens)
            raise excepting.ParseError(msg, tokens, index)                
            
        if not self.currentStore:
            msg = "ParseError: Building command '{0}'. No current store.".format(
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
                        print "Error building %s. Bad logger scheduled option got %s. index = %d tokens = %s" %\
                              (command, option, index, tokens)
                        return False

                    schedule = ScheduleValues[option] #replace text with value

                elif connective == 'in':
                    order = tokens[index]
                    index +=1
                    if order not in OrderValues:
                        print "Error building %s. Bad order got %s. index = %d tokens = %s" %\
                              (command, order, index, tokens)
                        return False
                    order = OrderValues[order] #convert to order value

                elif connective == 'flush':
                    interval = max(1.0,abs(Convert2Num(tokens[index])))
                    index +=1

                else:
                    print "Error building %s. Bad connective got %s. index = %d tokens = %s" %\
                          (command, connective, index, tokens)
                    return False

            prefix += '/' + self.currentHouse.name #extra slashes are ignored

            if name in logging.Logger.Names:
                print "Error building %s. Task %s already exists. index = %d tokens = %s" %\
                      (command, name, index, tokens)
                return False

            logger = logging.Logger(name = name, store = self.currentStore, 
                                    period = period, flushPeriod = interval,
                                    prefix = prefix)
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
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        return True


    def buildLog(self, command, tokens, index):
        """create log in current logger

           log name  [to fileName] [as (text, binary)] [on rule]
           rule: (once, never, always, update, change) 
           default fileName is log's name 
           default type is text
           default rule  is update

           for manual logging use tally command with rule once or never 


           log autopilot (text, binary, console) to './logs/' on (never, once, update, change, always) 
        """
        if not self.currentLogger:
            print "Error building %s. No current logger. index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if not self.currentStore:
            print "Error building %s. No current store. index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

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
                        print "Error building %s. Bad kind = %s. index = %d tokens = %s" %\
                              (command, kind, index, tokens)
                        return False

                elif connective == 'to':
                    fileName = tokens[index]
                    index +=1

                elif connective == 'on':
                    rule = tokens[index].capitalize()
                    index +=1

                    if rule not in LogRuleValues:
                        print "Error building %s. Bad rule = %s. index = %d tokens = %s" %\
                              (command, rule, index, tokens)
                        return False

                    rule = LogRuleValues[rule]

                else:
                    print "Error building %s. Bad connective got %s. index = %d tokens = %s" %\
                          (command, connective, index, tokens)
                    return False

            if name in logging.Log.Names:
                print "Error building %s. Log %s already exists. index = %d tokens = %s" %\
                      (command, name, index, tokens)
                return False

            log = logging.Log(name = name, store = self.currentStore, kind = kind, 
                              fileName = fileName, rule = rule)
            self.currentLogger.addLog(log)
            self.currentLog = log

            console.profuse("     Created log named {0} kind {1} file {2} rule {3}\n".format(
                name, kind, fileName, LogRuleNames[rule]))

        except IndexError:
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        return True

    def buildLoggee(self, command, tokens, index):
        """add loggee(s) to current log 

           loggee tag sharepath tag sharepath ... 
        """
        if not self.currentLog:
            print "Error building %s. No current log. index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if not self.currentStore:
            print "Error building %s. No current store. index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        try:
            while index < len(tokens):
                tag = tokens[index]
                index +=1
                path = tokens[index] #share path
                index +=1

                share = self.currentStore.create(path) #create so no errors at runtime
                if not isinstance(share, storing.Share): #verify path ends in share not node
                    print "Error building %s. Loggee path not Share. path = %s tokens = %s" %\
                          (command, path, tokens)
                    return False

                if tag in self.currentLog.loggees:
                    print "Error building %s. Loggee %s already exists in Log %s. index = %d tokens = %s" %\
                          (command, name, self.currentLog.name, index, tokens)
                    return False

                self.currentLog.addLoggee(tag = tag, loggee = share)

                console.profuse("     Added loggee {0} with tag {1} loggees {2}\n".format(
                    share.name, tag, self.currentLog.loggees))

        except IndexError:
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        return True

    #Framework specific builders

    def buildFramer(self, command, tokens, index):
        """Create a new framer and make it the current one

           framework framername [be (active, inactive, aux, slave)] [at period] [first frame]
           framework framername be active at 0.0
           framework framername 
        """
        if not self.currentHouse:
            print "Error building %s. No current house. index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if not self.currentStore:
            print "Error building %s. No current store. index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        try:
            name = tokens[index]
            index +=1

            self.verifyName(name, command, tokens, index)      

            schedule = INACTIVE  #globaling.py
            order = MID #globaling.py
            period = 0.0
            frame = ''


            while index < len(tokens): #options 
                connective = tokens[index]
                index += 1

                if connective == 'at':
                    period = abs(Convert2Num(tokens[index]))
                    index +=1

                elif connective == 'be':
                    option = tokens[index]
                    index +=1

                    if option not in ScheduleValues:
                        print "Error building %s. Bad scheduled option got %s. index = %d tokens = %s" %\
                              (command, option, index, tokens)
                        return False

                    schedule = ScheduleValues[option] #replace text with value

                elif connective == 'in':
                    order = tokens[index]
                    index +=1
                    if order not in OrderValues:
                        print "Error building %s. Bad order got %s. index = %d tokens = %s" %\
                              (command, order, index, tokens)
                        return False
                    order = OrderValues[order] #convert to order value

                elif connective == 'first':
                    frame = tokens[index]
                    index +=1

                    self.verifyName(frame, command, tokens, index)

                else:
                    print "Error building %s. Bad connective got %s. index = %d tokens = %s" %\
                          (command, connective, index, tokens)
                    return False

            if name in framing.Framer.Names:
                print "Error building %s. Framer or Task %s already exists. index = %d tokens = %s" %\
                      (command, name, index, tokens)
                return False
            else:
                framer = framing.Framer(name = name, store = self.currentStore, 
                                        period = period)
                framer.schedule = schedule
                framer.first = frame #need to resolve later

                self.currentHouse.taskers.append(framer)
                self.currentHouse.framers.append(framer)

                if schedule == SLAVE:
                    self.currentHouse.slaves.append(framer)
                elif schedule == AUX:
                    self.currentHouse.auxes.append(framer)
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

                console.profuse("     Created framer named {0} at period {1:0.4f} be {2} first {3}\n".format(
                    framer.name, framer.period, ScheduleNames[framer.schedule], framer.first))

                console.profuse("     Added framer {0} to house {1}, Assigned frame registry\n".format(
                    framer.name, self.currentHouse.name))


        except IndexError:
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        return True

    def buildFirst(self, command, tokens, index):
        """set first (starting) frame for current framer

           first framename
        """
        if not self.currentFramer:
            print "Error building %s. No current framer. index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        try:
            name = tokens[index]
            index +=1

            self.verifyName(name, command, tokens, index)       

            self.currentFramer.first = name #need to resolve later

            console.profuse("     Assigned first frame {0} for framework {1}\n".format(
                name, self.currentFramer.name))

        except IndexError:
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        return True

    #Frame specific builders
    def buildFrame(self, command, tokens, index):
        """Create frame and attach to over frame if indicated

           frame frameName
           frame frameName overName

           the frameName next is reserved

        """
        if not self.currentStore:
            print "Error building %s. No current store. index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if not self.currentFramer:
            print "Error building %s. No current framer. index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

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
                else:
                    print "Error building %s. Bad connective got %s. index = %d tokens = %s" %\
                          (command, connective, index, tokens)
                    return False

        except IndexError:
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if name in ReservedFrameNames:
            print "Error building %s in Framer %s. Frame name %s reserved. index = %d tokens = %s" %\
                  (command, self.currentFramer.name, name, index, tokens)
            return False
        elif name in framing.Frame.Names: #could use Registry Retrieve function
            print "Error building %s in Framer %s. Frame %s already exists. index = %d tokens = %s" %\
                  (command, self.currentFramer.name, name, index, tokens)
            return False
        else:
            frame = framing.Frame(name = name, store = self.currentStore, 
                                  framer = self.currentFramer) 

            if over:
                frame.over = over #need to resolve later

            #if previous frame did not have explicit next frame then use this new frame
            # ad next lexically
            if self.currentFrame and not self.currentFrame.next: 
                self.currentFrame.next = frame.name

                #default first frame is first lexical frame if not assigned otherwise
                #so if startFrame is none then we must be first lexical frame
            if not frame.framer.first:
                frame.framer.first = frame

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
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

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
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

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
                next = tokens[index]
                index += 1

                self.verifyName(next, command, tokens, index)

            else:
                next = None

        except IndexError:
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        self.currentFrame.next = next

        console.profuse("     Assigned next frame {0} for frame {1}\n".format(
            next, self.currentFrame.name))

        return True


    def buildAux(self, command, tokens, index):
        """Parse 'aux' command  for simple or conditional aux of forms

           Simple Auxiliary:
              aux framername

           Conditional Auxiliary:
              aux framername if [not] need 
              aux framername if [not] need [and [not] need ...]

        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            needs = []
            aux = None
            connective = None

            aux = tokens[index]
            index +=1 #eat token

            self.verifyName(aux, command, tokens, index)

            if index < len(tokens): #check for optional if connective
                connective = tokens[index]
                if connective not in ['if']: #invalid connective
                    msg = "ParseError: Building command '%s'. Bad connective '%s'" % \
                        (command, connective)
                    raise excepting.ParseError(msg, tokens, index)
                index += 1 #otherwise eat token            

                while (index < len(tokens)):   
                    act, index = self.makeNeed(tokens, index)
                    if not act:
                        return False # something wrong do not know what
                    needs.append(act)
                    if index < len(tokens):
                        connective = tokens[index]
                        if connective not in ['and']:
                            msg = "ParseError: Building command '%s'. Bad connective '%s'" % \
                                                    (command, connective)
                            raise excepting.ParseError(msg, tokens, index)
                        index += 1 #otherwise eat token                     

        except IndexError:
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if connective: #conditional auxiliary suspender preact
            human = ' '.join(tokens) #recreate transition command string for debugging
            #resolve aux link later 
            parms = dict(needs = needs, main = self.currentFrame, aux = aux, human = human)
            actor = acting.Actor.Names['suspender']
            act = acting.Act(actor = actor, parms = parms)
            self.currentFrame.addPreact(act)


            console.profuse("     Added suspender preact,  '{0}', with aux {1} needs:\n".format(
                command, aux))
            for need in needs:
                console.profuse("       {0} with parms = {1}\n".format(need.actor.name, need.parms))

            #create deactivator actor to deactivate aux in act 
            #add deactivator after act so decactivator always runs after act if in same context
            parms = dict(actor = actor, aux = aux)
            deAct = acting.Act(actor = acting.Actor.Names['deactivator'], parms = parms)
            self.currentFrame.addExact(deAct)

            console.profuse("     Added Exact {0} with {1}\n".format(deAct.actor.name, deAct.parms))         

        else: # Simple auxiliary
            self.currentFrame.addAux(aux) #need to resolve later
            console.profuse("     Added aux framer {0}\n".format(aux))      

        return True



    def buildDone(self, command, tokens, index):
        """Creates complete action that indicates tasker completed by setting .done state to True
           native context is enter
           Only works in framer taskers

           done
        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        if not self.currentFramer.schedule in [AUX,  SLAVE]:
            print "Error building %s. Framer is '%s' not auxiliary or slave. index = %d tokens = %s" %\
                  (command, self.currentFramer.schedule, index, tokens)
            return False


        try:
            kind = 'Done'
            framer = self.currentFramer
            actorName = 'complete' + kind.capitalize()
            if actorName not in completing.Complete.Names:
                print "Error building complete %s. No actor named %s. index = %d tokens = %s" %\
                      (kind, actorName, index, tokens)
                return False

            actor = completing.Complete.Names[actorName]

            parms = {}
            parms['framer'] = framer #resolve later if needed
            act = acting.Act(actor = actor, parms = parms)


        except IndexError:
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        context = self.currentContext
        if context == NATIVE: 
            context = ENTER #what is native for this command

        if not self.currentFrame.addByContext(act, context):   
            print "Error building %s. Bad context '%s'. index = %d tokens = %s" %\
                  (command, context, index, tokens)
            return False

        console.profuse("     Created done complete {0} with {1}\n".format(act.actor.name, act.parms))

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
                print "Error building %s. invalid timeout %s. index = %d tokens = %s" %\
                      (command, value, index, tokens)
                return (None, index)

        except IndexError:
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

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
        parms = dict(needs = needs, near = self.currentFrame, far = far, human = human)
        act = acting.Act(actor = acting.Actor.Names['transiter'], parms = parms)

        self.currentFrame.addPreact(act) #add transact as preact

        console.profuse("     Added timeout transition preact,  '{0}', with far {1} needs:\n".format(
            command, far))
        for act in needs:
            console.profuse("       {0} with parms = {1}\n".format(act.actor.name, act.parms))

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
                print "Error building %s. invalid repeat %s. index = %d tokens = %s" %\
                      (command, value, index, tokens)
                return (None, index)

        except IndexError:
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

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
        parms = dict(needs = needs, near = self.currentFrame, far = far, human = human)
        act = acting.Act(actor = acting.Actor.Names['transiter'], parms = parms)

        self.currentFrame.addPreact(act) #add transact as preact

        console.profuse("     Added repeat transition preact,  '{0}', with far {1} needs:\n".format(
            command, far))
        for act in needs:
            console.profuse("       {0} with parms = {1}\n".format(act.actor.name, act.parms))

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
        """prints a string consiting of space separated tokens
           print message

           print hello world


        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            message = ' '.join(tokens[1:])
        except IndexError:
            message = ''

        parms = dict(message = message)
        act = acting.Act(actor = acting.Actor.Names['printer'], parms = parms)

        context = self.currentContext
        if context == NATIVE: 
            context = ENTER #what is native for this command

        if not self.currentFrame.addByContext(act, context):   
            print "Error building %s. Bad context '%s'. index = %d tokens = %s" %\
                  (command, context, index, tokens)
            return False

        console.profuse("     Added {0} {1} with {2}\n".format(
            ActionContextNames[context], act.actor.name, act.parms))

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
            data, index = self.parseDirect(tokens, index)
            dataFields = data.keys()

            connective = tokens[index]
            index += 1
            if connective != 'into':
                msg = "ParseError: Building command '%s'. Unexpected connective '%s'" %\
                    (command, connective)
                raise excepting.ParseError(msg, tokens, index)

            dstFields, index = self.parseFields(tokens, index)
            dstPath, index = self.parseIndirect(tokens, index, variant = '')

        except IndexError:
            msg = "ParseError: Building command '%s'. Not enough tokens" % (command)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building command '%s'. Unused tokens after index" %\
                (command)
            raise excepting.ParseError(msg, tokens, index)

        if self.currentStore.fetchShare(dstPath) is None:
            print "     Warning: Put into non-existent share %s ... creating anyway" %\
                  (dstPath)
        dst = self.currentStore.create(dstPath)

        dataFields, dstFields = self.prepareDataDstFields(data, dataFields, dst, dstFields, tokens, index)

        dstData = odict()
        for dstField, dataField in izip(dstFields, dataFields):
            dstData[dstField] = data[dataField]

        actorName = 'poke' + 'Direct' #capitalize second word

        if actorName not in poking.Poke.Names:
            msg = "ParseError: Can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        actor = poking.Poke.Names[actorName]

        parms = {}
        parms['data'] = dstData #this is dict
        parms['destination'] = dst #this is a share

        act = acting.Act(actor = actor, parms = parms)

        msg = "     Created Actor {0} parms: data = {1}  destination = {2} ".format(
            actor.name, data, dst.name)
        console.profuse(msg)

        context = self.currentContext
        if context == NATIVE: 
            context = ENTER #what is native for this command

        if not self.currentFrame.addByContext(act, context):   
            print "Error building %s. Bad context '%s'. index = %d tokens = %s" %\
                  (command, context, index, tokens)
            return False

        console.profuse("     Added {0} {1} with {2}\n".format(
            ActionContextNames[self.currentContext], act.actor.name, act.parms))

        return True

    def buildInc(self, command, tokens, index):
        """Build inc command to inc share by data or from source

           inc destination by data
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
            dstPath, index = self.parseIndirect(tokens, index, variant = '')
            if self.currentStore.fetchShare(dstPath) is None:
                print "     Warning: Inc of non-existent share %s ... creating anyway" %\
                      ( dstPath)
            dst = self.currentStore.create(dstPath)

            connective = tokens[index]
            index += 1

            if connective == 'by':
                #print "index = %s" % index

                data, index = self.parseDirect(tokens, index)
                dataFields = data.keys()

                for field, value in data.items():
                    if isinstance(value, str):
                        msg = "ParseError: Building command '%s'. " % (command)
                        msg += "Data value = '%s' in field '%s' not a number" %\
                            (value, field)
                        raise excepting.ParseError(msg, tokens, index)

                dataFields, dstFields = self.prepareDataDstFields(data, dataFields, dst, dstFields, tokens, index)

                dstData = odict()
                for dstField, dataField in izip(dstFields, dataFields):
                    dstData[dstField] = data[dataField]

                act = self.makeDirectInc(dst, dstData)

            elif connective == 'from':
                srcFields, index = self.parseFields(tokens, index)
                srcPath, index = self.parsePath(tokens, index)
                if self.currentStore.fetchShare(srcPath) is None:
                    print "     Warning: Inc from non-existent share %s ... creating anyway" %\
                          (srcPath)
                src = self.currentStore.create(srcPath)

                srcFields, dstFields = self.prepareSrcDstFields(src, srcFields, dst, dstFields, tokens, index)

                act = self.makeIndirectInc(dst, dstFields, src, srcFields)

            else:
                msg = "ParseError: Building command '%s'. Unexpected connective '%s'" %\
                    (command, connective)
                raise excepting.ParseError(msg, tokens, index)

        except IndexError:
            msg = "ParseError: Building command '%s'. Not enough tokens" % (command)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building command '%s'. Unused tokens after index" %\
                (command)
            raise excepting.ParseError(msg, tokens, index)

        context = self.currentContext
        if context == NATIVE: 
            context = ENTER #what is native for this command

        if not self.currentFrame.addByContext(act, context):   
            print "Error building %s. Bad context '%s'. index = %d tokens = %s" %\
                  (command, context, index, tokens)
            return False

        console.profuse("     Added {0} {1} with {2}\n".format(
            ActionContextNames[self.currentContext], act.actor.name, act.parms))

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
            srcPath, index = self.parseIndirect(tokens, index, variant = '')

            connective = tokens[index]
            index += 1
            if connective != 'into':
                msg = "ParseError: Building command '%s'. Unexpected connective '%s'" %\
                    (command, connective)
                raise excepting.ParseError(msg, tokens, index)

            dstFields, index = self.parseFields(tokens, index)
            dstPath, index = self.parseIndirect(tokens, index, variant = '')

        except IndexError:
            msg = "ParseError: Building command '%s'. Not enough tokens" % (command)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building command '%s'. Unused tokens after index" %\
                (command)
            raise excepting.ParseError(msg, tokens, index)

        if self.currentStore.fetchShare(srcPath) is None:
            print "     Warning: Copy from non-existent share %s ... creating anyway" %\
                  (srcPath)
        src = self.currentStore.create(srcPath)

        if self.currentStore.fetchShare(dstPath) is None:
            print "     Warning: Copy into non-existent share %s ... creating anyway" %\
                  (dstPath)
        dst = self.currentStore.create(dstPath)

        srcFields, dstFields = self.prepareSrcDstFields(src, srcFields, dst, dstFields, tokens, index)

        actorName = 'poke' + 'Indirect' #capitalize second word

        if actorName not in poking.Poke.Names:
            msg = "ParseError: Can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        actor = poking.Poke.Names[actorName]

        parms = {}
        parms['source'] = src #this is share
        parms['sourceFields'] = srcFields #this is a list
        parms['destination'] = dst #this is a share
        parms['destinationFields'] = dstFields #this is a list

        act = acting.Act(actor = actor, parms = parms)

        msg = "     Created Actor {0} parms: ".format(actor.name)
        for key, value in parms.items():
            msg += " {0} = {1}".format(key, value)
        console.profuse("{0}\n".format(msg))

        context = self.currentContext
        if context == NATIVE: 
            context = ENTER #what is native for this command

        if not self.currentFrame.addByContext(act, context):   
            print "Error building %s. Bad context '%s'. index = %d tokens = %s" %\
                  (command, context, index, tokens)
            return False

        console.profuse("     Added {0} {1} with {2}\n".format(
            ActionContextNames[self.currentContext], act.actor.name, act.parms))

        return True

    def buildSet(self, command, tokens, index):
        """Build set command to generate goal actions

           set goal to data
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
                dstPath, index = self.parseIndirect(tokens, index, variant = 'goal')

                if self.currentStore.fetchShare(dstPath) is None:
                    print "     Warning: Nonexistent goal share %s ... creating anyway" %\
                          ( dstPath)
                dst = self.currentStore.create(dstPath)

                #required connective
                connective = tokens[index]
                index += 1

                if connective == 'to': #data direct  
                    data, index = self.parseDirect(tokens, index)
                    dataFields = data.keys()

                    dataFields, dstFields = self.prepareDataDstFields(data, dataFields, dst, dstFields, tokens, index)

                    dstData = odict()
                    for dstField, dataField in izip(dstFields, dataFields):
                        dstData[dstField] = data[dataField]

                    act = self.makeDirectGoal(dst, dstData)

                elif connective == 'from': #source indirect
                    srcFields, index = self.parseFields(tokens, index)
                    srcPath, index = self.parseIndirect(tokens, index, variant = '')

                    if self.currentStore.fetchShare(srcPath) is None:
                        print "     Warning: Copy from non-existent share %s ... creating anyway" %\
                              (srcPath)
                    src = self.currentStore.create(srcPath)

                    srcFields, dstFields = self.prepareSrcDstFields(src, srcFields, dst, dstFields, tokens, index)

                    act = self.makeIndirectGoal(dst, dstFields, src, srcFields)

                else:
                    msg = "ParseError: Building command '%s'. Unexpected connective '%s'" %\
                        (command, connective)
                    raise excepting.ParseError(msg, tokens, index)

            if not act:
                return False

        except IndexError:
            msg = "ParseError: Building command '%s'. Not enough tokens" % (command)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building command '%s'. Unused tokens after index" %\
                (command)
            raise excepting.ParseError(msg, tokens, index)

        context = self.currentContext
        if context == NATIVE: 
            context = ENTER #what is native for this command

        if not self.currentFrame.addByContext(act, context):   
            print "Error building %s. Bad context '%s'. index = %d tokens = %s" %\
                  (command, context, index, tokens)
            return False

        console.profuse("     Added {0} {1} with {2}\n".format(
            ActionContextNames[self.currentContext], act.actor.name, act.parms))      

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
                    msg = "ParseError: Building command '%s'. Bad connective '%s'" % \
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
                            msg = "ParseError: Building command '%s'. Bad connective '%s'" % \
                                                    (command, connective)
                            raise excepting.ParseError(msg, tokens, index)
                        index += 1 #otherwise eat token                             
                            

        except IndexError:
            msg = "ParseError: Building command '%s'. Not enough tokens" % (command)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building command '%s'. Unused tokens after index" %\
                (command)
            raise excepting.ParseError(msg, tokens, index)

        if not needs and connective: #if but no needs
            msg = "ParseError: Building command '%s'. Connective %s but missing need(s)" %\
                (command, connective)
            raise excepting.ParseError(msg, tokens, index)         

        # build transact 
        human = ' '.join(tokens) #recreate transition command string for debugging
        #resolve far link later 
        parms = dict(needs = needs, near = self.currentFrame, far = far, human = human)
        act = acting.Act(actor = acting.Actor.Names['transiter'], parms = parms)

        #resolve far link later 
        #act = acting.Transact(needs = needs, near = self.currentFrame, far = far, human = human)
        self.currentFrame.addPreact(act)

        console.profuse("     Added transition preact,  '{0}', with far {1} needs:\n".format(
            command, far))
        for act in needs:
            console.profuse("       {0} with parms = {1}\n".format(act.actor.name, act.parms))

        return True

    def buildLet(self, command, tokens, index):
        """Parse 'let' command  benter action  with entry conditions of forms

           Befor Enter:
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
                msg = "ParseError: Building command '%s'. Bad connective '%s'" % \
                    (command, connective)
                raise excepting.ParseError(msg, tokens, index)
            index += 1 #otherwise eat token                     

            if connective == 'me': 
                connective = tokens[index] #check for if connective
                if connective not in ['if']: #invalid connective
                    msg = "ParseError: Building command '%s'. Bad connective '%s'" % \
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
                        msg = "ParseError: Building command '%s'. Bad connective '%s'" % \
                                                (command, connective)
                        raise excepting.ParseError(msg, tokens, index)
                    index += 1 #otherwise eat token                 

        except IndexError:
            msg = "ParseError: Building command '%s'. Not enough tokens" % (command)
            raise excepting.ParseError(msg, tokens, index)

        if index != len(tokens):
            msg = "ParseError: Building command '%s'. Unused tokens after index" %\
                (command)
            raise excepting.ParseError(msg, tokens, index)

        if not needs: # no needs
            msg = "ParseError: Building command '%s'. Missing need(s)" %\
                (command)
            raise excepting.ParseError(msg, tokens, index)         

        # build beact 
        for act in needs:
            self.currentFrame.addBeact(act)

        console.profuse("     Added beact,  '{0}', with needs:\n".format(command))
        for act in needs:
            console.profuse("       {0} with {1}\n".format(act.actor.name, act.parms))

        return True      

    def buildDo(self, command, tokens, index):
        """do genre kind name

           do controller pid depth   --> controllerPIDDepth
           do arbiter switch heading  --> arbiterSwitchHeading

           do controller pid depth with foobar 1
           do controller pid depth from value in .max.depth


        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            parts = []
            parms = {}
            init = {}
            kind = None
            connective = None
            
            parts.append(tokens[index])
            index +=1

            while index < len(tokens): 
                if tokens[index] in ['as', 'to', 'from', 'with', 'per']: # end of parts
                    #connective = tokens[index]
                    #index += 1 #eat token
                    break
                parts.append(tokens[index])
                index += 1 #eat token
            
            name = "".join(parts[0:1] + [part.capitalize() for part in parts[1:]]) #camel case lower first
            
            while index < len(tokens): #options 
                connective = tokens[index]
                index += 1

                if connective == 'as':
                    parts = []
                    while index < len(tokens): # kind parts end when connective
                        if tokens[index] in ['as', 'to', 'from', 'with', 'per']: # end of parts
                            break
                        parts.append(tokens[index])
                        index += 1 #eat token

                    kind =  "".join(parts[0:1] + [part.capitalize() for part in parts[1:]]) #camel case lower first
                    if not kind:
                        msg = "ParseError: Building command '%s'. Missing kind for connective 'as'" % (command)
                        raise excepting.ParseError(msg, tokens, index)                                     
            
                elif connective == 'to':
                    data, index = self.parseDirect(tokens, index)
                    parms.update(data)
    
                elif connective == 'from':
                    srcFields, index = self.parseFields(tokens, index)
                    srcPath, index = self.parsePath(tokens, index)
                    if self.currentStore.fetchShare(srcPath) is None:
                        print "     Warning: Do from non-existent share %s ... creating anyway" %\
                              (srcPath)
                    src = self.currentStore.create(srcPath)
                    # assumes that src share was inited earlier in parsing so has fields
                    for field in srcFields:
                        parms[field] = src[field]
                
                elif connective == 'per':
                    data, index = self.parseDirect(tokens, index)
                    init.update(data)
                    
                elif connective == 'with':
                    srcFields, index = self.parseFields(tokens, index)
                    srcPath, index = self.parsePath(tokens, index)
                    if self.currentStore.fetchShare(srcPath) is None:
                        print "     Warning: Do from non-existent share %s ... creating anyway" %\
                              (srcPath)
                    src = self.currentStore.create(srcPath)
                    # assumes that src share was inited earlier in parsing so has fields
                    for field in srcFields:
                        init[field] = src[field]                

        except IndexError:
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False
        
        if kind: # Create new instance from kind class with name
            if name in deeding.Deed.Names:
                msg = "ParseError: Building command '%s'. Deed named %s of kind %s already exists" % \
                    (command, name, kind)
                raise excepting.ParseError(msg, tokens, index)

            if kind not in deeding.Deed.Names: # expect instance of same name as kind
                msg = "ParseError: Building command '%s'. No Deed kind of %s" %\
                    (command, kind)
                raise excepting.ParseError(msg, tokens, index)

            kinder = deeding.Deed.Names[kind]
            #create new instance as the same type as kinder
            actor = type(kinder)(name=name, store=self.currentStore)
            actor.ioinit.update(kinder.ioinit) # copy ioinit defaults from kinder
            if init:
                actor.preinitio(**init)
            actor.initio(**actor.ioinit)

        else: # Use an existing instance
            if name not in deeding.Deed.Names: #instance not exist
                msg = "ParseError: Building command '%s'. No Deed named %s" %\
                    (command, name)
                raise excepting.ParseError(msg, tokens, index)
            
            actor = deeding.Deed.Names[name] #fetch existing instance
            kind = actor.__class__.__name__
            if init:
                actor.preinitio(**init)
            actor.initio(**actor.ioinit)

        act = acting.Act(actor = actor, parms = parms)

        if hasattr(actor, 'restart'): #some deeds need to be restarted on frame entry
            #create restarter actor to restart actor 
            #add restarAct before act so restartAct always runs before act if in same context
            parms = dict(actor = actor)
            restartAct = acting.Act(actor = acting.Actor.Names['restarter'], parms = parms)
            self.currentFrame.addEnact(restartAct)
            context = 'enact'

            console.profuse("     Added {0} {1} with {2}\n".format(
                context, restartAct.actor.name, restartAct.parms['actor'].name))         

        context = self.currentContext
        if context == NATIVE: 
            context = RECUR #what is native for this command

        if not self.currentFrame.addByContext(act, context):   
            print "Error building %s. Bad context '%s'. index = %d tokens = %s" %\
                  (command, context, index, tokens)
            return False

        console.profuse("     Added {0} {1} with {2}\n".format(
            ActionContextNames[self.currentContext], act.actor.name, act.parms))

        return True

    def buildBid(self, command, tokens, index):
        """
           bid control tasker [tasker ...]
           bid control me
           bid control all

           control:
              (start, run, stop)

           tasker:
              (tasker, me, all)
        """
        self.verifyCurrentContext(tokens, index) #currentStore, currentFramer, currentFrame exist

        try:
            control = tokens[index]
            index +=1
            if control not in ['start', 'run', 'stop']:
                print "Error building %s. Bad control = %s. index = %d tokens = %s" %\
                      (command, control, index, tokens)
                return False

            taskers = []
            while index < len(tokens):
                tasker = tokens[index]
                index +=1

                self.verifyName(tasker, command, tokens, index)

                if tasker == 'me':
                    tasker = self.currentFramer            

                taskers.append(tasker) #resolve later

            if not taskers:
                print "Error building %s %s. No taskers. index = %d tokens = %s" %\
                      (command, control, index, tokens)
                return False

            actorName = 'want' + control.capitalize()
            if actorName not in wanting.Want.Names:
                print "Error building  %s. No actor named %s. index = %d tokens = %s" %\
                      (command, actorName, index, tokens)
                return False

            actor = wanting.Want.Names[actorName]
            parms = {}
            parms['taskers'] = taskers #resolve later
            act = acting.Act(actor = actor, parms = parms)

        except IndexError:
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        context = self.currentContext
        if context == NATIVE: 
            context = ENTER #what is native for this command

        if not self.currentFrame.addByContext(act, context):   
            print "Error building %s. Bad context '%s'. index = %d tokens = %s" %\
                  (command, context, index, tokens)
            return False

        console.profuse("     Added {0} want {1} with {2}\n".format(
            ActionContextNames[self.currentContext], act.actor.name, act.parms))      

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
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

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
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

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
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

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
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

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
            print "Error building %s. Not enough tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        if index != len(tokens):
            print "Error building %s. Unused tokens, index = %d tokens = %s" %\
                  (command, index, tokens)
            return False

        native = ENTER
        self.makeFiat(tasker, 'abort', native, command, tokens, index)

        return True   

    def buildUse(self, command, tokens, index):
        """

        """
        for token in tokens:
            print token,
        print
        return True


    def buildFlo(self, command, tokens, index):
        """

        """
        for token in tokens:
            print token,
        print
        return True

    def buildTake(self, command, tokens, index):
        """

        """
        for token in tokens:
            print token,
        print
        return True

    def buildGive(self, command, tokens, index):
        """

        """
        for token in tokens:
            print token,
        print
        return True


#------------------
    def makeDirectInc(self, destination, data):
        """Make DirectInc act 

           method must be wrapped in appropriate try excepts
        """
        actorName = 'inc' + 'Direct' #capitalize second word

        if actorName not in poking.Poke.Names:
            msg = "ParseError: Can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        actor = poking.Poke.Names[actorName]

        parms = {}
        parms['destination'] = destination #this is a share
        parms['data'] = data #this is an ordered dictionary

        act = acting.Act(actor = actor, parms = parms)

        msg = "     Created Actor {0} parms: ".format(actor.name)
        for key, value in parms.items():
            msg += " {0} = {1}".format(key, value)
        console.profuse("{0}\n".format(msg))      

        return act

    def makeIndirectInc(self, destination, destinationFields, source, sourceFields):
        """Make IndirectInc act 

           method must be wrapped in appropriate try excepts
        """
        actorName = 'inc' + 'Indirect' #capitalize second word

        if actorName not in poking.Poke.Names:
            msg = "ParseError: Goal can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        actor = poking.Poke.Names[actorName]

        parms = {}
        parms['destination'] = destination #this is a share
        parms['destinationFields'] = destinationFields #this is a list
        parms['source'] = source #this is a share
        parms['sourceFields'] = sourceFields #this is a list

        act = acting.Act(actor = actor, parms = parms)

        msg = "     Created Actor {0} parms: ".format(actor.name)
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
        dstPath = 'framer.' + self.currentFramer.name + '.goal.' + name
        dstField = 'value'
        dstFields = [dstField]
        #Create share as needed and create field as needed with default value
        #list of duples needed to initialize and dereference field
        dst = self.currentStore.create(dstPath).create([(dstField, 0)]) 

        #required connective
        connective = tokens[index]
        index += 1

        if connective == 'to': #data direct  
            data, index = self.parseDirect(tokens, index)
            dataFields = data.keys()

            dataFields, dstFields = self.prepareDataDstFields(data, dataFields, dst, dstFields, tokens, index)

            dstData = odict()
            for dstField, dataField in izip(dstFields, dataFields):
                dstData[dstField] = data[dataField]

            act = self.makeDirectGoal(dst, dstData)

        elif connective == 'from': #source indirect
            srcFields, index = self.parseFields(tokens, index)
            srcPath, index = self.parseIndirect(tokens, index, variant = '')

            if self.currentStore.fetchShare(srcPath) is None:
                print "     Warning: Copy from non-existent share %s ... creating anyway" %\
                      (srcPath)
            src = self.currentStore.create(srcPath)

            srcFields, dstFields = self.prepareSrcDstFields(src, srcFields, dst, dstFields, tokens, index)

            act = self.makeIndirectGoal(dst, dstFields, src, srcFields)

        else:
            msg = "ParseError:  Unexpected connective '%s'" %\
                (connective)
            raise excepting.ParseError(msg, tokens, index)

        return act, index

    def makeDirectGoal(self, goal, data):
        """Make directGoal act 

           method must be wrapped in appropriate try excepts
        """
        actorName = 'goal' + 'Direct' #capitalize second word

        if actorName not in goaling.Goal.Names:
            msg = "ParseError: Goal can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        actor = goaling.Goal.Names[actorName]

        parms = {}
        parms['goal'] = goal #this is a share
        parms['data'] = data #this is a dictionary

        act = acting.Act(actor = actor, parms = parms)

        msg = "     Created Actor {0} parms: ".format(actor.name)
        for key, value in parms.items():
            msg += " {0} = {1}".format(key, value)
        console.profuse("{0}\n".format(msg))   

        return act

    def makeIndirectGoal(self, goal, goalFields, source, sourceFields):
        """Make indirectGoal act 

           method must be wrapped in appropriate try excepts
        """
        actorName = 'goal' + 'Indirect' #capitalize second word

        if actorName not in goaling.Goal.Names:
            msg = "ParseError: Goal can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        actor = goaling.Goal.Names[actorName]

        parms = {}
        parms['goal'] = goal #this is share
        parms['goalFields'] = goalFields #this is a list
        parms['source'] = source #this is a share
        parms['sourceFields'] = sourceFields #this is a list

        act = acting.Act(actor = actor, parms = parms)

        msg = "     Created Actor {0} parms: ".format(actor.name)
        for key, value in parms.items():
            msg += " {0} = {1}".format(key, value)
        console.profuse("{0}\n".format(msg))   

        return act

    def makeNeed(self, tokens, index):
        """Parse a need

           method must be wrapped in try except indexError 
           method assumes already checked for currentStore
           method assumes already checked for currentFramer
           method assumes already checked for currentFrame

           Need forms:

           [not] need

           need: 
              always
              done tasker 
              status tasker is (readied, started, running, stopped, aborted)
              elapsed comparison goal [+- tolerance]
              recurred comparison goal [+- tolerance]
              state [comparison goal [+- tolerance]]  

           goal:
              goal
              value value
              boolnum
              [(value, field) in] absolute
              [(value, field) in] relativegoal

           comparison: 
              (==, !=, <, <=, >=, >)

           state:
              [(value, field) in] absolute
              [(value, field) in] relativestate

           tolerance:
              number (the absolute value is used)
        """
        Negate = False

        kind = tokens[index]

        if kind == 'not':
            Negate = True
            index += 1 #eat token
            kind = tokens[index] #get a new kind

        if kind in ['always', 'done', 'status']: #special needs
            index += 1 #eat token
            method = 'make' + kind.capitalize() + 'Need'
            if not hasattr(self, method):
                msg = "ParseError: No parse method called '%s' for need %s" %\
                    (method, kind)
                raise excepting.ParseError(msg, tokens, index)

            act, index = getattr(self, method)(kind, tokens, index)

        elif kind in ['elapsed', 'recurred']: #simple needs, direct and indirect, state is always framer relative
            index +=1 #eat token
            act, index = self.makeFramerNeed(kind, tokens, index)

        else: #basic needs dynamic (boolean, direct, & indirect)
            #parse  optional field and required statepath
            state, statePath, stateField, index = self.parseNeedState(tokens, index)

            #parse optional comparison
            comparison, index = self.parseComparisonOpt(tokens,index)

            if not comparison: #no comparison so make a boolean need

                act = self.makeBoolenNeed(state, stateField)

            else: #valid comparison so required goal
                #parse required goal
                direct, goal, goalField, index = self.parseNeedGoal(statePath, stateField, tokens, index)

                #parse optional tolerance
                tolerance, index = self.parseTolerance(tokens, index)

                if direct: #make a direct need
                    act = self.makeDirectNeed(state, stateField, comparison, goal, tolerance)

                else: #make an indirect need
                    act = self.makeIndirectNeed(state, stateField, comparison, goal, goalField, tolerance)

        if Negate:
            act = acting.Nact(actor = act.actor, parms = act.parms)

        return (act, index)

    def makeAlwaysNeed(self, kind, tokens, index):
        """Need that is true always

           method must be wrapped in appropriate try excepts

           always
        """
        actorName = 'need' + kind.capitalize()

        if actorName not in needing.Need.Names:
            msg = "ParseError: Need '%s' can't find actor named '%s'" %\
                (kind,actorName)
            raise excepting.ParseError(msg, tokens, index)

        actor = needing.Need.Names[actorName]
        parms = {}
        act = acting.Act(actor = actor, parms = parms)

        return (act, index)

    def makeDoneNeed(self, kind, tokens, index):
        """Need to check if tasker completed by .done truthy

           method must be wrapped in appropriate try excepts

           done tasker
        """
        tasker = tokens[index]
        index += 1

        actorName = 'need' + kind.capitalize()

        if actorName not in needing.Need.Names:
            msg = "ParseError: Need '%s' can't find actor named '%s'" %\
                (  kind, actorName)
            raise excepting.ParseError(msg, tokens, index)

        actor = needing.Need.Names[actorName]
        parms = {}
        parms['tasker'] = tasker
        act = acting.Act(actor = actor, parms = parms)

        return (act, index)

    def makeStatusNeed(self, kind, tokens, index):
        """Need to check if tasker named tasker status' is status

           method must be wrapped in appropriate try excepts

           status tasker is (readied, started, running, stopped, aborted)
        """
        tasker = tokens[index]
        index += 1

        connective = tokens[index]
        index += 1
        if connective != 'is':
            msg = "ParseError: Need status invalid connective '%s'" %\
                (kind, connective)
            raise excepting.ParseError(msg, tokens, index)

        status = tokens[index]
        index += 1
        if status.capitalize() not in StatusValues:
            msg = "ParseError: Need status invalid status '%s'" %\
                (kind, status)
            raise excepting.ParseError(msg, tokens, index)
        status = StatusValues[status.capitalize()] #replace name with value

        actorName = 'need' + kind.capitalize()

        if actorName not in needing.Need.Names:
            msg = "ParseError: Need '%s' can't find actor named '%s'" %\
                (kind, actorName)
            raise excepting.ParseError(msg, tokens, index)

        actor = needing.Need.Names[actorName]
        parms = {}
        parms['tasker'] = tasker  #need to resolve this
        parms['status'] = status
        act = acting.Act(actor = actor, parms = parms)

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
        statePath = 'framer.' + self.currentFramer.name + '.state.' + name
        stateField = 'value'

        #convert state path to share and create field if necessary
        #pass in list of duple to dereference field to its string
        state = self.currentStore.create(statePath).create([(stateField, 0.0)])

        act = self.makeDirectNeed(state, stateField, comparison, goal, tolerance)

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
        statePath = 'framer.' + self.currentFramer.name + '.state.' + name
        stateField = 'value'

        #convert state path to share and create field if necessary
        #pass in list of duple to dereference field to its string
        state = self.currentStore.create(statePath).create([(stateField, 0.0)])

        #parse required comparison
        comparison, index = self.parseComparisonReq(tokens,index)

        #parse required goal
        direct, goal, goalField, index = self.parseNeedGoal(statePath, stateField, tokens, index)

        #parse optional tolerance
        tolerance, index = self.parseTolerance(tokens, index)

        if direct: #make a direct need
            act = self.makeDirectNeed(state, stateField, comparison, goal, tolerance)

        else: #make an indirect need
            act = self.makeIndirectNeed(state, stateField, comparison, goal, goalField, tolerance)

        return (act, index)

    def makeBoolenNeed(self, state, stateField):
        """Make booleanNeed act 

           method must be wrapped in appropriate try excepts
        """
        actorName = 'need' + 'Boolean' #capitalize second word

        if actorName not in needing.Need.Names:
            msg = "ParseError: Need can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        actor = needing.Need.Names[actorName]
        parms = {}
        parms['state'] = state #this is a share
        parms['stateField'] = stateField #this is string

        act = acting.Act(actor = actor, parms = parms)

        msg = "     Created Actor {0} parms: ".format(actor.name)
        for key, value in parms.items():
            msg += " {0} = {1}".format(key, value)
        console.profuse("{0}\n".format(msg))   

        return act


    def makeDirectNeed(self, state, stateField, comparison, goal, tolerance):
        """Make directNeed act 

           method must be wrapped in appropriate try excepts
        """
        actorName = 'need' + 'Direct' #capitalize second word

        if actorName not in needing.Need.Names:
            msg = "ParseError: Need can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        actor = needing.Need.Names[actorName]
        parms = {}
        parms['state'] = state #this is a share
        parms['stateField'] = stateField #this is a string
        parms['comparison'] = comparison #this is a string
        parms['goal'] = goal  #this is a value: boolean number or string
        parms['tolerance'] = tolerance #this is a number

        act = acting.Act(actor = actor, parms = parms)


        msg = "     Created Actor {0} parms: ".format(actor.name)
        for key, value in parms.items():
            msg += " {0} = {1}".format(key, value)
        console.profuse("{0}\n".format(msg))   

        return act

    def makeIndirectNeed(self, state, stateField, comparison, goal, goalField, tolerance):
        """Make indirectNeed act 

           method must be wrapped in appropriate try excepts
        """
        actorName = 'need' + 'Indirect' #capitalize second word

        if actorName not in needing.Need.Names:
            msg = "ParseError: Need can't find actor named '%s'" % (actorName)
            raise excepting.ParseError(msg, tokens, index)

        actor = needing.Need.Names[actorName]
        parms = {}
        parms['state'] = state #this is share
        parms['stateField'] = stateField #this is a string
        parms['comparison'] = comparison #this is a string
        parms['goal'] = goal #this is a share
        parms['goalField'] = goalField #this is a string
        parms['tolerance'] = tolerance #this is a number

        msg = "     Created Actor {0} parms: ".format(actor.name)
        for key, value in parms.items():
            msg += " {0} = {1}".format(key, value)
        console.profuse("{0}\n".format(msg))   

        act = acting.Act(actor = actor, parms = parms)

        return act

    def makeFiat(self, name, kind, native, command, tokens, index):
        """
           Assumes wrapped in currentFrame etc checks

           make a fiat action given the tasker name and fiat kind

        """
        actorName = 'fiat' +  kind.capitalize()
        if actorName not in fiating.Fiat.Names:
            print "Error building fiat %s. No actor named %s. index = %d tokens = %s" %\
                  (kind, actorName, index, tokens)
            return False

        actor = fiating.Fiat.Names[actorName]
        parms = {}
        parms['tasker'] = name #resolve later
        act = acting.Act(actor = actor, parms = parms)      

        context = self.currentContext
        if context == NATIVE: 
            context = native #The native context for this command

        if not self.currentFrame.addByContext(act, context):   
            print "Error building %s. Bad context '%s'. index = %d tokens = %s" %\
                  (command, context, index, tokens)
            return False

        console.profuse("     Added {0} fiat {1} with {2}\n".format(
            ActionContextNames[self.currentContext], act.actor.name, act.parms))

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
            index +=1 #eat token
            field = 'value' #default field

        else: #more than one so first may be field and second token may be value
            field = tokens[index]
            index += 1
            value = tokens[index] 
            if value in Reserved: #second reserved token so first token was value
                value = field
                field = 'value' #default field
            else: #first token was field and second value
                index += 1 #eat token

        data[field] = Convert2StrBoolCoordNum(value) #convert to BoolNumStr, load data 

        #parse rest if any
        while index < len(tokens): #must be in pairs unless first is ending token
            field = tokens[index]
            if field in Reserved: #ending token so break
                break

            index += 1 #eat token
            value = tokens[index] 
            index += 1

            data[field] = Convert2StrBoolCoordNum(value) #convert to BoolNumStr, load data 

        #prevent using multiple fields if one of them is 'value'
        if (len(data) > 1) and ('value' in data): 
            msg = "ParseError: Direct data field = 'value' must be only field '%s'" % (data.keys)
            raise excepting.ParseError(msg, tokens, index)

        #prevent using incorrect format for fields
        for field, value in data.items():
            if not REO_IdentPub.match(field): #invalid format
                msg = "ParseError: Invalid field  = '%s'" % (field)
                raise excepting.ParseError(msg, tokens, index)

        return (data, index)

    def parseDirectOne(self, tokens, index):
        """Parse DirectOne
           returns ordered dictionary of one field  and its value
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

        """
        if index == (len(tokens) - 1): #only one more token so it must be value
            value = tokens[index] 
            index +=1 #eat token
            field = 'value' #default field

        else: #more than one so first may be field and second token may be value
            field = tokens[index]
            index += 1
            value = tokens[index] 
            if value in Reserved: #second reserved token so first token was value
                value = field
                field = 'value' #default field
            else: #first token was field and second value
                index += 1 #eat token

        value = Convert2StrBoolCoordNum(value) #convert to boolnumstr 

        #prevent using incorrect format for fields
        if not REO_IdentPub.match(field): #invalid format
            msg = "ParseError: Invalid field  = '%s'" % (field)
            raise excepting.ParseError(msg, tokens, index)

        return (field, value, index)

    def parseFields(self, tokens, index):
        """Parse optional field list for Indirect address

           parms:
              tokens = list of tokens for command
              index = current index into tokens

           returns:
              fields
              index

           method must be wrapped in appropriate try excepts 

           Syntax:

           [(value, fields) in] indirect

           fields:
              field [field ...]

           valid fields only when encounter token 'in' after fields

           parsing end conditions that signify no fields
           if encounter before 'in':
              no more tokens (init, put, copy, set)
              token 'to'  (init, set)
              token 'from' (init, set)
              token 'into' (copy)

        """
        indexSave = index #save it since welookahead to see if "in"
        fields = []
        found = False #flag to indicate found 'in' wich indicates fields clause

        while index < len(tokens):
            field = tokens[index]
            if field == 'in': #field list present and completed
                index +=1
                found = True
                break

            if field in Reserved: #field list not present
                break

            index += 1 #eat token
            fields.append(field)

        if not found: #no fields clause
            index = indexSave #so restore index 
            fields = [] #empty fields list

        #prevent using multiple fields if one of them is 'value'
        if (len(fields) > 1) and ('value' in fields): 
            msg = "ParseError: Field = 'value' with multiple fields = '%s'" % (fields)
            raise excepting.ParseError(msg, tokens, index)

        for field in fields:
            if not REO_IdentPub.match(field):
                msg = "ParseError: Invalid format of field '%s'" % (field)
                raise excepting.ParseError(msg, tokens, index)

        return (fields, index)

    def parseField(self, tokens, index):
        """Parse optional field  for Indirect address

           parms:
              tokens = list of tokens for command
              index = current index into tokens

           returns:
              field
              index

           method must be wrapped in appropriate try excepts 

           Syntax:

           [(value, field) in] indirect

           valid fields only when encounter token 'in' after fields

           parsing end conditions that signify no fields
           if encounter before 'in':
              no more tokens (init, put, copy, set)
              token 'to'  (init, set)
              token 'from' (init, set)
              token 'into' (copy)

        """
        indexSave = index #save it since welookahead to see if "in"
        fields = []
        found = False #flag to indicate found 'in' wich indicates fields clause

        while index < len(tokens):
            field = tokens[index]
            if field == 'in': #field list present and completed
                index +=1
                found = True
                break

            if field in Reserved: #field list not present
                break

            index += 1 #eat token
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

           method must be wrapped in appropriate try excepts
        """
        path = tokens[index] 
        index +=1

        if not REO_Path.match(path): #check if valid path
            msg = "ParseError: Invalid path '%s'" % (path)
            raise excepting.ParseError(msg, tokens, index)

        #path = path.lstrip('.') #remove leading dot if any

        return (path, index)


    def parseIndirect(self, tokens, index, variant = ''):
        """Parse Indirect data address

           parms:
              tokens = list of tokens for command
              index = current index into tokens
              variant = '' or if variant applies = 'goal' or 'state' 

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
              framer
              frame

           root:
              path [of root]

           framer:
              path of framer [name]

           frame:
              path of frame [name]

        """
        path = tokens[index] 
        index +=1

        if path in Reserved:
            msg = "ParseError: Invalid path '%s' using reserved" % (path)
            raise excepting.ParseError(msg, tokens, index)

        if REO_DotPath.match(path): #valid absolute path
            #check for optional relation clause
            #if 'of relation' clause then allows override of relative  variant
            #but still relative but using dotpath instead of path
            relation, index = self.parseRelation(tokens, index) 

            path = relation + path #absolute path starts with '.'

        elif REO_RelPath.match(path): #valid relative path
            #get optional relation clause, default is root
            relation, index = self.parseRelation(tokens, index)

            if relation:
                relation += '.'

            if variant:
                variant += '.' 

            path = relation + variant + path

        else: #invalid path format
            msg = "ParseError: Invalid path '%s'" % (path)
            raise excepting.ParseError(msg, tokens, index)

        #path = path.lstrip('.') #remove leading dot if any, all done

        return (path, index)

    def parseRelation(self, tokens, index):
        """Parse optional relation clause of relative data address

           parms:
              tokens = list of tokens for command
              index = current index into tokens

           returns:
              relation
              index

           method must be wrapped in appropriate try excepts 

           Syntax:

           relative:
              root
              framer
              frame

           root:
              path [of root]

           framer:
              path of framer [name]

           frame:
              path of frame [name]


        """
        relation = '' #default relation if none given
        if index < len(tokens): #are there more tokens
            connective = tokens[index]
            if connective == 'of': #of means relation given
                index += 1 #eat token
                relation = tokens[index]
                index +=1

                if relation not in ['root', 'framer', 'frame']:
                    msg = "ParseError: Invalid relation '%s'" % (relation)
                    raise excepting.ParseError(msg, tokens, index)

                if relation == 'root':
                    relation = '' #nothing gets prepended for root relative

            if relation in ['framer', 'frame']: #may be optional name for framer or frame
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
                    if relation == 'framer':
                        name = self.currentFramer.name
                    else: # relation == 'frame':
                        name = self.currentFrame.name

                relation += '.' + name  #append name

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

    def parseNeedState(self, tokens, index):
        """Parse required need state 

           method must be wrapped in appropriate try excepts
        """
        stateField, index = self.parseField(tokens, index)
        statePath, index = self.parseIndirect(tokens, index, variant = 'state')
        if self.currentStore.fetchShare(statePath) is None:
            print "     Warning: State '%s' non-existent ... creating anyway" %\
                  (statePath)
        state = self.currentStore.create(statePath)

        if not stateField: #default rules for field
            if state: #state has fields
                if 'value' in state:
                    stateField = 'value'

                else: #ambiguous
                    msg = "ParseError: Can't determine field for state '%s'" % (state.name)
                    raise excepting.ParseError(msg, tokens, index)
            else:
                stateField = 'value'

        if stateField not in state:
            print "     Warning: Non-existent field '%s' in state %s ... creating anyway" %\
                  (stateField, state.name)
            state[stateField] = 0.0 #create

        return (state, statePath, stateField, index)

    def parseNeedGoal(self, statePath, stateField, tokens, index):
        """Parse required goal 

           method must be wrapped in appropriate try excepts
        """
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
                #check if statePath can be interpreted  as state relative
                chunks = statePath.strip('.').split('.')
                try:
                    if chunks[0] == 'state': #root relative
                        chunks[0] = 'goal'

                    elif ((chunks[0] == 'framer') or (chunks[0] == 'frame')) and \
                         (chunks[2] == 'state'): #framer or frame relative .frame.name.state
                        chunks[2] = 'goal' #becomes .frame.name.goal

                    else:
                        msg = "ParseError: Goal = 'goal' without state variant path '%s'" %\
                            (statePath)
                        raise excepting.ParseError(msg, tokens, index)

                except IndexError:
                    msg = "ParseError: Goal = 'goal' without state variant path '%s'" %\
                        (statePath)
                    raise excepting.ParseError(msg, tokens, index)

                goalPath = ".".join(chunks)
                goalField = stateField #goal field is the same as the given state field

                if self.currentStore.fetchShare(goalPath) is None:
                    print "     Warning: Goal '%s' non-existent ... creating anyway" %\
                          (goalPath)
                goal = self.currentStore.create(goalPath)

                if goalField not in goal:
                    print "     Warning: Non-existent field '%s' in goal %s ... creating anyway" %\
                          (goalField, goal.name)
                    goal[goalField] = 0.0 #create

            else: #not 'goal' so parse as indirect
                direct = False
                #is 'field in' clause present
                goalField, index = self.parseField(tokens, index)
                goalPath, index =  self.parseIndirect(tokens, index, variant = 'goal')
                if self.currentStore.fetchShare(goalPath) is None:
                    print "     Warning: Goal '%s' non-existent ... creating anyway" %\
                          (goalPath)
                goal = self.currentStore.create(goalPath)

                if not goalField: #default rules for field
                    if goal: #goal has fields
                        if 'value' in goal:
                            goalField = 'value'

                        else: #use stateField
                            goalField = stateField
                    else:
                        goalField = 'value'

                if goalField not in goal:
                    print "     Warning: Non-existent field '%s' in goal %s ... creating anyway" %\
                          (goalField, goal.name)
                    goal[goalField] = 0.0 #create


        return (direct, goal, goalField, index)

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

    #---------------------------

    def prepareSrcDstFields(self, src, srcFields, dst, dstFields, tokens, index):
        """Prepares and verifys a transfer of data 
           from sourceFields in source to dstFields in dst
           handles default conditions when fields are empty

           src and dst are shares
           fields are lists

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
                print "     Warning: Field names mismatch. '%s' in %s from '%s' in %s  ... creating anyway" %\
                      (dstField, dst.name, srcField, src.name)

        #create any non existent source or destination fields
        for field in srcFields: #use source fields for source data
            if field not in src:
                print "     Warning: Transfer from non-existent field '%s' in share %s ... creating anyway" %\
                      (field, src.name)
                src[field] = 0.0 #create

        for field in dstFields: #use destination fields for destination data
            if field not in dst:
                print "     Warning: Transfer into non-existent field '%s' in share %s ... creating anyway" %\
                      (field, dst.name)
                dst[field] = 0.0 #create

        return (srcFields, dstFields)

    def prepareDataDstFields(self, data, dataFields, dst, dstFields, tokens, index):
        """Prepares and verifys a transfer of data 
           from dataFields in data to dstFields in dst
           handles default conditions when fields are empty

           data is dict
           dst is share
           fields are lists

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
                print "     Warning: Field names mismatch. '%s' in %s from '%s' ... creating anyway" %\
                      (dstField, dst.name, dataField)

        #create any non existent destination fields
        for field in dstFields: #use destination fields for destination data
            if field not in dst:
                print "     Warning: Transfer into non-existent field '%s' in share %s ... creating anyway" %\
                      (field, dst.name)
                dst[field] = 0.0 #create

        return (dataFields, dstFields)

    def verifyShareFields(self, share, fields, tokens, index):
        """Verify that updating fields in share won't violate the
           condition that when a share has field == 'value' 
           it will be the only field

           fields is list of field names
           share is  share

           raises exception if condition would be violated
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
            msg = "ParseError: Building command '%s'. No current store" % (tokens)
            raise excepting.ParseError(msg, tokens, index)

        if not self.currentFramer:
            msg = "ParseError: Building command '%s'. No current framer" % (tokens)
            raise excepting.ParseError(msg, tokens, index)

        if not self.currentFrame:
            msg = "ParseError: Building command '%s'. No current frame" % (tokens)
            raise excepting.ParseError(msg, tokens, index)

        return

    def verifyName(self, name, command, tokens, index):
        """Verify that name is a valid public identifyer
           Used for Task, Framer, and Frame names
        """
        if not REO_IdentPub.match(name): #bad name
            msg = "ParseError: Building command '%s'. Invalid entity name '%s'" %\
                (command, name)
            raise excepting.ParseError(msg, tokens, index)        

    #------------------------   

def DebugShareFields(store, name):
    """ prints out  fields of share named name from store for debugging """

    share = store.fetch(name)
    if share is not None:
        print '++++++++ Debug share fields++++++++'
        print share.name
        print share.items


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
    import deeding
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
                  deeding, arbiting, controlling,
                  tasking, framing, logging, interfacing, serving, 
                  housing, monitoring, testing]


    if not fileName:
        fileName = "mission.txt"

    b = Builder()
    if b.build(fileName = fileName):
        print 
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
            #print "***********"

            for house in houses:
                actives = []
                for framer in house.actives:
                    #print
                    #status = framer.status
                    desire = framer.desire
                    if desire != None:
                        control = desire
                    else:
                        control = RUN

                    status = framer.runner.send(control)
                    #print "Framer %s control %s resulting status = %s" %\
                    #            (framer.name, ControlNames[control],StatusNames[status])
                    if not (status == STOPPED or status == ABORTED):
                        actives.append(framer)
                        done = False

                house.actives = actives
                #print
                for tasker in house.taskers:
                    status = tasker.runner.send(RUN)
                    #print "    Task %s status = %s" % (tasker.name, StatusNames[status])
                house.store.advanceStamp(0.125)


        for house in houses:
            for tasker in house.taskers:
                status = tasker.runner.send(STOP) # closes files

    return b

if __name__ == "__main__":
    Test()
