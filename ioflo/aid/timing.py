"""aiding.py constants and basic functions

"""
from __future__ import absolute_import, division, print_function


import time
import random
import datetime


# Import ioflo libs
from .sixing import *
from ..base import excepting

from .consoling import getConsole
console = getConsole()

TIME1970 = long(2208988800) #offset secs between SNTP epoch=1900 & unix epoch=1970

def totalSeconds(td):
    """ Compute total seconds for datetime.timedelta object
        needed for python 2.6
    """
    return ((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6)

TotalSeconds = totalSeconds

def iso8601(dt=None):
    """
    Returns string datetime stamp in iso 8601 format from datetime object dt
    If dt is missing then use utcnow
    YYYY-MM-DDTHH:MM:SS.mmmmmm which is strftime '%Y-%m-%dT%H:%M:%S.%f'
    """
    if dt is None:
        dt = datetime.datetime.utcnow()
    return(dt.isoformat())

def tuuid(stamp=None, prefix=None):
    """
    Returns lexocographically sortable TUUID  (Time Universal Unique Identifier)
    that is hex formated string of length 24
    stamp is float time since unix epoch (1970-1-1) as in time.time()
    If stamp not provided uses current system time UTC
    
    prefix is optional prefix string that is prepended to tuid with '_'
    for example if prefix is 'm' then tuiid looks like
    'm_0000014ddf1f2f9c_5e36738'
    The length of the tuuid is now 24 + len(prefix) +1

    Format of of TUUID is hex string of form stamphex_randombyteshex
    Example:
    '0000014ddf1f2f9c_5e36738'

    Stamp is time since unix epoch (1970-1-1) in milliseconds, for example
        1422658890197

    Unix time is 32 bit integer in seconds which rolls over on 2038-1-19
    To represent unix epoch in seconds need at least 32 bits
    To represent unix epoch in microseconds use 64 bits (8 bytes, 16 hex characters)

    Adding separator character adds 1 hex char for 17 hex digits
    Adding 7 hex char of random data brings the total to 24 hex bytes

    28 bits (3.5 bytes, 7 hex characters) the random bytes or 24 characters total

    16 chars (8 bytes) stamp + 1 char underscore + 7 chars (3.5 bytes) random =
        24 chars (12 bytes)

    Uses random.SystemRandom which is crytographically random
    """
    parts = []
    if prefix is not None:
        parts.append(prefix)
    stamp = stamp if stamp is not None else time.mktime(time.gmtime())
    stamp = int(stamp * 1000000)
    stamp = "{0:016x}".format(stamp)[-16:]
    parts.append(stamp)
    randomized = random.SystemRandom().randint(0, 0xFFFFFFF)
    randomized = "{0:07x}".format(randomized)[-7:]
    parts.append(randomized)
    return ("_".join(parts))


class Timer(object):
    """ Class to manage real elaspsed time.  needs time module
        attributes:
        .duration = time duration of timer start to stop
        .start = time started
        .stop = time when timer expires

        properties:
        .elaspsed = time elasped since start
        .remaining = time remaining until stop
        .expired = True if expired, False otherwise

        methods:
        .extend() = extends/shrinks timer duration
        .repeat() = restarts timer at last .stop so no time lost
        .restart() = restarts timer
    """

    def __init__(self, duration = 0.0):
        """ Initialization method for instance.
            duration in seconds (fractional)
        """
        self.restart(start=time.time(), duration=duration)

    def getElapsed(self): #for property
        """ Computes elapsed time in seconds (fractional) since start.
            if zero then hasn't started yet
        """
        return max(0.0, time.time() - self.start)
    elapsed = property(getElapsed, doc='Elapsed time.')

    def getRemaining(self):# for property
        """ Returns time remaining in seconds (fractional) before expires.
            returns zero if it has already expired
        """
        return max(0.0, self.stop - time.time())
    remaining = property(getRemaining, doc='Remaining time.')

    def getExpired(self):
        if (time.time() >= self.stop):
            return True
        else:
            return False
    expired = property(getExpired, doc='True if expired, False otherwise')

    def restart(self,start=None, duration=None):
        """ Starts timer at start time secs for duration secs.
            (fractional from epoc)
            If start arg is missing then restarts at current time
            If duration arg is missing then restarts for current duration
        """
        if start is not None:
            self.start = abs(start) #must be non negative
        else: #use current time
            self.start = time.time()

        if duration is not None:
            self.duration = abs(duration) #must be non negative
        #Otherwise keep old duration

        self.stop = self.start + self.duration

        return (self.start, self.stop)

    def repeat(self):
        """ Restarts timer at stop so no time lost

        """
        return self.restart(start=self.stop)

    def extend(self, extension=None):
        """ Extends timer duration for additional extension seconds (fractional).
            Useful so as not to lose time when  need more/less time on timer

            If extension negative then shortens existing duration
            If extension arg missing then extends for the existing duration
            effectively doubling the time

        """
        if extension is None: #otherwise extend by .duration or double
            extension = self.duration

        duration = self.duration + extension

        return self.restart(start=self.start, duration=duration)

class MonoTimer(object):
    """ Class to manage real elaspsed time with monotonic guarantee.
        If the system clock is retrograded (moved back in time)
        while the timer is running then time.time() could move
        to before the start time.
        A MonoTimer detects this retrograde and if adjust is True then
        shifts the timer back otherwise it raises a TimerRetroError
        exception.
        This timer is not able to detect a prograded clock
        (moved forward in time)

        Needs time module
        attributes:
        .duration = time duration of timer start to stop
        .start = time started
        .stop = time when timer expires
        .retro = automaticall shift timer if retrograded clock detected

        properties:
        .elaspsed = time elasped since start
        .remaining = time remaining until stop
        .expired = True if expired, False otherwise

        methods:
        .extend() = extends/shrinks timer duration
        .repeat() = restarts timer at last .stop so no time lost
        .restart() = restarts timer
    """

    def __init__(self, duration = 0.0, retro=False):
        """ Initialization method for instance.
            duration in seconds (fractional)
        """
        self.retro = True if retro else False
        self.start = None
        self.stop = None
        self.latest = time.time()  # last time checked current time
        self.restart(start=self.latest, duration=duration)

    def update(self):
        '''
        Updates .latest to current time.
        Checks for retrograde movement of system time.time() and either
        raises a TimerRetroErrorexception or adjusts the timer attributes to compensate.
        '''
        delta = time.time() - self.latest  # current time - last time checked
        if delta < 0:  # system clock has retrograded
            if not self.retro:
                raise excepting.TimerRetroError("Timer retrograded by {0} "
                                                "seconds\n".format(delta))
            self.start = self.start + delta
            self.stop = self.stop + delta

        self.latest += delta

    def getElapsed(self): #for property
        """ Computes elapsed time in seconds (fractional) since start.
            if zero then hasn't started yet
        """
        self.update()
        return max(0.0, self.latest - self.start)
    elapsed = property(getElapsed, doc='Elapsed time.')

    def getRemaining(self):# for property
        """ Returns time remaining in seconds (fractional) before expires.
            returns zero if it has already expired
        """
        self.update()
        return max(0.0, self.stop - self.latest)
    remaining = property(getRemaining, doc='Remaining time.')

    def getExpired(self):
        self.update()
        if (self.latest >= self.stop):
            return True
        else:
            return False
    expired = property(getExpired, doc='True if expired, False otherwise')

    def restart(self,start=None, duration=None):
        """ Starts timer at start time secs for duration secs.
            (fractional from epoc)
            If start arg is missing then restarts at current time
            If duration arg is missing then restarts for current duration
        """
        self.update()
        if start is not None:
            self.start = abs(start) #must be non negative
        else: #use current time
            self.start = self.latest

        if duration is not None:
            self.duration = abs(duration) #must be non negative
        #Otherwise keep old duration

        self.stop = self.start + self.duration

        return (self.start, self.stop)

    def repeat(self):
        """ Restarts timer at stop so no time lost

        """
        return self.restart(start=self.stop)

    def extend(self, extension=None):
        """ Extends timer duration for additional extension seconds (fractional).
            Useful so as not to lose time when  need more/less time on timer

            If extension negative then shortens existing duration
            If extension arg missing then extends for the existing duration
            effectively doubling the time

        """
        if extension is None: #otherwise extend by .duration or double
            extension = self.duration

        duration = self.duration + extension

        return self.restart(start=self.start, duration=duration)

class StoreTimer(object):
    """ Class to manage relative Store based time.
        Uses Store instance .stamp attribute as current time
        Attributes:
        .duration = time duration of timer start to stop
        .start = time started
        .stop = time when timer expires

        properties:
        .elaspsed = time elasped since start
        .remaining = time remaining until stop
        .expired = True if expired, False otherwise

        methods:
        .extend() = extends/shrinks timer duration
        .repeat() = restarts timer at last .stop so no time lost
        .restart() = restarts timer
    """

    def __init__(self, store, duration = 0.0):
        """ Initialization method for instance.
            store is reference to Store instance
            duration in seconds (fractional)
        """
        self.store = store
        start = self.store.stamp if self.store.stamp is not None else 0.0
        self.restart(start=start, duration=duration)

    def getElapsed(self): #for property
        """ Computes elapsed time in seconds (fractional) since start.
            if zero then hasn't started yet
        """
        return max(0.0, self.store.stamp - self.start)
    elapsed = property(getElapsed, doc='Elapsed time.')

    def getRemaining(self):# for property
        """ Returns time remaining in seconds (fractional) before expires.
            returns zero if it has already expired
        """
        return max(0.0, self.stop - self.store.stamp)
    remaining = property(getRemaining, doc='Remaining time.')

    def getExpired(self):
        if (self.store.stamp is not None and self.store.stamp >= self.stop):
            return True
        else:
            return False
    expired = property(getExpired, doc='True if expired, False otherwise')

    def restart(self, start=None, duration=None):
        """ Starts timer at start time secs for duration secs.
            (fractional from epoc)
            If start arg is missing then restarts at current time
            If duration arg is missing then restarts for current duration
        """
        if start is not None:
            self.start = abs(start) #must be non negative
        else: #use current time
            self.start = self.store.stamp

        if duration is not None:
            self.duration = abs(duration) #must be non negative
        #Otherwise keep old duration

        self.stop = self.start + self.duration

        return (self.start, self.stop)

    def repeat(self):
        """ Restarts timer at stop so no time lost

        """
        return self.restart(start = self.stop)

    def extend(self, extension=None):
        """ Extends timer duration for additional extension seconds (fractional).
            Useful so as not to lose time when  need more/less time on timer

            If extension negative then shortens existing duration
            If extension arg missing then extends for the existing duration
            effectively doubling the time

        """
        if extension is None: #otherwise extend by .duration or double
            extension = self.duration

        duration = self.duration + extension

        return self.restart(start=self.start, duration=duration)


class Stamper(object):
    """
    Provides a relative time stamp that is advanced with method
    Models the protocol for time stamps used by the Store class
    Use this to provide matching interface to Store for relative time stamp

    Attributes:
        stamp is relative time stamp

    """
    def __init__(self, stamp=None):
        """
        Initialize instance
        """
        self.stamp = float(stamp) if stamp is not None else 0.0

    def change(self, stamp):
        """
        change time stamp
        """
        self.stamp = float(stamp)

    changeStamp = change  # alias

    def advance(self, delta):
        """
        Advance time stamp by delta
        """
        self.stamp += float(delta)

    advanceStamp = advance  # alias



