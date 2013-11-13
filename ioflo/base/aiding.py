"""aiding.py constants and basic functions

"""
#print "module %s" % __name__


import exceptions
import math
import types
import socket
import os
import errno
import time
import struct
import re
import string
from collections import deque


from .globaling import *

from .consoling import getConsole
console = getConsole()


class fifo(deque):  #new-style class to add put get methods
    """ Extends deque to support more convenient FIFO queue access
       
       for any python sequence to determin if it is empty just use "if s:"
       
       local methods
       .put inserts non-None item at tail, back (right side) of deque
       .get retrieves item from head, front, (left side) of deque, None if empty
       

       inherited methods:
       .append()  = add to right side of deque
       .appendleft() = add to left side of deque
       .clear()  = clear items from deque
       .extend() = append iterable
       .extendleft = appendleft iterable
       .pop() = remove from right side
       .popleft() = remove from left side
       .remove() = remove first occurence of value left to right
       .rotate() = rotate to right if neg rotate to left
       .reversed() = copy of deque reversed
    """

    def put(self, item):
        """Puts item at tail of queue = back of deque
           If item is None don't put on Queue. Symmetric with get which returns
           None if queue empty
        """
        if item is not None:
            self.append(item)

    def get(self):
        """Returns item from head of fifo = front of deque
           If empty returns None  (therefore None is not allowed as item in fifo)
        """
        try:
            item = self.popleft()
        except IndexError:
            item = None

        return item



class Timer(object):
    """Class to manage real elaspsed time.  needs time module
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
        """Initialization method for instance.
           duration in seconds (fractional)
        """
        self.restart(start = time.time(), duration = duration)

    def getElapsed(self): #for property
        """Computes elapsed time in seconds (fractional) since start.
           if zero then hasn't started yet
        """
        return abs(time.time() - self.start)
    elapsed = property(getElapsed, doc = 'Elapsed time.')

    def getRemaining(self):# for property
        """Returns time remaining in seconds (fractional) before expires.
           returns zero if it has already expired
        """
        return max(0.0, self.stop - time.time()) 
    remaining = property(getRemaining, doc = 'Remaining time.')

    def getExpired(self):
        if (time.time() >= self.stop):
            return True
        else:
            return False
    expired = property(getExpired, doc = 'True if expired, False otherwise')

    def restart(self,start = None, duration = None):
        """Starts timer at start time secs for duration secs.
           (fractional from epoc) 
           If start arg is missing then restarts at current time
           If duration arg is missing then restarts for current duration
        """
        if start != None:
            self.start = abs(start) #must be non negative
        else: #use current time
            self.start = time.time()

        if duration != None: 
            self.duration = abs(duration) #must be non negative
        #Otherwise keep old duration

        self.stop = self.start + self.duration

        return (self.start, self.stop)

    def repeat(self):
        """restarts timer at stop so no time lost

        """
        return self.restart(start = self.stop)

    def extend(self, extension = None):
        """Extends timer duration for additional extension seconds (fractional).
           Useful so as not to lose time when  need more/less time on timer

           If extension negative then shortens existing duration
           If extension arg missing then extends for the existing duration
           effectively doubling the time

        """
        if extension == None: #otherwise extend by .duration or double
            extension = self.duration

        duration = self.duration + extension

        return self.restart(start = self.start, duration = duration)


class ConsoleNB(object):
    """Class to manage non blocking reads from console.

       Opens non blocking read file descriptor on console
       Use instance method close to close file descriptor
       Use instance methods getline & put to read & write to console
       Needs os module
    """

    def __init__(self):
        """Initialization method for instance.

        """
        self.fd = None #console file descriptor needs to be opened

    def open(self, port = '', canonical = True):
        """Opens fd on terminal console in non blocking mode.

           port is the serial port or if '' then use os.ctermid() which
           returns path name of console usually '/dev/tty'

           canonical sets the mode for the port. Canonical means no characters
           available until a newline

           os.O_NONBLOCK makes non blocking io
           os.O_RDWR allows both read and write.
           os.O_NOCTTY don't make this the controlling terminal of the process
           O_NOCTTY is only for cross platform portability BSD never makes it the
           controlling terminal

           Don't use print at same time since it will mess up non blocking reads.

           Default is canonical mode so no characters available until newline
           need to add code to enable  non canonical mode

           It appears that canonical mode only applies to the console. For other
           serial ports the characters are available immediately
        """
        if not port:
            port = os.ctermid() #default to console

        self.fd = os.open(port,os.O_NONBLOCK | os.O_RDWR | os.O_NOCTTY)


    def close(self):
        """Closes fd. 

        """
        if self.fd:
            os.close(self.fd)
            self.fd = None


    def getLine(self,bs = 80):
        """Gets nonblocking line from console up to bs characters including newline.

           Returns empty string if no characters available else returns line.
           In canonical mode no chars available until newline is entered.
        """
        line = ''
        try:
            line = os.read(self.fd, bs)
        except OSError, ex1:  #if no chars available generates exception
            try: #need to catch correct exception
                errno = ex1.args[0] #if args not sequence get TypeError
                if errno == 35:
                    pass #No characters available
                else:
                    raise #re raise exception ex1
            except TypeError, ex2:  #catch args[0] mismatch above
                raise ex1 #ignore TypeError, re-raise exception ex1

        return line

    def put(self, data = '\n'):
        """Writes data string to console.

        """
        os.write(self.fd, data)

class SocketNB(object):
    """Class to manage non blocking reads from socket.

       Opens non blocking socket
       Use instance method close to close socket

       Needs socket module
    """

    def __init__(self, ha=None, host = '', port = 55000, bufsize = 1024, 
                 path = '', log = False):
        """Initialization method for instance.

           ha = host address duple (host, port)
           host = '' equivalant to any interface on host
           port = socket port
           bs = buffer size
        """
        self.ha = ha or (host,port) #ha = host address
        self.bs = bufsize
        self.ss = None #server's socket needs to be opened

        self.path = path #path to directory where log files go must end in /
        self.txLog = None #transmit log
        self.rxLog = None #receive log
        self.log = log

    def openLogs(self, path = ''):
        """Open log files

        """
        date = time.strftime('%Y%m%d_%H%M%S',time.gmtime(time.time()))
        name = "%s%s_%s_%s_tx.txt" % (self.path, self.ha[0], str(self.ha[1]), date)
        try:
            self.txLog = open(name, 'w+')
        except IOError:
            self.txLog = None
            self.log = False
            return False
        name = "%s%s_%s_%s_rx.txt" % (self.path, self.ha[0], str(self.ha[1]), date)
        try:
            self.rxLog = open(name, 'w+')
        except IOError:
            self.rxLog = None
            self.log = False
            return False

        return True

    def closeLogs(self):
        """Close log files

        """
        if self.txLog and not self.txLog.closed:
            self.txLog.close()
        if self.rxLog and not self.rxLog.closed:
            self.rxLog.close()

    def open(self):
        """Opens socket in non blocking mode.

           if socket not closed properly, binding socket gets error
              socket.error: (48, 'Address already in use')
        """
        #create socket ss = server socket
        self.ss = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #make socket address reusable. doesn't seem to have an effect.
        self.ss.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.ss.setblocking(0) #non blocking socket

        #bind to Host Address Port
        try:
            self.ss.bind(self.ha)
        except socket.error, e:
            console.terse("socket.error = {0}\n".format(e))
            return False

        if self.log:
            if not self.openLogs():
                return False

        return True

    def reopen(self):
        """     """
        self.close()
        return self.open()

    def close(self):
        """Closes  socket. 

        """
        if self.ss:
            self.ss.close() #close socket
            self.ss = None

        self.closeLogs()

    def receive(self):
        """Perform non blocking read on  socket. 

           returns tuple of form (data, sa)
           if no data then returns ('',None)
           but always returns a tuple with two elements
        """
        try:
            #sa = source address tuple (sourcehost, sourceport)
            data, sa = self.ss.recvfrom(self.bs) 

            message = "Server at {0} received {1} from {2}\n".format(
                str(self.ha),data, str(sa))
            console.profuse(message)

            if self.log and self.rxLog:
                self.rxLog.write("%s\n%s\n" % (str(sa), repr(data)))

            return (data,sa)
        except socket.error, ex1: #ex1 is a socket.error instance
            try:
                errno = ex1.args[0] # if args is not sequence get TypeError
                #ignore resource unavailable error for non blocking, means empty
                if errno == 35: #Resource temporarily unavailable on os x
                    return ('',None) #receive has nothing empty string for data
                elif errno == 11: #Resource temporarily unavailable on debian
                    return ('',None) #receive has nothing empty string for data
                else:
                    raise #re raise exception ex1
            except TypeError, ex2:  #catch args[0] mismatch above
                #ignore type error and re raise original exception ex1
                raise ex1

    def send(self,data, da):
        """Perform non blocking send on  socket. 

           data is string
           da is destination address tuple (destHost, destPort)

        """  
        try:
            result = self.ss.sendto(data,da) #result is number of bytes sent
        except socket.error, e:
            print "socket.error = %s" % e
            result = 0

        console.profuse("Server at {0} sent {1} bytes\n".format(str(self.ha),result))

        if self.log and self.txLog:
            self.txLog.write("%s %s bytes\n%s\n" %
                             (str(da), str(result), repr(data)))

        return result


#Utility Functions

def NameToPath(name):
    """ Converts camel case name into share path where uppercase letters denote
        nodes in path
        
        Assumes Name is of the correct format to be Identifier.
    """
    pathParts = []
    nameParts = list(name)
    for c in nameParts:
        if c.isupper():
            pathParts.append('.')
            pathParts.append(c.lower())
        else:
            pathParts.append(c)
        
    path = ''.join(pathParts)
    return path

nameToPath = NameToPath

def Repack(n, seq):
    """ Repacks seq into a generator of len n and returns the generator.
        The purpose is to enable unpacking into n variables.
        The first n-1 elements of seq are returned as the first n-1 elements of the
        generator and any remaining elements are returned in a tuple as the
        last element of the generator
        None is substituted for missing elements when len(seq) < n
        
        Example:
        
        x = (1, 2, 3, 4)
        tuple(Repack(3, x))
        (1, 2, (3, 4))
        
        x = (1, 2, 3)
        tuple(Repack(3, x))
        (1, 2, (3,))
        
        x = (1, 2)
        tuple(Repack(3, x))
        (1, 2, ())
        
        x = (1, )
        tuple(Repack(3, x))
        (1, None, ())
        
        x = ()
        tuple(Repack(3, x))
        (None, None, ())

    """
    it = iter(seq)
    for _i in range(n - 1):
        yield next(it, None)
    yield tuple(it)

repack = Repack #alias
    

def Just(n, seq):
    """ Returns a generator of just the first n elements of seq and substitutes
        None for any missing elements. This guarantees that a generator of exactly
        n elements is returned. This is to enable unpacking into n varaibles
    
        Example:
        
        x = (1, 2, 3, 4)
        tuple(Just(3, x))
        (1, 2, 3)
        x = (1, 2, 3)
        tuple(Just(3, x))
        (1, 2, 3)
        x = (1, 2)
        tuple(Just(3, x))
        (1, 2, None)
        x = (1, )
        tuple(Just(3, x))
        (1, None, None)
        x = ()
        tuple(Just(3, x))
        (None, None, None)
        
    """
    it = iter(seq)
    for _i in range(n):
        yield next(it, None)
        
just = Just #alias


from abc import ABCMeta,  abstractmethod
class NonStringIterable:
    """ Check for iterable that is not a string
        Works in python 2.6 to 3.x with isinstance(x,NonStringIterable)
        
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __iter__(self):
        while False:
            yield None

    @classmethod
    def __subclasshook__(cls, C):
        if cls is NonStringIterable:
            if any("__iter__" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented

# Faster to use precompiled versions in globaling
def IsPath(s):
    """Returns True if string s is valid Store path name
       Returns False otherwise

       raw string
       this also matches an empty string so need
       r'^([a-zA-Z_][a-zA-Z_0-9]*)?([.][a-zA-Z_][a-zA-Z_0-9]*)*$'

       at least either one of these
       r'^([a-zA-Z_][a-zA-Z_0-9]*)+([.][a-zA-Z_][a-zA-Z_0-9]*)*$'
       r'^([.][a-zA-Z_][a-zA-Z_0-9]*)+$'

       so get
       r'^([a-zA-Z_][a-zA-Z_0-9]*)+([.][a-zA-Z_][a-zA-Z_0-9]*)*$|^([.][a-zA-Z_][a-zA-Z_0-9]*)+$'

       shorthand replace [a-zA-Z_0-9] with  \w which is shorthand for [a-zA-Z_0-9]
       r'^([a-zA-Z_]\w*)+([.][a-zA-Z_]\w*)*$|^([.][a-zA-Z_]\w*)+$'

       ^ anchor to start
       $ anchor to end
       | must either match preceding or succeeding expression
       * repeat previous match zero or more times greedily
       ? repeat previous match zero or one times
       ( ) group
       [ ] char from set of ranges
       [a-zA-Z_] alpha or underscore one and only one
       [a-zA-Z_0-9]* alpha numeric or underscore (zero or more)
       ([a-zA-Z_][a-zA-Z_0-9]*) group made up of one alpha_ and zero or more alphanumeric_
       ([a-zA-Z_][a-zA-Z_0-9]*)? zero or one of the previous group

       ([.][a-zA-Z_][a-zA-Z_0-9]*) group made of one period one alpha_ and zero or more alphanumeric_
       ([.][a-zA-Z_][a-zA-Z_0-9]*)* zero or more of the previous group

       so what it matches.
       if first character is alpha_ then all remaining alphanumeric_ characters will
       match up to but not including first period if any

       from then on it will match groups that start with period one alpha_ and zero
       or more alphanumeric_ until the end

       valid forms
       a
       a1
       .a
       .a1

       a.b
       a1.b2
       .a1.b2
       .a.b

       but not
       .
       a.
       a..b
       ..a
       1.2

    """
    if re.match(r'^([a-zA-Z_]\w*)+([.][a-zA-Z_]\w*)*$|^([.][a-zA-Z_]\w*)+$',s):
        return True
    else:
        return False

def IsIdentifier(s):
    """Returns True if string s is valid python identifier (variable, attribute etc)
       Returns False otherwise

       how to determine if string is valid python identifier

       r'^[a-zA-Z_]\w*$'
       r'^[a-zA-Z_][a-zA-Z_0-9]*$'  #equivalent \w is shorthand for [a-zA-Z_0-9]

       r' = raw string
       ^ = anchor to start
       [a-zA-Z_] = first char is letter or underscore
       [a-zA-Z_0-9] = next char is letter, underscore, or digit
       * = repeat previous character match greedily
       $ = anchor to end

       How
       import re
       reo = re.compile(r'^[a-zA-Z_]\w*$') #compile is faster
       if reo.match('_hello') is not None: #matched returns match object or None

       #re.match caches compiled pattern string compile so faster after first
       if re.match(r'^[a-zA-Z_]\w*$', '_hello') 

       reo = re.compile(r'^[a-zA-Z_][a-zA-Z_0-9]*$')
       reo.match(

    """
    if re.match(r'^[a-zA-Z_]\w*$',s):
        return True
    else:
        return False

def IsIdentPub(s):
    """Returns True if string s is valid python public identifier,
       that is, an identifier that does not start with an underscore
       Returns False otherwise
    """
    if re.match(r'^[a-zA-Z]\w*$',s):
        return True
    else:
        return False

def Sign(x):
    """Calculates the sign of a number and returns
       1 if positive
       -1 if negative
       0 if zero
       should make it so type int or float of x is preserved in return type
    """
    if x > 0.0:
        return 1.0
    elif x < 0.0:
        return -1.0
    else:
        return 0.0


def Delta(desired, actual, wrap = 180.0):
    """Calculate the short rotation for delta = desired - actual
       and delta wraps around at wrap

    """
    #delta = desired  - actual  so
    #desired  = actual  + delta

    return Wrap2(angle = (desired - actual), wrap = wrap)


def Wrap2(angle, wrap = 180.0):
    """Wrap2 = (2 sided one positive one negative) wrap of angle to 
       signed interval [-wrap, + wrap] wrap is half circle
       if wrap = 0 then don't wrap
       angle may be positive or negative
       result is invariant to sign of wrap

       Wrap preserves convention so angle can be in compass or Cartesian coordinates

       Uses property of python modulo operator that implement true 
       clock or circular arithmetic as location on circle
       distance % circumference = location
       if circumference positive then locations postive sign, 
             magnitues increase CW  (CW 0 1 2 3 ... 0)
       if circumference negative then locations negative sign, 
             magnitudes increase CCW  (CCW 0 -1 -2 -3 ... 0)

       if distance positive then wrap distance CW around circle
       if distance negative then wrap distance CCW around circle

       No need for a full wrap in Python since modulo operator does that
        even for negative angles
       angle %= 360.0

    """

    if wrap != 0.0:
        angle %= wrap * 2.0 #wrap to full circle first
        if abs(angle) > abs(wrap): #more than half way round
            angle = (angle - wrap) % (- wrap) #wrap extra on reversed half circle

    return angle


def MoveByHSD(heading = 0.0, speed = 1.0, duration = 0.0):
    """ 
       Returns change in position after moving on heading at speed for duration
       heading in compass coordinates, 0 deg is north, up, cw rotation increases
    """
    deltaNorth = duration * (speed * math.cos(DEGTORAD * heading))
    deltaEast = duration * (speed * math.sin(DEGTORAD * heading))

    return (deltaNorth, deltaEast)

def MoveToHSD(north = 0.0, east = 0.0, 
              heading = 0.0, speed = 1.0, duration = 0.0):
    """ 
       Returns new position after moving on heading at speed for duration
       heading in compass coordinates, 0 deg is north, up, cw rotation increases

       north east order since lat long
    """
    north += duration * (speed * math.cos(DEGTORAD * heading))
    east += duration * (speed * math.sin(DEGTORAD * heading))


    return (north,east)


def RotateFSToNE(heading = 0.0, forward = 0.0, starboard = 0.0):
    """ 
       rotates Forward Starboard vector to North East vector
       heading in compass coordinates, 0 deg is north, up, cw rotation increases

       north east order since lat long
    """
    ch = math.cos(DEGTORAD * heading)
    sh = math.sin(DEGTORAD * heading)
    north = ch * forward - sh * starboard
    east = sh * forward + ch * starboard

    return (north,east)

def RotateNEToFS(heading = 0.0, north = 0.0, east = 0.0):
    """ 
       Rotate north east vector to Forward Starboard
       heading in compass coordinates, 0 deg is north, up, cw rotation increases

       north east order since lat long
    """
    ch = math.cos(DEGTORAD * heading)
    sh = math.sin(DEGTORAD * heading)
    forward = ch * north + sh * east
    starboard = - sh * north + ch * east


    return (forward,starboard)


def AlongCrossTrack(track = 0.0, north = 0.0, east = 0.0, 
                    mag = None, heading = None):
    """ 
       Returns as a tuple, the along and cross track components  of the vector 
       given by (north, east) where the track is from origin to (n, e)
       or by mag (magnitude) heading (degrees) if provided

       track is the track course ( nav angle degrees)
       a positive along track is in the foreward direction of the track
       a negative along track is in the backward direction of the track
       a positive cross track is to the east of the track
       a negative cross track is to the west of the track
    """
    if mag is not None and heading is not None:
        heading = Wrap2(heading)
        north = mag * math.cos(DEGTORAD * heading)
        east = mag * math.sin(DEGTORAD * heading)

    track = Wrap2(track)

    #along track component
    trackNorth = math.cos(DEGTORAD * track)
    trackEast = math.sin(DEGTORAD * track)

    A = north * trackNorth + east * trackEast

    #cross track vector
    crossNorth = north - A * trackNorth
    crossEast = east - A * trackEast

    #cross track magnitude
    C = (crossNorth ** 2.0 + crossEast ** 2.0) ** 0.5

    #fix sign by testing for shortest rotation of cross vector to track direction
    #if z component of cross X track is positive then shortest rotation is CCW
    # and cross is to the right of track
    #if z component of cross x track is negative then shortest rotation is CW
    # and cross is to the left of track

    (x,y,z) = CrossProduct3D((crossEast, crossNorth, 0.0),
                             (trackEast, trackNorth,0.0))

    if z < 0.0: #make C negative if to left of track
        C *= -1

    return (A,C)

def CrabSpeed(track = 0.0,  speed = 2.0, north = 0.0, east = 0.0, 
              mag = None, heading = None):
    """ 
       Returns a tuple of the compensating (crabbed) course angle (in degrees) 
       and the delta crab angle
       and the resulting along track speed (including current and cluster).
       The crabbed course is that needed to compensate for the current
       given by (east, north) or mag (magnitude) heading (degrees) if provided
       Where the resulting along track speed is the projection of 
       the compensating course at speed onto the desired course

       track is the desired track course ( nav angle degrees)
       speed is the cluster speed (must be non zero)

       compensating course = desired course - delta crab angle
       a positive crab angle means the compensating course is to the left
       of the desired course.
       a negative crab angle means the compensating course is to the right
       of the desired course
    """
    if mag is not None and heading is not None:
        heading = Wrap2(heading)
        north = mag * math.cos(DEGTORAD * heading)
        east = mag * math.sin(DEGTORAD * heading)

    track = Wrap2(track)

    (A,C) = AlongCrossTrack(track = track, north = north, east = east)

    #print A
    #print C
    #current compensated course crab = track + delta crab angle
    delta = - RADTODEG * math.asin(C / speed)
    crab = track + delta


    #B = along track component of compensated course
    B = speed * (math.sin(DEGTORAD * crab) * math.sin(DEGTORAD * track) +
                 math.cos(DEGTORAD * crab) * math.cos(DEGTORAD * track)  )

    #print B                 

    return (crab, delta, B + A)


def CrossProduct3D(a,b):
    """Forms the 3 dimentional vector cross product of sequences a and b
       a is crossed onto b
       cartesian coordinates
       returns a 3 tuple
    """
    cx = a[1] * b[2] - b[1] * a[2]
    cy = a[2] * b[0] - b[2] * a[0]
    cz = a[0] * b[1] - b[0] * a[1]

    return (cx,cy,cz)

def DotProduct(a,b):
    """Returns the N dimensional vector dot product of sequences a and b

    """
    dot = 0.0
    for i in range(len(a)):
        dot += a[i] * b[i]

    return dot

def PerpProduct2D(a,b):
    """Computes the the 2D perpendicular product of sequences a and b.
       The convention is a perp b. 
       The product is:
          positive if b is to the left of a
          negative if b is to the right of a
          zero if b is colinear with a
       left right defined as shortest angle (< 180)
    """
    return (a[0] * b[1] - a[1] * b[0])

def DistancePointToTrack2D(a,track, b):
    """Computes the signed distance between point b and  the track ray defined by
       point a and track azimuth track 
       a and b are sequences x (east) coord is  index 0, y (north) coord is index 1
       track in degrees from north
       x = east
       y = north

       The distance is
          positive if b is to the left of the track line
          negative if b is to the right of the track line
          zero if b is colinear with the track line
       left right defined as shortest angle (< 180)
    """
    dx = math.sin(DEGTORAD * track) #normalized vector
    dy = math.cos(DEGTORAD * track) #normalized vector

    return (dx * (b[1] - a[1]) - dy * (b[0] - a[0]))

def SpheroidLLLLToDNDE(a,b):
    """Computes the flat earth approx of change in north east position meters
       for a change in lat lon location on spheroid.   
       from location lat0 lon0 to location lat1 lon1
       point lat0 lon0  in total fractional degrees north east positive
       point lat1, lon1 in total fractional degrees north east positive
       returns tuple (dn,de) where dn is delta north and de is delta east meters
       Uses WGS84 spheroid
    """
    re = 6378137.0 #equitorial radius in meters
    f = 1/298.257223563 #flattening
    e2 = f*(2.0 - f) #eccentricity squared


def SphereLLLLToDNDE(lat0,lon0,lat1,lon1):
    """Computes the flat earth approx of change in north east position meters
       for a change in lat lon location on sphere.   
       from location lat0 lon0 to location lat1 lon1
       point lat0 lon0  in total fractional degrees north east positive
       point lat1, lon1 in total fractional degrees north east positive
       returns tuple (dn,de) where dn is delta north and de is delta east meters
       Uses sphere 1 nm = 1 minute 1852 meters per nautical mile
    """
    r = 6366710.0 #radius of earth in meters = 1852 * 60 * 180/pi

    dlat = (lat1 - lat0) 
    dlon = (lon1 - lon0) 

    avlat = (lat1 + lat0)/2.0
    #avlat = lat0

    dn = r * dlat * DEGTORAD 
    de = r * dlon * DEGTORAD * math.cos( DEGTORAD * avlat)

    return (dn, de)

def SphereLLByDNDEToLL(lat0,lon0,dn,de):
    """Computes new lat lon location on sphere
       from the flat earth approx of  change in position dn (north) meters 
       and de (east) meters from the given location lat0 lon0
       point lat0 lon0  in total fractional degrees north east positive
       returns tuple (lat1,lon1) 
       Uses sphere 1 nm = 1 minute 1852 meters per nautical mile
    """
    r = 6366710.0 #radius of earth in meters = 1852 * 60 * 180/pi

    dlat = dn/(r * DEGTORAD)
    lat1 = lat0 + dlat
    avlat = (lat1 + lat0)/2.0

    try:
        dlon = de / (r * DEGTORAD * math.cos(DEGTORAD * avlat))
    except ZeroDivisionError:
        dlon = 0.0

    lon1 = lon0 + dlon

    avlat = (lat1 + lat0)/2.0

    return (lat1, lon1)

def SphereLLbyRBtoLL(lat0,lon0,range,bearing):
    """Computes new lat lon location on sphere
        from the flat earth approx of  change in range meters at bearing degrees from
         from the given location lat0 lon0
       point lat0 lon0  in total fractional degrees north east positive
       returns tuple (lat1,lon1) 
       Uses sphere 1 nm = 1 minute 1852 meters per nautical mile
    """
    r = 6366710.0 #radius of earth in meters = 1852 * 60 * 180/pi

    dn = range * math.cos(DEGTORAD * bearing)
    de = range * math.sin(DEGTORAD * bearing)

    dlat = dn/(r * DEGTORAD)
    lat1 = lat0 + dlat
    avlat = (lat1 + lat0)/2.0

    try:
        dlon = de / (r * DEGTORAD * math.cos(DEGTORAD * avlat))
    except ZeroDivisionError:
        dlon = 0.0

    lon1 = lon0 + dlon

    avlat = (lat1 + lat0)/2.0

    return (lat1, lon1)

def SphereLLLLToRB(lat0,lon0,lat1,lon1):
    """Computes the flat earth approx of change in range meters bearing degrees
       for a change in lat lon location.   
       from location lat0 lon0 to location lat1 lon1
       point lat0 lon0  in total fractional degrees north east positive
       point lat1, lon1 in total fractional degrees north east positive
       returns tuple (dn,de) where dn is delta north and de is delta east meters
       Uses sphere 1 nm = 1 minute 1852 meters per nautical mile
    """
    r = 6366710.0 #radius of earth in meters = 1852 * 60 * 180/pi

    dlat = (lat1 - lat0) 
    dlon = (lon1 - lon0) 

    avlat = (lat1 + lat0)/2.0
    #avlat = lat0

    dn = r * dlat * DEGTORAD 
    de = r * dlon * DEGTORAD * math.cos( DEGTORAD * avlat)

    range = (dn * dn + de * de) ** 0.5
    bearing = RADTODEG * ((math.pi / 2.0) - math.atan2(dn,de))

    return (range, bearing)


def RBToDNDE(range, bearing):
    """Computes change in north east position for an offset 
       of range (meters) at bearing (degrees)
       returns tuple(delta north, delta East)
    """
    dn = range * math.cos(DEGTORAD * bearing)
    de = range * math.sin(DEGTORAD * bearing)

    return (dn, de)

def DNDEToRB(dn ,de):
    """Computes relative range (meters) and bearing (degrees)for change 
       in position of north (meters) east (meters)
       returns tuple(Range, Bearing)
    """
    range = (dn * dn + de * de) ** 0.5
    bearing = RADTODEG * ((math.pi / 2.0) - math.atan2(dn,de))

    return (range, bearing)

def DegMinToFracDeg(latDeg, latMin, lonDeg, lonMin):
    """Converts location in separated format of Deg and Min
       to combined format of total fractional degrees
       lat is in signed fractional degrees positive = North negative = South
       lon in in signed fractional dregrees positive = East negative = West
       latDeg are in signed degrees North positive South Negative
       latMin are in signed minutes North positive South Negative
       lonDeg are in signed degrees East positive West Negative
       lonMin are in signed minutes East positive West Negative
    """
    if Sign(latDeg) != Sign(latMin):
        latMin = - latMin

    if Sign(lonDeg) != Sign(lonMin):
        lonMin =  - lonMin

    lat = latDeg + (latMin / 60.0)
    lon = lonDeg + (lonMin / 60.0)
    return (lat, lon)

def FracDegToDegMin(lat, lon):
    """Converts location in format of total fractional degrees to
       separated format of deg and minutes
       lat is in signed fractional degrees positive = North negative = South
       lon in in signed fractional dregrees positive = East negative = West
       latDeg are in signed degrees North positive South Negative
       latMin are in signed minutes North positive South Negative
       lonDeg are in signed degrees East positive West Negative
       lonMin are in signed minutes East positive West Negative
    """
    latDeg = int(lat)
    latMin = (lat - latDeg) * 60.0 

    lonDeg = int(lon)
    lonMin = (lon - lonDeg) * 60.0 

    return (latDeg, latMin, lonDeg, lonMin)

def FracDegToHuman(lat, lon):
    """Converts location in format of total fractional degrees to
       tuple (latDM, lonDM) of human friendly string of form  
       latDegXlatMin where X is N if lat positive and S if lat negative
          latDeg in units of integer degrees [0 ,90]
          lat Min in units of fractinal minutes [0.0, 60.0)
       and 
       lonDegXlonMin where X is E if lon positive and W if lon negative
          lonDeg in units of integer degrees [0 ,180]
          lon Min in units of fractinal minutes [0.0, 60.0)

       lat is in signed fractional degrees positive = North, negative = South
          [-90, 90]  
       lon in in signed fractional dregrees positive = East, negative = West
          [-180, 180]

       Does not handle wrapping lat over poles or lon past halfway round
    """
    latDeg, latMin, lonDeg, lonMin = FracDegToDegMin(lat, lon)

    if latDeg >= 0:
        latDM = "%dN%0.3f" % (latDeg, latMin)
    else:
        latDM = "%dS%0.3f" % (-latDeg, -latMin)

    if lonDeg >= 0:
        lonDM = "%dE%0.3f" % (lonDeg, lonMin)
    else:
        lonDM = "%dW%0.3f" % (-lonDeg, -lonMin)

    return (latDM, lonDM)

def HumanLatToFracDeg(latDM):
    """Converts latDM  in human friendly string of form  
       latDegXlatMin where X is N if lat positive and S if lat negative
          latDeg in units of integer degrees [0 ,90]
          lat Min in units of fractinal minutes [0.0, 60.0)

       to lat in total fractional degrees 

       lat is in signed fractional degrees positive = North, negative = South
          [-90, 90]  

       Does not handle wrapping lat over poles or lon past halfway round
    """
    latDM = latDM.upper() 
    if ('N' in latDM): 
        (degrees,minutes) = latDM.split('N')
        lat = int(degrees) + (float(minutes) / 60.0)

    elif ('S' in latDM): 
        (degrees,minutes) = latDM.split('S')
        lat = - (int(degrees) + (float(minutes) / 60.0))

    else:
        raise ValueError, "Bad format for latitude '%s'" % (latDM)

    return (lat)

def HumanLonToFracDeg(lonDM):
    """Converts  lonDM  in human friendly string of form  
       lonDegXlonMin where X is E if lon positive and W if lon negative
          lonDeg in units of integer degrees [0 ,180]
          lon Min in units of fractinal minutes [0.0, 60.0)

       to lon in total fractional degrees 

       lon in in signed fractional dregrees positive = East, negative = West
          [-180, 180]

       Does not handle wrapping lat over poles or lon past halfway round
    """
    lonDM = lonDM.upper() 
    if ('E' in lonDM): 
        (degrees,minutes) = lonDM.split('E')
        lon = int(degrees) + (float(minutes) / 60.0)

    elif ('W' in lonDM): 
        (degrees,minutes) = lonDM.split('W')
        lon = - (int(degrees) + (float(minutes) / 60.0))

    else:
        raise ValueError, "Bad format for longitude '%s'" % (lonDM)

    return (lon)


def HumanToFracDeg(latDM, lonDM):
    """Converts  pair of coordinates  in human friendly strings of form   DegXMin to
       total fractional degrees where
       the result is positive if X is N or E and
       the result is negative if X is S or W 

       Does not handle wrapping over poles or past halfway round
    """
    lat = HumanLatToFracDeg(latDM)
    lon = HumanLonToFracDeg(lonDM)
    return (lat,lon)

def HumanLLToFracDeg(hdm):
    """Converts  a coordinate  in human friendly string of form   DegXMin to
       total fractional degrees where
       the result is positive if X is N or E and
       the result is negative if X is S or W 

       Does not handle wrapping over poles or past halfway round
    """
    dm = REO_LatLonNE.findall(hdm) #returns list of tuples of groups [(deg,min)]
    if dm:
        deg = float(dm[0][0])
        min = float(dm[0][1])
        return (deg + min/60.0)

    dm = REO_LatLonSW.findall(hdm) #returns list of tuples of groups [(deg,min)]
    if dm:
        deg = float(dm[0][0])
        min = float(dm[0][1])
        return (-(deg + min/60.0))

    raise ValueError, "Bad format for lat or lon '%s'" % (hdm)

def Midpoint(latDM0, lonDM0, latDM1, lonDM1):
    """Computes the midpoint  of a trackline between 
       (latDM0,lonDM0) and (latDM1,lonDM1)
       arguments are in human friendly degrees fractional minutes format
       40N35.67  70W56.45
    """
    lat0 = HumanLLToFracDeg(latDM0)
    lon0 = HumanLLToFracDeg(lonDM0)
    lat1 = HumanLLToFracDeg(latDM1)
    lon1 = HumanLLToFracDeg(lonDM1)

    dn, de = SphereLLLLToDNDE(lat0,lon0,lat1,lon1)
    dn = dn/2.0 #get half the distance
    de = de/2.0
    lat1, lon1 =  SphereLLByDNDEToLL(lat0,lon0,dn,de) #midpoint
    latDM, lonDM = FracDegToHuman(lat1, lon1)

    return (latDM, lonDM)

def Endpoint(latDM0, lonDM0, range, bearing):
    """Computes the endpoint  track from latDM, lonDm of range at bearing 

       arguments are in human friendly degrees fractional minutes format
       40N35.67  70W56.45
    """
    lat0 = HumanLLToFracDeg(latDM0)
    lon0 = HumanLLToFracDeg(lonDM0)


    lat1, lon1 = SphereLLbyRBtoLL(lat0,lon0,range,bearing)
    latDM1, lonDM1 = FracDegToHuman(lat1, lon1)

    return (latDM1, lonDM1)

def Blend0(d = 0.0, u = 1.0, s = 1.0):
    """
       blending function trapezoid
       d = delta x = xabs - xdr
       u = uncertainty radius of xabs estimate error
       s = tuning scale factor

       returns blend
    """
    d = float(abs(d))
    u = float(abs(u))
    s = float(abs(s))
    v = d - u #offset by radius

    if v >= s:  #first so if s == 0 catches here so no divide by zero below
        b = 0.0
    elif v <= 0.0:
        b = 1.0
    else: # 0 < v < s
        b = 1.0 - (v / s)

    return b

def Blend1(d = 0.0, u = 1.0, s = 1.0):
    """
       blending function pisig
       d = delta x = xabs - xdr
       u = uncertainty radius of xabs estimate error
       s = tuning scale factor

       returns blend
    """
    v = float(abs(u * s)) #scale uncertainty radius make sure positive
    a = float(abs(d)) #symmetric about origin

    if a >= v or v == 0.0 : #outside uncertainty radius accept delta
        b = 1.0 
    elif a < v/2.0: # inside 1/2 uncertainty radius closer to 0
        b = 2.0 * (a * a)/(v * v)
    else: #greater than 1/2 uncertainty radius closer to 1
        b = 1.0 - (2.0 * (a - v) * (a - v))/ (v * v)

    return b

def Blend2(d = 0.0, u = 1.0, s = 5.0):
    """
       blending function gaussian
       d = delta x = xabs - xdr
       u = uncertainty radius of xabs estimate error
       s = tuning scale factor

       returns blend
    """
    d = float(d)
    u = float(u)
    s = float(abs(s)) # make sure positive

    b = 1.0 - math.exp( - s * (d * d)/(u * u))

    return b

def Blend3(d = 0.0, u = 1.0, s = 0.05):
    """
       blending function polynomial
       d = delta x = xabs - xdr
       u = uncertainty radius of xabs estimate error
       s = tuning scale factor

       returns blend
    """
    d = float(d)
    u = float(u)
    s = min(1.0,float(abs(s))) # make sure positive <= 1.0

    b = 1.0 - s ** ((d * d)/(u * u))

    return b


def PackByte(format = '8',fields = [0x0000]):
    """Packs fields sequence into one byte using format string.

       Each fields element is a bit field and each
       char in format is the corresponding bit field length.
       Assumes unsigned fields values.
       Assumes network big endian so first fields element is high order bits.
       Format string is number of bits per bit field 
       Fields with length of 1 are treated as has having boolean field values
          that is,   nonzero is True and packs as a 1
       for 2-8 length bit fields the field element is truncated 
       to the number of low order bits in the bit field
       if sum of number of bits in format less than 8 last bits are padded
       if sum of number of bits in format greater than 8 returns exception
       to pad just use 0 value in source. 
       example 
       PackByte("1322",(True,4,0,3)). returns 0xc3
    """

    byte = 0x00
    bfp = 8 #bit field position
    bu = 0 #bits used

    for i in range(len(format)):
        bits = 0x00
        bfl = int(format[i])

        if not (0 < bfl <= 8):
            raise ValueError, "Bit field length in format must be > 0 and <= 8"

        bu += bfl
        if bu > 8:
            raise ValueError, "Sum of bit field lengths in format must be <= 8"

        if bfl == 1:
            if fields[i]:
                bits = 0x01
            else:
                bits = 0x00
        else:
            bits = fields[i] & (2**bfl - 1) #bit and to mask out high order bits

        bits <<= (bfp - bfl) #shift left to bit position less bit field size

        byte |= bits #or in bits
        bfp -= bfl #adjust bit field position for next element

    console.profuse("Packed byte = {0:#x}\n".format(byte))

    return byte

def UnpackByte(format = '11111111', byte = 0x00, boolean = True):
    """unpacks source byte into tuple of bit fields given by format string.

       Each char of format is a bit field length.
       returns unsigned fields values.
       Assumes network big endian so first format is high order bits.
       Format string is number of bits per bit field 
       If boolean parameter is True then return boolean values for
          bit fields of length 1

       if sum of number of bits in format less than 8 then remaining
       bits returned as additional element in result.

       if sum of number of bits in format greater than 8 returns exception
       only low order byte of byte is used.

       example 
       UnpackByte("1322",0xc3, False ) returns (1,4,0,3)
       UnpackByte("1322",0xc3, True ) returns (True,4,0,3)
    """

    fields = [] #list of bit fields
    bfp = 8 #bit field position
    bu = 0 #bits used
    byte &= 0xff #get low order byte

    for i in range(len(format)):
        bfl = int(format[i])

        if not (0 < bfl <= 8):
            raise ValueError, "Bit field length in format must be > 0 and <= 8"

        bu += bfl
        if bu > 8:
            raise ValueError, "Sum of bit field lengths in format must be <= 8"

        mask = (2**bfl - 1) << (bfp - bfl) #make mask
        bits = byte & mask #mask off other bits
        bits >>= (bfp - bfl) #right shift to low order bits
        if bfl == 1 and boolean: #convert to boolean
            if bits:
                bits = True
            else:
                bits = False

        fields.append(bits) #assign to fields list

        bfp -= bfl #adjust bit field position for next element

    return tuple(fields) #convert to tuple

def Hexize(s = ''):
    """Converts string s into hex format
       Where each char (byte) in string s is expanded into the 2 charater hex 
       equivalent of the decimal value of each byte
       returns the expanded hex version of the string
    """
    h = ''
    for i in range(len(s)):
        h += ("%02x" % ord(s[i]))
    return h

def Binize(h = ''):
    """Converts string h from hex format into the binary equivalent string by
       compressing every two hex characters into 1 byte that is the binary equivalent
       If h does not have an even number of characters then a 0 is first prepended
       to h
       returns the packed binary  version of the string
    """
    #remove any non hex characters, any char that is not in '0123456789ABCDEF'
    b = h #make copy so iteration not change
    for c in b:
        if c not in string.hexdigits:
            h = h.replace(c,'') #delete characters

    if len(h) % 2: #odd number of characters
        h = '0' + h #prepend a zero to make even number

    p = ''
    for i in xrange(0,len(h),2):
        s = h[i:i+2]
        p = p + struct.pack('!B',int(s,16))

    return p

# convert a decimal (denary, base 10) integer to a binary string (base 2)

def Denary2BinaryStr(n, l = 8):
    '''convert denary integer n to binary string bs, left pad to length l'''
    bs = ''
    if n < 0:  raise ValueError, "must be a positive integer"
    if n == 0: return '0'
    while n > 0:
        bs = str(n % 2) + bs
        n = n >> 1
    return bs.rjust(l,'0')

def Dec2BinStr(n, count=24):
    """returns the binary formated string of integer n, using count number of digits"""
    return "".join([str((n >> y) & 1) for y in range(count-1, -1, -1)])


def PrintHex(s, chunk = 0, chunks = 0, silent = False, separator = '.'):
    """prints elements of string s in hex notation.

       chunk is number of bytes per chunk
       0 means no chunking
       chunks is the number of chunks per line
       0 means no new lines

       silent = True means return formatted string but do not print
    """
    if (chunk < 0):
        raise ValueError, "invalid size of chunk"

    if (chunks < 0):
        raise ValueError, "invalid chunks per line"

    slen = len(s)

    if chunk == 0:
        chunk = slen

    if chunks == 0:
        line = slen
    else:
        line = chunk * chunks


    cc = 0
    ps = ''
    for i in range(len(s)):
        ps += ("%02x" % ord(s[i]))
        #add space or dot if not end of line or end of string
        if ((i + 1) % line) and ((i+1) % slen): 
            if not ((i + 1) % chunk): #end of chunk
                ps += ' ' #space between chunks
            else:
                ps += separator #between bytes in chunk
        elif (i + 1) != slen: # newline if not last line
            ps += '\n' #newline

    if not silent:
        print ps

    return ps


def PrintDecimal(s):
    """prints elements of string s in decimal notation.

    """
    ps = ''
    for i in range(len(s)):
        ps = ps + ("%03d." % ord(s[i]))
    ps = ps[0:-1] #strip trailing .
    print ps


#should also do faster table lookup version CRC16Fast

def CRC16(inpkt):
    """Generates 16 bit crc compatible with ANSI 709.1 and 852

       needs struct module
    """


    poly = 0x1021  # Generator Polynomial
    crc = 0xffff        
    for element in inpkt :
        i = 0
        byte = ord(element)
        while i < 8 :
            crcbit = 0x0
            if (crc & 0x8000):
                crcbit = 0x01
            databit = 0x0   
            if (byte & 0x80):
                databit = 0x01
            crc = crc << 1
            crc = crc & 0xffff
            if (crcbit != databit):
                crc = crc ^ poly
            byte = byte << 1
            byte = byte & 0x00ff
            i += 1
    crc = crc ^ 0xffff
    return struct.pack("!H",crc )

def Ocfn(filename, openMode = 'r+'):
    """Atomically open or create file from filename.

       If file already exists, Then open file using openMode 
       Else create file using write update mode
       Returns file object
    """
    try:
        newfd = os.open(filename, os.O_EXCL | os.O_CREAT | os.O_RDWR, 0664)
        newfile = os.fdopen(newfd,"w+")
    except OSError as ex:
        if ex.errno == errno.EEXIST:
            newfile = open(filename, openMode)
        else:
            raise 
    return newfile 

def Load(file = ""):
    """Loads object from pickled file, returns object"""

    if not file:
        raise ParameterError, "No file to Load form: %s" % file

    f = open(file,"r+")
    p = pickle.Unpickler(f)
    it = p.load()
    f.close()
    return it

def Dump(it = None, file = ""):
    """Pickles  it object to file"""

    if not it:
        raise ParameterError, "No object to Dump: %s" % str(it)

    if not file:
        raise ParameterError, "No file to Dump to: %s" % file


    f = open(file, "w+")
    p = pickle.Pickler(f)
    p.dump(it)
    f.close()




# These test should be redone with assert statements so that can get a boolean
# result that the test passed
def TestConsoleNB():
    """Class ConsoleNB self test"""
    try:
        print "Testing ConsoleNB"
        console = ConsoleNB()
        console.open()

        console.put("Testing nonblocking console\n")
        console.put("Enter characters and hit return: ")
        x = ''
        while not x:
            x = console.getLine()
        console.put("You typed: " + x)
    finally:
        console.close()


def TestSocketNB():
    """Class SocketNB self test """
    try:
        print "Testing SocketNB"
        serverA = SocketNB(port = 6101)
        serverA.open()
        serverB = SocketNB(port = 6102)
        serverB.open()

        serverA.send("A sends to B",serverB.ha)
        print serverB.receive()
        serverA.send("A sends to A",serverA.ha)
        print serverA.receive()
        serverB.send("B sends to A",serverA.ha)
        print serverA.receive()
        serverB.send("B sends to B",serverB.ha)
        print serverB.receive()

    finally:
        serverA.close()
        serverB.close()

def TestBlend0(u = .25, s = .75, steps = 10):
    """Test the Blend0 function

    """
    u = abs(u)
    s = abs(s)
    steps = abs(steps)
    span = u + s
    ss = span / steps
    for x in xrange(-(steps + 1), steps + 2, 1):
        d = x * ss
        b = Blend0(d,u,s)
        print d, b




def Test():
    """Module self test



    """
    pass

if __name__ == "__main__":
    Test()
