"""
navigating.py constants and basic functions for navigation

"""
from __future__ import absolute_import, division, print_function

import sys
import math


# Import ioflo libs
from .sixing import *
from .odicting import odict
from ..base import excepting

from .consoling import getConsole
console = getConsole()

TWOPI = 2.0 * math.pi  # two times pi
DEGTORAD = math.pi / 180.0  # r = DEGTORAD * d
RADTODEG = 180.0 / math.pi  # d = RADTODEG * r

def sign(x):
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

Sign = sign

def wrap2(angle, wrap = 180.0):
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

Wrap2 = wrap2


def delta(desired, actual, wrap = 180.0):
    """Calculate the short rotation for delta = desired - actual
       and delta wraps around at wrap

    """
    #delta = desired  - actual  so
    #desired  = actual  + delta

    return wrap2(angle = (desired - actual), wrap = wrap)

Delta = delta


def moveByHSD(heading = 0.0, speed = 1.0, duration = 0.0):
    """
       Returns change in position after moving on heading at speed for duration
       heading in compass coordinates, 0 deg is north, up, cw rotation increases
    """
    deltaNorth = duration * (speed * math.cos(DEGTORAD * heading))
    deltaEast = duration * (speed * math.sin(DEGTORAD * heading))

    return (deltaNorth, deltaEast)

MoveByHSD = moveByHSD

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
        heading = wrap2(heading)
        north = mag * math.cos(DEGTORAD * heading)
        east = mag * math.sin(DEGTORAD * heading)

    track = wrap2(track)

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
        heading = wrap2(heading)
        north = mag * math.cos(DEGTORAD * heading)
        east = mag * math.sin(DEGTORAD * heading)

    track = wrap2(track)
    (A,C) = AlongCrossTrack(track = track, north = north, east = east)
    #current compensated course crab = track + delta crab angle
    delta = - RADTODEG * math.asin(C / speed)
    crab = track + delta
    #B = along track component of compensated course
    B = speed * (math.sin(DEGTORAD * crab) * math.sin(DEGTORAD * track) +
                 math.cos(DEGTORAD * crab) * math.cos(DEGTORAD * track)  )
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

def sphereLLByDNDEToLL(lat0, lon0, dn, de):
    """
    Returns new lat lon location on sphere in total fractional
    degrees north east positive
    Using the flat earth approx of sphere
    given relative position dn (north) meters and de (east) meters
    from the given location lat0 lon0

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

SphereLLByDNDEToLL = sphereLLByDNDEToLL

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
    if sign(latDeg) != sign(latMin):
        latMin = - latMin

    if sign(lonDeg) != sign(lonMin):
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
        raise ValueError("Bad format for latitude '{0}'".format(latDM))

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
        raise ValueError("Bad format for longitude '{0}'".format(lonDM))

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
        min_ = float(dm[0][1])
        return (deg + min_/60.0)

    dm = REO_LatLonSW.findall(hdm) #returns list of tuples of groups [(deg,min)]
    if dm:
        deg = float(dm[0][0])
        min_ = float(dm[0][1])
        return (-(deg + min_/60.0))

    raise ValueError("Bad format for lat or lon '{0}'".format(hdm))

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
