"""logging.py log file making module


"""
#print("module {0}".format(__name__))

import sys
if sys.version < '3':
    def b(x):
        return x
else:
    def b(x):
        return x.encode('ISO-8859-1')
    xrange = range
import os
import time
import datetime
import copy
import io


from collections import deque, MutableSequence, MutableMapping

from ..aid.sixing import *
from .globaling import *
from ..aid.odicting import odict

from . import excepting
from . import registering
from . import storing
from . import tasking

from ..aid.consoling import getConsole
console = getConsole()

#Class definitions


class Logger(tasking.Tasker):
    """Logger Task Patron Registry Class for managing Logs

       Usage:   logger.send(START) to prepare log formats also reopens files
                logger.send(RUN) runs logs
                logger.send(STOP) closes log files needed to flush caches

       iherited instance attributes
          .name = unique name for machine
          .store = data store for house should be same for all frameworks

          .period = desired time in seconds between runs must be non negative, zero means asap
          .stamp = time when tasker last ran sucessfully (not interrupted by exception)
          .status = operational status of tasker
          .desire = desired control asked by this or other taskers
          .runner = generator to run tasker

       Instance attributes
          .logs = dict of logs
          .flushStamp = time logs last flushed
          .flushPeriod = period between flushes
          .prefix = prefix used to create log directory
          .path = full path name of log directory

    """
    #Counter = 0
    #Names = {}

    def __init__(self, flushPeriod = 30.0, prefix = './', **kw):
        """Initialize instance.

           Parameters
              flushPeriod = time in seconds between flushes
              prefix = prefix used to create log directory

        """
        super(Logger,self).__init__(**kw) #status = STOPPED  make runner advance so can send cmd

        self.logs = [] #list of logs
        self.flushStamp = 0.0
        self.flushPeriod = max(1.0, flushPeriod)
        self.prefix = prefix #prefix to log directory path
        self.path = '' #log directory path created on .reopen()

    def log(self):
        """    """
        for log in self.logs:
            log()

        try:
            if (self.store.stamp - self.flushStamp) >= self.flushPeriod:
                console.profuse("Logger {0} Flushed at {1}, previous flush at {2}\n".format(
                    self.name, self.store.stamp, self.flushStamp))
                self.flush()
                self.flushStamp = self.store.stamp

        except TypeError:
            self.flushStamp = self.store.stamp #forces flushStamp to be a number once store.stamp is

    def reopen(self):
        """    """
        if not self.createPath(prefix = self.prefix):
            return False

        for log in self.logs:
            log.createPath(prefix = self.path)

            if not log.reopen():
                return False

        return True

    def close(self):
        """      """
        for log in self.logs:
            log.close()

    def flush(self):
        """      """
        for log in self.logs:
            log.flush()

    def prepare(self):
        """Called in runner on control = START    """
        for log in self.logs:
            log.prepare()

    def resolve(self):
        """    """
        for log in self.logs:
            log.resolve()

    def addLog(self, log):
        """   """
        self.logs.append(log)
        #log.prepare()

    def createPath(self, prefix = './'):
        """creates log directory path
           creates physical directories on disk
        """
        try:
            #if repened too quickly could be same so we make a do until kludge
            path = self.path

            i = 0
            while path == self.path: #do until keep trying until different
                dt = datetime.datetime.now()
                path = "{0}_{1}_{2:04d}{3:02d}{4:02d}_{5:02d}{6:02d}{7:02d}".format(
                        prefix, self.name, dt.year, dt.month, dt.day, dt.hour,
                        dt.minute, dt.second + i)
                path = os.path.abspath(path) #convert to proper absolute path
                i +=1

            if not os.path.exists(path):
                os.makedirs(path)

        except OSError as ex:
            console.terse("Error: creating log directory '{0}'\n".format(ex))
            return False

        self.path = path
        console.concise("     Created Logger {0} Directory= '{1}'\n".format(
                self.name, self.path))

        return True

    def makeRunner(self):
        """generator factory function to create generator to run this logger
        """
        #do any on creation initialization here
        console.profuse("     Making Logger Task Runner {0}\n".format(self.name))

        self.status = STOPPED #operational status of tasker
        self.desire = STOP #default what to do next time, override below

        try: #catch exceptions to close log files before exiting generator
            while (True):
                control = (yield (self.status )) #accept control and yield status
                console.profuse("\n     Iterate Logger {0} with control = {1} status = {2}\n".format(
                    self.name,
                    ControlNames.get(control, 'Unknown'),
                    StatusNames.get(self.status, 'Unknown')))

                if control == RUN:
                    console.profuse("     Running Logger {0} ...\n".format(self.name))
                    self.log()
                    self.status = RUNNING

                elif control == READY:
                    console.profuse("     Attempting Ready Logger {0}\n".format(self.name))
                    #doesn't do anything yet
                    console.terse("     Readied Logger {0} ...\n".format(self.name))
                    self.status = READIED

                elif control == START:
                    console.profuse("     Attempting Start Logger {0}\n".format(self.name))

                    if self.reopen():
                        console.terse("     Starting Logger {0} ...\n".format(self.name))
                        self.prepare()
                        self.log()
                        self.desire = RUN
                        self.status = STARTED
                    else:
                        self.desire = STOP
                        self.status = STOPPED

                elif control == STOP:
                    if self.status != STOPPED:
                        console.terse("     Stopping Logger {0} ...\n".format(self.name))
                        self.log() #final log
                        self.close()
                        self.desire = STOP
                        self.status = STOPPED

                else:  #control == ABORT
                    console.profuse("     Aborting Logger {0} ...\n".format(self.name))
                    self.close()
                    self.desire = ABORT
                    self.status = ABORTED

                self.stamp = self.store.stamp

        except Exception as ex:
            console.terse("{0}\n".format(ex))
            console.terse("     Exception in Logger {0} in {1}\n".format(
                    self.name, self.store.house.name))
            raise

        finally:
            self.close() #close all log files
            self.desire = ABORT
            self.status = ABORTED

class Log(registering.StoriedRegistrar):
    """Log Class for logging to file

       Iherited instance attributes:
          .name = unique name for log (group)
          .store = data store

       Instance attributes:
          .stamp = time stamp last time logged used by once and update actions
          .kind = text or binary
          .fileName = file name only
          .path = full dir path name of file
          .file = file where log is written
          .rule = log rule conditions for log
          .action = function to use when logging
          .header = header for log file
          .formats = ordered dictionary of log format strings
          .loggees = ordered dictionary of shares to be logged
    """
    Counter = 0
    Names = {}

    def __init__(self, kind = 'text', fileName = '', rule = NEVER, loggees = None, **kw):
        """Initialize instance.
           Parameters:
           kind = text or binary
           rule = log rule conditions (NEVER, ONCE, ALWAYS, UPDATE, CHANGE)
           loggees = ordered dictionary of shares to be logged with tags
        """
        if 'preface' not in kw:
            kw['preface'] = 'Log'

        super(Log,self).__init__(**kw) #store and name inited here

        self.stamp = None #time stamp last logged, None means never logged

        self.kind = kind
        if fileName:
            self.fileName = fileName #file name only
        else:
            self.fileName = self.name
        self.path = '' #full dir path name of file
        self.file = None #file where log is written

        self.rule = rule #log rule when to log
        self.action = None #which method to use when logging
        self.assignRuleAction() #assign log action function

        self.header = ''
        self.formats = odict() #ordered dictionary of log format strings by tag
        self.loggees = odict() #ordered dict of shares to be logged (loggees) by tag
        self.lasts = odict()   #ordered dict of last values for loggees by tag

        if loggees:
            if '_time' in loggees:
                raise excepting.ResolveError("Bad loggee tag '_time'", self.name, loggee['_time'].name)
            self.loggees.update(loggees)

    def __call__(self, **kw):
        """run .action

        """
        self.action(**kw)
        console.profuse("     Log {0} at {1}\n".format(self.name, self.stamp))

    def createPath(self, prefix):
        """creates full path name of file

        """
        if self.kind == 'text':
            suffix = '.txt'
        elif self.kind == 'binary':
            suffix = '.log'

        self.path = "%s/%s%s" % (prefix,self.fileName,suffix)
        self.path = os.path.abspath(self.path) #convert to proper absolute path

    def reopen(self):
        """closes if open then reopens
        """
        self.close()  #innocuous to call close() on unopened file
        try:
            self.file = open(self.path, 'a+')

        except IOError as ex:
            console.terse("Error: creating log file '{0}'\n".format(ex))
            self.file = None
            return False

        console.concise("     Created Log file '{0}'\n".format(self.path))

        return True

    def close(self):
        """ close self.file if open except stdout
        """
        if self.file and not self.file.closed:
            self.file.close()
            self.file = None

    def flush(self):
        """ flush self.file if open except stdout
        """
        if self.file and not self.file.closed:
            self.file.flush()
            os.fsync(self.file.fileno())

    def assignRuleAction(self, rule = None):
        """Assigns correct log action based on rule

        """
        #should be different if binary kind
        if rule is not None:
            self.rule = rule

        if self.rule == ONCE:
            self.action = self.once
        elif self.rule == ALWAYS:
            self.action = self.always
        elif self.rule == UPDATE:
            self.action = self.update
        elif self.rule == CHANGE:
            self.action = self.change
        elif self.rule == LIFO:
            self.action = self.lifo
        elif self.rule == FIFO:
            self.action = self.fifo
        else:
            self.action = self.never

    def prepare(self):
        """Prepare log formats and values

        """
        console.profuse("     Preparing formats for Log {0}\n".format(self.name))

        #build header
        cf = io.StringIO()
        cf.write(ns2u(self.kind))
        cf.write(u'\t')
        cf.write(ns2u(LogRuleNames[self.rule]))
        cf.write(u'\t')
        cf.write(ns2u(self.fileName))
        cf.write(u'\n')
        cf.write(u'_time')
        for tag, loggee in self.loggees.items():
            if len(loggee) > 1:
                for field in loggee:
                    cf.write(u'\t')
                    cf.write(ns2u(tag))
                    cf.write(u'.')
                    cf.write(ns2u(field))
            else:
                cf.write(u'\t')
                cf.write(ns2u(tag))

        cf.write(u'\n')
        self.header = cf.getvalue()
        cf.close()

        #should be different if binary kind
        #build formats
        self.formats.clear()
        self.formats['_time'] = '%0.4f'
        for tag, loggee in self.loggees.items():
            self.formats[tag] = odict()
            for field, value in loggee.items():
                self.formats[tag][field] = self.format(value)

        #build last copies for if changed
        self.lasts.clear()
        for tag, loggee in self.loggees.items():
            self.lasts[tag] = storing.Data(loggee.items())  #make copy of loggee data

        if self.stamp is None: #never logged so log headers
            self.file.write(self.header)

    def format(self, value):
        """returns format string for value type

        """
        if isinstance(value, float):
            return '\t%0.4f'
        elif isinstance(value, bool):
            return '\t%s'
        elif isinstance(value, int) or isinstance(value, long):
            return '\t%d'
        else:
            return '\t%s'

    def log(self):
        """called by conditional actions

        """
        self.stamp = self.store.stamp

        #should be different if binary kind
        cf = io.StringIO() #use string io faster than concatenation
        try:
            text = self.formats['_time'] % self.stamp
        except TypeError:
            text = '%s' % self.stamp
        cf.write(ns2u(text))

        for tag, loggee in self.loggees.items():
            if loggee: #len non zero
                for field, value in loggee.items():
                    try:
                        text = self.formats[tag][field] % value
                    except TypeError:
                        text = '%s' % value
                    cf.write(ns2u(text))

            else: #no items so just write tab
                cf.write(u'\t')

        cf.write(u'\n')

        try:
            self.file.write(cf.getvalue())
        except ValueError as ex: #if self.file already closed then ValueError
            console.terse("{0}\n".format(ex))

        cf.close()

    def logSequence(self, fifo=False):
        """ called by conditional actions
            Log and remove all elements of sequence
            Default is lifo order
            If fifo Then log in fifo order
            head is left tail is right
            lifo is log tail to head
            fifo is log head to tail
        """
        self.stamp = self.store.stamp

        #should be different if binary kind
        cf = io.StringIO() #use string io faster than concatenation
        try:
            stamp = self.formats['_time'] % self.stamp
        except TypeError:
            stamp = '%s' % self.stamp

        if self.loggees:
            tag, loggee = self.loggees.items()[0] # only works for one loggee
            if loggee: # not empty
                field, value = loggee.items()[0] # only first item
                d = deque()
                if isinstance(value, MutableSequence): #has pop method
                    while value: # not empty
                        d.appendleft(value.pop()) #remove and copy in order

                elif isinstance(value, MutableMapping): # has popitem method
                    while value: # not empty
                        d.appendleft(value.popitem()) #remove and copy in order

                else: #not mutable sequence or mapping so log normally
                    d.appendleft(value)

                while d: # not empty
                    if fifo:
                        element = d.popleft()
                    else: #lifo
                        element = d.pop()

                    try:
                        text = self.formats[tag][field] % (element, )
                    except TypeError:
                        text = '%s' % element
                    cf.write(u"%s\t%s\n" % (stamp, text))

        try:
            self.file.write(cf.getvalue())
        except ValueError as ex: #if self.file already closed then ValueError
            console.terse("{0}\n".format(ex))

        cf.close()

    def never(self):
        """log never
           This if for manual logging by frame action
        """
        pass

    def once(self):
        """log once
           Good for logging paramters that don't change but want record
        """
        if self.stamp is None:
            self.log()

    def always(self):
        """log always

        """
        self.log()

    def lifo(self):
        """log lifo sequence
            log elements in lifo order from sequence until empty
        """
        self.logSequence()

    def fifo(self):
        """log fifo sequence
            log elements in fifo order from sequence until empty
        """
        self.logSequence(fifo=True)

    def update(self):
        """log if updated
           logs once and then only if updated
        """
        if self.stamp is None: #Always log at least once even if not updated
            self.log()
            return

        for loggee in self.loggees.values():
            if loggee.stamp is not None and loggee.stamp > self.stamp:  #any number is > None
                self.log()
                return  #first update triggers log once per cycle

    def change(self):
        """log if changed
           logs once and then only if changed
           requires that self.prepare has been called otherwise fields in
           self.lasts won't match fields in log
        """
        if self.stamp is None: #Always log at least once even if not updated
            self.log()
            return

        change = False
        for tag, loggee in self.loggees.items():
            last = self.lasts[tag] #get last Data object for each loggee
            for field, value in loggee.items():
                try:
                    if getattr(last, field) != value:
                        change = True
                        setattr(last, field, value)
                except AttributeError as ex: #
                    console.terse("Warning: Log {0}, new runtime field"
                                  " '{1}' for loggee {2}\n".format(
                                      self.name, field, loggee.name))

        if change:
            self.log()

    def addLoggee(self, tag, loggee):
        """

        """
        if self.stamp is None: #only add if not logged even once yet
            if tag in self.loggees: #only add if not already there
                raise excepting.ResolveError("Duplicate tag", tag, loggee)
            self.loggees[tag] = loggee

    def resolve(self):
        """resolves links to loggees

        """
        console.profuse("     Resolving links for Log {0}\n".format(self.name))

        for tag, loggee in self.loggees.items():
            if not isinstance(loggee, storing.Share):
                share = self.store.fetch(loggee)
                if not share:
                    raise excepting.ResolveError("Loggee not in store", loggee, self.name)
                self.loggees[tag] = share #replace link name with link

