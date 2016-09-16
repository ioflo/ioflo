"""
logging.py log file making module
"""
from __future__ import absolute_import, division, print_function

import sys
import os
import time
import datetime
import copy
import io

from collections import deque, MutableSequence, MutableMapping, Mapping

from ..aid.sixing import *
from .globaling import *
from ..aid.odicting import odict
from ..aid.filing import ocfn

from . import excepting
from . import registering
from . import storing
from . import tasking

from ..aid.consoling import getConsole
console = getConsole()

#Class definitions


class Logger(tasking.Tasker):
    """
    Logger Task Patron Registry Class for managing Logs

    Usage:   logger.send(START) to prepare log formats also reopens files
             logger.send(RUN) runs logs
             logger.send(STOP) closes log files needed to flush caches

    """

    def __init__(self,
                 flushPeriod=30.0,
                 prefix='~/.ioflo/log',
                 keep=0,
                 cyclePeriod=0.0,
                 fileSize=0,
                 reuse=False,
                 **kw):
        """
        Initialize instance.

        Inherited Parameters:
            name = unique name for logger
            store = data store
            period = time period between runs of logger
            schedule = tasker shedule such as ACTIVE INACTIVE

        Parameters:
            flushPeriod = time in seconds between flushes
            prefix = prefix used to create log directory
            keep = int number of log copies in rotation <1> means do not cycle
            cyclePeriod = interval in seconds between log rotations,
                     0.0 or None means do not rotate
            fileSize = size in bytes  of log file required to peform rotation
                       Do not rotate is main file is not at least meet file size
                       0 means always rotate
            reuse = Make unique time stamped log directory if True otherwise nonunique
                    useful when rotating


        Inherited Class Attributes:
            Counter = number of instances in class registrar
            Names = odict of instances keyed by name in class registrar

        Inherited instance attributes
            .name = unique name for logger
            .store = data store for house
            .period = desired time in seconds between runs,non negative, zero means asap
            .schedule = initial scheduling context for this logger vis a vis skedder

            .stamp = depends on subclass default is time logger last RUN
            .status = operational status of logger
            .desire = desired control asked by this or other taskers
            .done = logger completion state True or False
            .runner = generator to run logger

        Instance attributes
            .flushPeriod = period between flushes
            .prefix = prefix used to create log directory
            .keep = int number of log copies in rotation, < 1 means do cycle
            .cyclePeriod = interval in seconds between log rotations,
                     0.0 or None means do not rotate
            .fileSize = minimum size in bytes of main log file for rotation to occur
            .reuse = Make unique time stamped log directory if True otherwise nonunique
                    useful when rotating

            .rotateStamp = time logs last rotated
            .flushStamp = time logs last flushed
            .path = full path name of log directory
            .logs = dict of logs


        """
        super(Logger, self).__init__(**kw) #status = STOPPED  make runner advance so can send cmd

        self.flushPeriod = max(1.0, flushPeriod)
        self.prefix = prefix #prefix to log directory path
        self.keep = int(keep)
        self.cyclePeriod = max(0.0, cyclePeriod)  # ensure >= 0
        if self.keep > 0 and not self.cyclePeriod:
            self.keep = 0  # cyclePeriod must be nonzero if keep > 0
        self.fileSize = max(0, fileSize)
        self.reuse = True if reuse else False

        self.cycleStamp = 0.0
        self.flushStamp = 0.0
        self.path = '' #log directory path created on .reopen()
        self.logs = [] #list of logs

    def log(self):
        """
        Perform one log action
        """
        for log in self.logs:
            log()

        try:
            if (self.store.stamp - self.flushStamp) >= self.flushPeriod:
                console.profuse("Logger {0} Flushed at {1}, previous flush at {2}\n".format(
                    self.name, self.store.stamp, self.flushStamp))
                self.flush()
                self.flushStamp = self.store.stamp

        except TypeError:  # stamps may be None so handle
            self.flushStamp = self.store.stamp  # force flushStamp to be store.stamp

        if self.keep:
            try:
                if (self.store.stamp - self.cycleStamp) >= self.cyclePeriod:
                    console.profuse("Logger {0} Cycle rotation at {1}, previous cycle at {2}\n".format(
                        self.name, self.store.stamp, self.cycleStamp))
                    self.cycle()
                    self.cycleStamp = self.store.stamp

            except TypeError:  # stamps may be None so handle
                self.cycleStamp = self.store.stamp  # force cycleStamp to be store.stamp

    def reopen(self):
        """
        Reopen all log files
        """
        if not self.path:  # not created yet
            self.path = self.createPath(prefix = self.prefix)
            if not self.path:
                return False

        for log in self.logs:
            if not log.reopen(prefix=self.path, keep=self.keep):
                return False

        return True

    def close(self):
        """
        Close all log files
        """
        for log in self.logs:
            log.close()

    def flush(self):
        """
        Flush all log files
        """
        for log in self.logs:
            log.flush()

    def cycle(self):
        """
        Cycle (Rotate) all log files
        """
        for log in self.logs:
            log.cycle(size=self.fileSize)

    def prepare(self):
        """
        Called in runner on control = START
        """
        for log in self.logs:
            log.prepare()

    def resolve(self):
        """
        Called by house to resolve links in tasker
        """
        for log in self.logs:
            log.resolve()

    def addLog(self, log):
        """
        Add log to list of logs
        """
        self.logs.append(log)

    def createPath(self, prefix = '~/.ioflo/log'):
        """
        Returns unique logger base directory path
        if successfully creates base logger directory, empty otherwise
        creates unique log directory path
        creates physical directories on disk
        """
        path = ''
        try:
            if self.reuse:
                path = os.path.join(prefix, self.store.house.name, self.name)
                path = os.path.abspath(path)  # convert to proper absolute path
                if not os.path.exists(path):
                    os.makedirs(path)

            else:  # unique directory name
                i = 0
                while True:  # do until keep trying until different

                    dt = datetime.datetime.now()
                    dirname = "{0}_{1:04d}{2:02d}{3:02d}_{4:02d}{5:02d}{6:02d}_{7:03d}".format(
                               self.name, dt.year, dt.month, dt.day, dt.hour,
                               dt.minute, dt.second, dt.microsecond // 1000 + i )

                    path = os.path.join(prefix, self.store.house.name, dirname)
                    path = os.path.abspath(path) #convert to proper absolute path
                    if not os.path.exists(path):
                        os.makedirs(path)
                        break
                    i +=1

        except OSError as ex:
            console.terse("Error: creating log directory '{0}'\n".format(ex))
            return path

        console.concise("     Created Logger {0} Directory at '{1}'\n".format(
                self.name, self.path))

        return path

    def makeRunner(self):
        """
        generator factory function to create generator to run this logger
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
                        if self.keep and self.reuse:  # recycle in case multiple restarts
                            self.cycle()  # cause log file to exceed size before cycle time
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
    """
    Log Class for logging to file

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

       .loggees = odict of loggee shares to be logged keyed by tag
       .formats = odict of loggee format string odicts keyed by tag
                  each format string odict is are format strings keyed by data field
       .lasts = odict of loggee Data instances of last values keyed by tag
                  each Data instance attribute is data field
    """
    Counter = 0  # Logs have their own namespace
    Names = {}

    def __init__(self,
                 kind='text',
                 baseFilename='',
                 rule=NEVER,
                 loggees=None,
                 fields=None,
                 **kw):
        """
        Initialize instance.
        Parameters:
            kind = text or binary
            baseFilename = base for log file name, extension added later when path created
            rule = log rule conditions (NEVER, ONCE, ALWAYS, UPDATE, CHANGE)
            loggees = odict of shares to be logged keyed by tags
            fields = odict of field name lists keyed by loggee tag

        """
        if 'preface' not in kw:
            kw['preface'] = 'Log'

        super(Log,self).__init__(**kw) #store and name inited here

        self.stamp = None  # time stamp last logged, None means not yet logged
        self.first = True  # True means file created for the first time

        self.kind = kind
        if baseFilename:
            self.baseFilename = baseFilename #file name only
        else:
            self.baseFilename = self.name
        self.path = ''  # full dir path name of file
        self.file = None  # file where log is written
        self.paths = []  # file path names of log rotate copies

        self.rule = rule #log rule when to log
        self.action = None #which method to use when logging
        self.assignRuleAction() #assign log action function

        self.header = ''  # log file header

        self.loggees = odict()  # odict of share refs to be logged (loggees) keyed by tag
        # odict of lists of field names for loggee keyed by tag
        self.fields =  fields if fields is not None else odict()
        self.formats = odict()  # odict of format string odicts keyed by tag
                                # each entry value is odict of format strings keyed by data field
        self.lasts = odict()  # odict of data instances of last values  keyed by tag

        if loggees:
            for tag, loggee in loggees.items():
                self.addLoggee(tag, loggee)


    def resolve(self):
        """
        resolves links to loggees

        """
        console.profuse("     Resolving links for Log {0}\n".format(self.name))

        for tag, loggee in self.loggees.items():
            if not isinstance(loggee, storing.Share):
                share = self.store.fetch(loggee)
                if share is None:
                    raise excepting.ResolveError("Loggee not in store", loggee, self.name)
                self.loggees[tag] = share #replace link name with link

    def __call__(self, **kw):
        """
        run .action
        """
        self.action(**kw)
        console.profuse("     Log {0} at {1}\n".format(self.name, self.stamp))

    def createPath(self, prefix):
        """
        Returns full path name of file given prefix and .kind .baseFilename
        """
        if self.kind == 'text':
            ext = '.txt'
        elif self.kind == 'binary':
            ext = '.log'

        filename= "{0}{1}".format(self.baseFilename, ext)
        path = os.path.join(prefix, filename)
        path = os.path.abspath(path)  # convert to proper absolute path
        return path

    def reopen(self, prefix='', keep=0):
        """
        Returns True is successful False otherwise
        Closes if open then reopens
        Opens or Creates log file and assign to .path
        If .path empty then creates path using prefix
        If keep then creates cycle (rotation) copy paths in .paths
           trial opens cycle paths.
        """
        keep = int(keep)

        if not self.path:
            self.path = self.createPath(prefix=prefix)
            self.paths = []  # remove stale rotate paths

        self.close()  #innocuous to call close() on unopened file
        if os.path.exists(self.path):
            self.first = False

        try:
            self.file = ocfn(self.path, 'a+')  # append pick up where left off
        except IOError as ex:
            console.terse("Error: Creating/opening log file '{0}'\n".format(ex))
            self.file = None
            return False

        console.concise("     Created/Opened Log file '{0}'\n".format(self.path))

        if keep > 0:
            self.paths = [self.path]
            for k in range(keep):
                k += 1
                root, ext = os.path.splitext(self.path)
                path = "{0}{1:02}{2}".format(root, k, ext)
                self.paths.append(path)

                try:  # trial open file to make
                    file = ocfn(path, 'r')  # do not truncate in case reusing
                except IOError as ex:
                    console.terse("Error: Creating/opening log rotate file '{0}'\n".format(ex))
                    return False
                file.close()
                console.concise("     Created Log rotate file '{0}'\n".format(path))

        return True

    def close(self):
        """
        close self.file if open except stdout
        """
        if self.file and not self.file.closed:
            self.flush()  # close does not necessarily fsync
            self.file.close()
            self.file = None

    def flush(self):
        """
        flush self.file if open except stdout
        """
        if self.file and not self.file.closed:
            self.file.flush()
            os.fsync(self.file.fileno())

    def cycle(self, size=0):
        """
        Returns True if cycle rotate successful, False otherwise
        Cycle log files  Only cycle if size > 0 and main log file size >= size
        """

        if self.paths:  # non zero rotate copies
            self.flush()
            try:
                if size and os.path.getsize(self.path) < size:
                    return False
            except OSError as ex:
                console.terse("Error: Reading file size '{0}'\n".format(ex))
                return False

            self.close()  # also flushes
            cycled = True
            for k in reversed(range(len(self.paths) - 1)):
                old = self.paths[k]
                new = self.paths[k+1]
                try:
                    os.rename(old, new)
                except OSError as ex:
                    console.terse("Error: Moving log rotate file '{0}'\n".format(ex))
                    cycled = False
                    break

            if not cycled:
                self.reopen()  # reopen so don't lose data
                return False

            try:  # truncate main file
                self.file = ocfn(self.path, 'w+')  # truncate.file
            except IOError as ex:
                console.terse("Error: Truncating log file '{0}'\n".format(ex))
                self.file = None
                return False

            self.file.write(self.header)  # rewrite header
            self.reopen()  # reopen for append

        return True

    def assignRuleAction(self, rule = None):
        """
        Assigns correct log action based on rule
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
        elif self.rule == STREAK:
            self.action = self.streak
        elif self.rule == DECK:
            self.action = self.deck
        else:
            self.action = self.never

    def buildHeader(self):
        """
        Build  .header
        """
        # build first line header with kind rule and file name
        cf = io.StringIO()
        cf.write(ns2u(self.kind))
        cf.write(u'\t')
        cf.write(ns2u(LogRuleNames[self.rule]))
        cf.write(u'\t')
        cf.write(ns2u(self.baseFilename))
        cf.write(u'\n')
        # build second line header with field names
        cf.write(u'_time')
        for tag, fields in self.fields.items():
            if len(fields) > 1:  # multiple data fields so prepend with tag.
                for field in fields:
                    cf.write(u"\t{0}.{1}".format(tag, field))
            else:
                cf.write(u"\t{0}".format(tag))

        cf.write(u'\n')
        self.header = cf.getvalue()
        cf.close()

    def prepare(self):
        """
        Prepare log formats and values
        """
        console.profuse("     Preparing formats for Log {0}\n".format(self.name))

        if self.rule in (DECK, ):
            tag, loggee = self.loggees.items()[0]  # first loggee only
            fields = self.fields.get(tag)
            if not fields:
                raise ValueError("Log {0}: Rule '{1}' requires field list.".format(
                    self.name,
                    LogRuleNames[DECK]))

        if self.rule in (STREAK, ):
            tag, loggee = self.loggees.items()[0]  # first loggee only
            if tag in self.fields:
                if self.fields[tag]:  # at least one field
                    self.fields[tag] = self.fields[tag][:1]  # only one field allowed
                else:  # use first fields in loggee if present
                    self.fields[tag] = [loggee.keys()[0]] if loggee else []
            else:  # fields not given use first fields in loggee if present
                self.fields[tag] = [loggee.keys()[0]] if loggee else []


        else:  # default fields from loggee
            for tag, loggee in self.loggees.items():
                if tag not in self.fields or not self.fields[tag]:  # if fields not given use all fields in loggee
                    self.fields[tag] = [field for field in loggee]

        #should be different if binary kind
        #build formats
        self.formats.clear()
        self.formats['_time'] = '%s'  # '%0.6f'
        for tag, fields in self.fields.items():
            self.formats[tag] = odict()
            for field in fields:
                fmt = '\t%s'  # str for all
                self.formats[tag][field] = fmt

        #if self.rule in (STREAK, DECK, ):  # no way to know data so default fmt
            #for tag, fields in self.fields.items():
                #self.formats[tag] = odict()
                #for field in fields:
                    #fmt = '\t%s'
                    #self.formats[tag][field] = fmt

        #else:  # formats from loggee fields if present
            #for tag, fields in self.fields.items():
                #self.formats[tag] = odict()
                #loggee = self.loggees[tag]
                #for field in fields:
                    #if field in loggee:
                        #fmt = self.format(loggee[field])
                    #else:
                        #fmt = '\t%s'
                    #self.formats[tag][field] = fmt


        if self.rule in (CHANGE, ):  # build last copies for if changed
            self.lasts.clear()
            for tag, fields in self.fields.items():  # list of fields by tag
                loggee = self.loggees[tag]
                lasts = [(key, loggee[key]) for key in fields if key in loggee]
                self.lasts[tag] = storing.Data(lasts)  # in both loggee and fields

        self.buildHeader()

        if self.stamp is None and self.first:  # never logged so log headers
            self.file.write(self.header)

    def format(self, value):
        """
        returns format string for value type
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
        """
        log loggees
        called by conditional actions
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
            for field, fmt in self.formats[tag].items():
                if field in loggee:
                    value = loggee[field]
                    try:
                        text = fmt % value
                    except TypeError:
                        text = '\t%s' % value
                    cf.write(ns2u(text))

                else:  # field no longer present in loggee so just tab
                    cf.write(u'\t')

        cf.write(u'\n')

        try:
            self.file.write(cf.getvalue())
        except ValueError as ex: #if self.file already closed then ValueError
            console.terse("{0}\n".format(ex))

        cf.close()

    def logStreak(self):
        """
        called by conditional actions
        Log and remove all elements of sequence in fifo order
        head is left tail is right, Fifo is head to tail

        """
        self.stamp = self.store.stamp

        #should be different if binary kind
        cf = io.StringIO() #use string io faster than concatenation

        if self.loggees:
            tag, loggee = self.loggees.items()[0] # only works for one loggee
            if loggee: # not empty has at least one field
                if not self.fields[tag]:  # field was not prepared
                    field = loggee.keys()[0]  # first field
                    fmt = "\t%s"  # default
                else:
                    field = self.fields[tag][0]  # first prepared field
                    fmt = self.formats[tag][field]

                if field in loggee:
                    value = loggee[field]
                    d = deque()
                    if isinstance(value, MutableSequence): # has pop method
                        while value: # not empty
                            d.appendleft(value.pop()) #remove and copy in order

                    elif isinstance(value, MutableMapping): # has popitem method
                        while value: # not empty
                            d.appendleft(value.popitem()) #remove and copy in order

                    else: #not mutable sequence or mapping so log normally
                        d.appendleft(value)

                    while d: # not empty
                        try:
                            text = self.formats['_time'] % self.stamp
                        except TypeError:
                            text = '%s' % self.stamp
                        cf.write(ns2u(text))

                        element = d.popleft()
                        try:
                            text = fmt % (element, )
                        except TypeError:
                            text = '\t%s' % element
                        cf.write(ns2u(text))
                        cf.write(u'\n')

                    try:
                        self.file.write(cf.getvalue())
                    except ValueError as ex: #if self.file already closed then ValueError
                        console.terse("{0}\n".format(ex))

        cf.close()

    def logDeck(self):
        """
        called by conditional actions
        Log and remove all elements of deck in fifo order which is pull
        """
        self.stamp = self.store.stamp

        if self.loggees:
            tag, loggee = self.loggees.items()[0]  # only works for first loggee
            fields = self.fields[tag]

            if loggee.deck:  # something to log
                cf = io.StringIO() #use string io faster than concatenation

                while loggee.deck:  # while not empty deck
                    entry = loggee.pull()  # assumed a dict
                    if not isinstance(entry, Mapping):
                        console.concise("Log {0}: Deck entry of '{1}' = '{2}' not a "
                                    "mapping.\n".format(self.name, loggee.name, entry))
                        continue

                    try:
                        text = self.formats['_time'] % self.stamp
                    except TypeError:
                        text = '%s' % self.stamp
                    cf.write(ns2u(text))

                    for field in fields:
                        if field in entry:
                            fmt = self.formats[tag][field]
                            value = entry[field]
                            try:
                                text = fmt % value
                            except TypeError:
                                text = '\t%s' % value
                            cf.write(ns2u(text))

                        else:  # field not in element
                            cf.write(u'\t')

                    cf.write(u'\n')

                try:
                    self.file.write(cf.getvalue())
                except ValueError as ex: #if self.file already closed then ValueError
                    console.terse("{0}\n".format(ex))

                cf.close()

    def never(self):
        """
        log never
        This if for manual logging by frame action
        """
        pass

    def once(self):
        """
        log once
        Good for logging paramters that don't change but want record
        """
        if self.stamp is None:
            self.log()

    def always(self):
        """
        log always
        Good for logging every time logger runs unconditionally
        """
        self.log()

    def streak(self):
        """
        log sequence of first field of first loggee only
        log elements in fifo order from sequence until empty
        """
        self.logStreak()

    def deck(self):
        """
        log deck
        log elements in fifo order from deck until empty
        """
        self.logDeck()


    def update(self):
        """
        log if updated
        logs once and then only if updated after first time
        """
        if self.stamp is None: #Always log at least once even if not updated
            self.log()
            return

        for loggee in self.loggees.values():
            if loggee.stamp is not None and loggee.stamp > self.stamp:  #any number is > None
                self.log()
                return  #first update triggers log once per cycle

    def change(self):
        """
        log if changed
        logs once and then only if changed after first time
        requires that self.prepare has been called otherwise fields in
        self.lasts won't match fields in log
        """
        if self.stamp is None: #Always log at least once even if not updated
            self.log()
            return

        change = False
        for tag, fields in self.fields.items():
            last = self.lasts[tag]  # get last Data object for each loggee
            loggee = self.loggees[tag]  # get loggee for tag

            try:
                for field in fields:
                    if not hasattr(last, field):  # was not present in prepare
                        if field in loggee:  # now present
                            change = True
                            setattr(last, field, loggee[field])

                    else:  # was present in prepare
                        if loggee[field] != getattr(last, field):
                            change = True
                            setattr(last, field, loggee[field])

            except AttributeError as ex: #
                console.terse("Warning: Log {0}, missing field"
                              " '{1}' for last value of loggee {2}\n".format(
                                  self.name, field, loggee.name))

            except KeyError as ex: #
                console.terse("Warning: Log {0}, missing field"
                              " '{1}' for loggee {2}\n".format(
                                  self.name, field, loggee.name))

        if change:
            self.log()

    def addLoggee(self, tag, loggee, fields=None):
        """
        Add a loggee at tag to .loggees
        Optional fields is list of field name strings to sub select fields in loggee
        """
        if self.stamp is None: #only add if not logged even once yet
            if tag ==  '_time':
                raise excepting.ResolveError("Bad loggee tag '_time'", self.name, loggee.name)
            if tag in self.loggees: #only add if not already there
                raise excepting.ResolveError("Duplicate tag", tag, loggee)
            self.loggees[tag] = loggee
            self.fields[tag] = fields if fields else []  # need tag to preserve order

