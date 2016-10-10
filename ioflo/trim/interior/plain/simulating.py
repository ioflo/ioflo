"""simulating.py simulator deed module
   simulates the motion of UUV or USV etc

"""
#print("module {0}".format(__name__))

import math
import time
import struct
from collections import deque
import random


from ....aid.sixing import *
from ....base.globaling import *
from ....aid.odicting import odict
from ....aid import aiding, navigating
from ....aid.navigating import DEGTORAD, RADTODEG
from ....base import doing

from ....aid.consoling import getConsole
console = getConsole()

class SimulatorBase(doing.DoerLapse):
    """
    Base class to provide backwards compatible ._initio interface
    """
    def _initio(self, ioinits):
        """
        Initialize Actor data store interface from ioinits odict
        Wrapper for backwards compatibility to new ._initio signature
        """
        self._prepio(**ioinits)
        return odict()


class SimulatorMotionUuv(SimulatorBase):
    """UUV motion simulator class
    """
    Ioinits=odict(
        group = 'simulator.motion.uuv',
        speed = 'state.speed', speedRate = 'state.speedRate',
        velocity = 'state.velocity',
        depth = 'state.depth', depthRate = 'state.depthRate',
        pitch = 'state.pitch', pitchRate = 'state.pitchRate',
        altitude = 'state.altitude',
        heading = 'state.heading', headingRate = 'state.headingRate',
        position = 'state.position', location = 'state.location',
        rpm = 'goal.rpm', stern = 'goal.stern', rudder = 'goal.rudder',
        current = 'scenario.current', bottom = 'scenario.bottom',
        onset = 'scenario.onset', origin = 'scenario.origin',
        parms = dict(rpmLimit = 1200.0, sternLimit = 20.0, rudderLimit = 20.0,
                     gs = 0.0022, gpr = -0.4, gpp = 0.0, gdb = -0.1, ghr = -0.4))

    def __init__(self, **kw):
        """Initialize instance.
           because of Center of buoyancy Center of gravity separation when pitched
           the relationship between sternPlane and pitch rate is usually nonlinear
           uses poor linear approx
           better would be to make pitch rate function of pitch and stern

        """
        #call super class method
        super(SimulatorMotionUuv,self).__init__(**kw)

        #used in reset to speed up processing
        self.ionames = dict( speed = None, speedRate = None, bottom = None,
                             pitch = None, pitchRate = None,
                             depth = None, depthRate = None, altitude = None,
                             heading = None, headingRate = None)

    def _prepio(self, group, speed, speedRate, velocity,
                 depth, depthRate, pitch, pitchRate, altitude,
                 heading, headingRate, position, location,
                 rpm, stern, rudder, current, bottom, onset, origin, parms = None, **kw):
        """ Override since legacy interface

            group is path name of group in store, group has following subgroups or shares:
              group.parm = share for data structure of fixed parameters or coefficients
                 parm has the following fields:
                    rpmLimit = max rpm of motor
                    sternLimit = max absolute stern angle
                    rudderLimit = max abs rudder angle
                    gs = gain speed due to rpm where speed = gs * rpm
                    gpr = gain pitch rate due to stern where pitch rate = gpr * stern
                    gpp = gain pitch rate due to pitch where pitch rate = gpp * pitch (neg)
                          (cbcg restoring force)
                    gdb = gain depth rate due to buoyancy where depth rate = gdb (neg)
                    ghr = gain heading rate dut to rudder where headingRate = ghr * rudder

              group.elapsed = share copy of time lapse for logging

           speed = share path name output water speed m/s
           speedRate = share path name output water speedRate m/s^2

           velocity = share path name output velocity over ground vector (north east) m/s

           depth = share path name output depth meters positive down
           depthRate = share path name output depthRate meters/second positive down
           pitch = share path name output pitch degrees pitch up positive
           pitchRate = share path name output pitch degrees/second = delta pitch / lapse
           altitude = share path name output altitude off bottom

           heading = share path name output heading deg north =0 positive clock wise
           headingRate = share path name output headingRate deg/sec = delta heading / lapse
           position = share path name output position vector (north, east) m wrt origin on plane
           location = share path name output location vector (lat, lon) m wrt sphere flat earth

           rpm = share path name input rpm
           rudder = share path name input rudder
           stern = share path name input stern plane degrees positive down
           current = share path name input water current vector (north east) m/s
           bottom = share path name input simulated bottom depth of ocean
           onset = share path name input onset (start) position vector (north east)
           origin = share path name input origin (start) location  (lat lon)

           parms = dictionary to initialize group.parm fields

           instance attributes

           .group = copy of group name
           .parm = reference to input parameter share
           .speed = ref to speed share
           .speedRate = ref to speedRate share
           .velocity = ref to velocity share
           .depth = ref to depth share
           .depthRate = ref to depthRate share
           .pitch = ref to pitch share
           .pitchRate = ref to pitchRate share
           .altitude = ref to altitude share
           .heading = ref to heading share
           .headingRate = ref to headingRate share
           .position = ref to position north east share
           .location = ref to location lat lon share

           .rpm = ref to rpm share
           .stern = ref to stern share
           .rudder = ref to rudder share
           .current = ref to current share
           .bottom = ref to bottom share
           .onset = ref to onset share
           .origin = ref to origin share
        """
        self.group = group

        self.parm = self.store.create(group + '.parm')#create if not exist
        if not parms:
            parms = dict(rpmLimit = 1200.0, sternLimit = 20.0,rudderLimit = 20.0,
                         gs = 0.0020, gpr = -0.4, gpp = 0.0, gdb = -0.1, ghr = -0.4)
        self.parm.create(**parms)

        self.elapsed = self.store.create(group + '.elapsed').create(value = 0.0)#create if not exist

        #outputs create share if not exist but force update of value
        self.speed = self.store.create(speed).update(value = 0.0)
        self.speedRate = self.store.create(speedRate).update(value = 0.0)

        self.velocity = self.store.create(velocity)
        self.velocity.update(north = 0.0)
        self.velocity.update(east = 0.0)

        self.depth = self.store.create(depth).update(value = 0.0)
        self.depthRate = self.store.create(depthRate).update(value = 0.0)
        self.pitch = self.store.create(pitch).update(value = 0.0)
        self.pitchRate = self.store.create(pitchRate).update(value = 0.0)
        self.altitude = self.store.create(altitude).update(value = 0.0)
        self.heading = self.store.create(heading).update(value = 0.0)
        self.headingRate = self.store.create(headingRate).update(value = 0.0)

        self.position = self.store.create(position)
        self.position.update(north = 0.0) #preserves order
        self.position.update(east = 0.0)

        self.location = self.store.create(location)
        self.location.update(lat = 0.0) #preserves order
        self.location.update(lon = 0.0)

        #inputs create share if not exists and create value if not exist
        self.rpm = self.store.create(rpm).create(value = 0.0)
        self.stern = self.store.create(stern).create(value = 0.0)
        self.rudder = self.store.create(rudder).create(value = 0.0)
        self.current = self.store.create(current)
        self.current.create(north = 0.0) #preserves field order
        self.current.create(east = 0.0)
        self.bottom = self.store.create(bottom).create(value = 50.0)
        self.onset = self.store.create(onset)
        self.onset.create(north = 0.0) #preserves order
        self.onset.create(east = 0.0)
        self.origin = self.store.create(origin)
        self.origin.create(lat = 0.0) #preserves order
        self.origin.create(lon = 0.0)

    def reset(self, **kwa):
        """Resets simulated motion state to passed in parameters
        """
        for key, value in kwa.iteritems():
            if key in self.ionames:
                getattr(self, key).value = value

    def restart(self):
        """Restart motion  simulator

        """
        self.stamp = self.store.stamp
        self.lapse = 0.0

        #need to init position here since onset may be changed at build time by init command
        if self.position.stamp is None: #only on first run
            #init position to onset where vehicle starts relative to 0,0 origin
            self.position.update(north = self.onset.data.north, east = self.onset.data.east)

        #need to init location here since origin may be changed at build time by init command
        if self.location.stamp is None: #only on first run
            #init location to origin lat lon
            self.location.update(lat = self.origin.data.lat, lon = self.origin.data.lon)

    def action(self, **kw):
        """Updates simulated motion state of vehicle
        """
        super(SimulatorMotionUuv,self).action(**kw) #lapse updated here

        self.elapsed.value = self.lapse #store lapse for logging

        if self.lapse <= 0.0: #only evaluate if lapse positive so rate calc good
            return

        rpm = self.rpm.value
        rpm = min(abs(self.parm.data.rpmLimit),max(0.0, rpm)) #limit rpm

        rudder = self.rudder.value
        rudderLimit = abs(self.parm.data.rudderLimit)
        rudder = min(rudderLimit,max(-rudderLimit,rudder)) #limit rudder

        stern = self.stern.value
        sternLimit = abs(self.parm.data.sternLimit)
        stern = min(sternLimit,max(-sternLimit, stern)) #limit stern

        speedLast = self.speed.value
        speed = self.parm.data.gs * rpm
        self.speed.value = speed

        speedRate = (speed - speedLast)/self.lapse
        self.speedRate.value = speedRate

        #slant distance traveled
        slant = speed * self.lapse

        #Pitch
        pitchLast = self.pitch.value
        #linear approximation
        #pitchrate a function of stern (gpr) and restoring force cbcg (gpp) as a function of pitch
        pitchRate = self.parm.data.gpr * stern + self.parm.data.gpp * pitchLast
        self.pitchRate.value = pitchRate

        pitch = pitchLast + self.lapse * pitchRate
        self.pitch.value = pitch

        #Depth
        depthLast = self.depth.value #need for horizontal component position change
        #vertical component of slant is depth change
        #positive pitch decreases depth also buoyancy term gdb that changes depth
        depth = depthLast - slant * math.sin(DEGTORAD * pitch) + self.parm.data.gdb * self.lapse
        #depth delta calculation assumes that if trying to change depth
        #but can't when on suface that horizontal component of motion
        #still needs to be reduced since vehicle slows down when pitched
        depthChange = depth - depthLast #virtual depth change
        depth = max(0.0,depth) #can't have negative depth
        self.depth.value = depth

        depthRate = (depth - depthLast)/self.lapse #actual depth rate of change
        self.depthRate.value = depthRate

        #altitude
        altitude = self.bottom.value - depth
        self.altitude.value = altitude

        #Heading
        headingRate = self.parm.data.ghr * rudder
        self.headingRate.value = headingRate

        headingLast = self.heading.value #need for position change
        heading = headingLast +  self.lapse * headingRate

        #Position
        #average heading over time lapse to calc position change must avg before wrap around
        headAvg = (heading + headingLast)/2.0
        #don't remember why want heading to be [0, 360] instead of [-180, 180]
        #if the latter we could use navigating.Wrap2()
        heading %= 360.0 #mod 360 to wrap aound
        if (heading < 0.0): #if negative make equiv positive
            heading += 360.0
        self.heading.value = heading

        #scale by horiz component of slant when changing depth
        horizontal = (slant**2 + depthChange**2)**0.5

        #heading angle convention  0 is north increasing clockwise
        #cartesian angle convention is 0 east increasing counter clockwise
        #cartesion angle = pi/2 - heading angle
        #cos(pi/2 - psi) = sin(psi)
        #sin(pi/2 - psi) = cos(psi)

        north = self.position.data.north
        east = self.position.data.east

        deltaNorth = horizontal * math.cos(DEGTORAD * headAvg) +\
            self.current.data.north * self.lapse
        deltaEast = horizontal  * math.sin(DEGTORAD * headAvg) +\
            self.current.data.east * self.lapse

        self.velocity.update(north = (deltaNorth / self.lapse),
                             east = (deltaEast / self.lapse))

        self.position.update(north = north + deltaNorth, east = east + deltaEast)

        lat, lon = navigating.SphereLLByDNDEToLL(self.location.data.lat,self.location.data.lon,deltaNorth,deltaEast)
        self.location.update(lat = lat, lon = lon)

    def _expose(self):
        """
           prints out motion state

        """
        print("Simulator %s stamp = %s  lapse = %0.3f" % (self.name, self.stamp,self.lapse))
        print("speed = %0.3f, rpm = %0.3f depth = %0.3f  pitch = %0.3f stern plane = %0.3f" %\
              (self.speed.value, self.rpm.value, self.depth.value, self.pitch.value, self.stern.value))
        print("heading = %0.3f rudder = %0.3f" %\
              (self.heading.value, self.rudder.value))
        print("vel north = %0.3f vel east = %0.3f, pos north = %0.3f pos east = %0.3f" %\
              (self.velocity.data.north, self.velocity.data.east,
               self.position.data.north, self.position.data.east))

class SimulatorMotionUsv(SimulatorBase):
    """USV motion simulator class
    """
    Ioinits=odict(
        group = 'simulator.motion.usv',
        speed = 'state.speed', speedRate = 'state.speedRate',
        velocity = 'state.velocity',
        heading = 'state.heading', headingRate = 'state.headingRate',
        position = 'state.position',
        rpm = 'goal.rpm', rudder = 'goal.rudder',
        current = 'scenario.current',
        onset = 'scenario.onset',
        parms = dict(rpmLimit = 3000.0,  rudderLimit = 20.0,
                     gs = 0.0025,  ghr = -0.25))

    def __init__(self,  **kw):
        """Initialize instance.
        """
        #call super class method
        super(SimulatorMotionUsv,self).__init__(**kw)

        #used in reset to speed up processing
        self.ionames = dict( speed = None, speedRate = None,
                             heading = None, headingRate = None)

    def _prepio(self, group, speed, speedRate,  velocity,
                 heading, headingRate, position,
                 rpm, rudder, current, onset, parms = None, **kw):
        """ Override since legacy interface

            group is path name of group in store, group has following subgroups or shares:
              group.parm = share for data structure of fixed parameters or coefficients
                 parm has the following fields:
                    rpmLimit = max rpm of motor
                    rudderLimit = max abs rudder angle
                    gs = gain speed  where speed = gs * rpm
                    ghr = gain heading rate where headingRate = ghr * rudder

              group.elapsed = share copy of time lapse for logging

           speed = share path name output water speed m/s
           speedRate = share path name output water speedRate m/s^2

           velocity = share path name output velocity over ground vector (north east) m/s

           heading = share path name output heading deg north =0 positive clock wise
           headingRate = share path name output headingRate deg/sec = delta heading / lapse
           position = share path name output position vector (north, east) m wrt origin on plane

           rpm = share path name input rpm
           rudder = share path name input rudder
           current = share path name input water current vector (north east) m/s
           onset = share path name input onset (start) position vector (north east)

           parms = dictionary to initialize group.parm fields

           instance attributes

           .group = copy of group name
           .parm = reference to input parameter share
           .speed = ref to speed share
           .speedRate = ref to speedRate share
           .velocity = ref to velocity share
           .heading = ref to heading share
           .headingRate = ref to headingRate share
           .position = ref to position north east share

           .rpm = ref to rpm share
           .rudder = ref to rudder share
           .current = ref to current share
           .onset = ref to onset share
        """
        self.group = group

        self.parm = self.store.create(group + '.parm')#create if not exist
        if not parms:
            parms = dict(rpmLimit = 3000.0, rudderLimit = 20.0,
                         gs = 0.0025, ghr = -0.001)

        self.parm.create(**parms)

        self.elapsed = self.store.create(group + '.elapsed').create(value = 0.0)#create if not exist

        #outputs create share if not exist but force update of value
        self.speed = self.store.create(speed).update(value = 0.0)
        self.speedRate = self.store.create(speedRate).update(value = 0.0)

        self.velocity = self.store.create(velocity)
        self.velocity.update(north = 0.0)
        self.velocity.update(east = 0.0)

        self.heading = self.store.create(heading).update(value = 0.0)
        self.headingRate = self.store.create(headingRate).update(value = 0.0)

        self.position = self.store.create(position)
        self.position.update(north = 0.0) #preserves order
        self.position.update(east = 0.0)

        #inputs create share if not exists and create value if not exist
        self.rpm = self.store.create(rpm).create(value = 0.0)
        self.rudder = self.store.create(rudder).create(value = 0.0)
        self.current = self.store.create(current)
        self.current.create(north = 0.0) #preserves field order
        self.current.create(east = 0.0)
        self.onset = self.store.create(onset)
        self.onset.create(north = 0.0) #preserves order
        self.onset.create(east = 0.0)
        #init onset position where vehicle starts relative to 0,0 origin
        self.position.update(north = self.onset.data.north, east = self.onset.data.east)

    def reset(self, **kwa):
        """Resets simulated motion state to passed in parameters
        """
        for key, value in kwa.iteritems():
            if key in self.ionames:
                getattr(self, key).value = value

    def restart(self):
        """Restart motion  simulator

        """
        self.stamp = self.store.stamp
        self.lapse = 0.0
        #self.position.update(self.onset.items())

    def action(self, **kw):
        """Updates simulated motion state of vehicle
        """
        super(SimulatorMotionUsv,self).action(**kw) #lapse updated here

        #self.elapsed.updateJointly(value = self.lapse, stamp = stamp) #store lapse for logging
        self.elapsed.value = self.lapse

        if self.lapse <= 0.0: #only evaluate controller if lapse positive so rate calc good
            return

        rpm = self.rpm.value
        rpm = min(abs(self.parm.data.rpmLimit),max(0.0, rpm)) #limit rpm

        rudder = self.rudder.value
        rudderLimit = abs(self.parm.data.rudderLimit)
        rudder = min(rudderLimit,max(-rudderLimit,rudder)) #limit rudder

        speedLast = self.speed.value
        speed = self.parm.data.gs * rpm
        self.speed.value = speed

        speedRate = (speed - speedLast)/self.lapse
        self.speedRate.value = speedRate

        #Heading
        headingRate = self.parm.data.ghr * speed * rudder
        self.headingRate.value = headingRate

        headingLast = self.heading.value #need for position change
        heading = headingLast +  self.lapse * headingRate

        #Position
        #average heading over time lapse to calc position change must avg before wrap around
        headAvg = (heading + headingLast)/2.0
        #don't remember why want heading to be [0, 360] instead of [-180, 180]
        #if the latter we could use navigating.Wrap2()
        heading %= 360.0 #mod 360 to wrap around
        if (heading < 0.0): #if negative make equiv positive
            heading += 360.0
        self.heading.value = heading

        #distance traveled
        horizontal = speed * self.lapse

        #heading angle convention  0 is north increasing clockwise
        #cartesian angle convention is 0 east increasing counter clockwise
        #cartesion angle = pi/2 - heading angle
        #cos(pi/2 - psi) = sin(psi)
        #sin(pi/2 - psi) = cos(psi)
        north = self.position.data.north
        east = self.position.data.east

        deltaNorth = horizontal * math.cos(DEGTORAD * headAvg) +\
            self.current.data.north * self.lapse
        deltaEast = horizontal  * math.sin(DEGTORAD * headAvg) +\
            self.current.data.east * self.lapse

        self.velocity.update(north = (deltaNorth / self.lapse),
                             east = (deltaEast / self.lapse))

        self.position.update(north = north + deltaNorth, east = east + deltaEast)

    def _expose(self):
        """
           prints out motion state

        """
        print("Simulator %s stamp = %s  lapse = %0.3f" % (self.name, self.stamp,self.lapse))
        print("speed = %0.3f, rpm = %0.3f heading = %0.3f rudder = %0.3f north = %0.3f east = %0.3f" %\
              (self.speed.value, self.rpm.value, self.heading.value, self.rudder.value))
        print("vel north = %0.3f vel east = %0.3f, pos north = %0.3f pos east = %0.3f" %\
              (self.velocity.data.north, self.velocity.data.east,
               self.position.data.north, self.position.data.east))

class SimulatorSensorGps(SimulatorBase):
    """GPS sensor simulator class
    """
    Ioinits=odict(
        group = 'simulator.sensor.gps',
        positionOut = 'gps.position', velocityOut = 'gps.velocity',
        error = 'gps.error',
        heading = 'heading.output', speed = 'state.speed',
        positionIn = 'state.position', velocityIn = 'state.velocity',
        scenario = 'scenario.gps',
        parms = dict(noiseBand = 5.0,  noiseJitter = 2.5,
                     noiseVelocity = 0.1))

    def __init__(self, **kw):
        """Initialize instance.
        """
        #call super class method
        super(SimulatorSensorGps,self).__init__(**kw)

    def _prepio(self, group, positionOut, velocityOut, error,
                 heading, speed,  positionIn, velocityIn,
                 scenario, parms = None, **kw):
        """ Override since legacy interface

            group is path name of group in store, group has following subgroups or shares:
              group.parm = share for data structure of fixed parameters or coefficients
                 parm has the following fields:
                    noiseBand = meters max error in position from noise simulated
                    noiseJitter = meters/second max delta position noise
                    noiseVelocity = sigma of velocity noise

              group.elapsed = share copy of time lapse for logging

           positionOut = share path name output position meters north east GPS sim
           velocityOut = share path name output velocity m/s north east for GPS sim
           error = share path name output position error


           heading = share path name input heading deg north =0 positive clock wise
           speed = share path name input speed m/s

           positionIn = share path name input position vector (north, east) m wrt origin on plane
           velocityIn = share path name input ground velocity north east m/s

           scenario = share path name input scenario (for dropouts etc)
           parms = dictionary to initialize group.parm fields

           instance attributes

           .group = copy of group name
           .parm = reference to input parameter share

           .positionOut = ref to gps position share
           .velocityOut = ref to gps velocity share
           .error = ref to gps position error


           .heading = ref to input heading share
           .speed = ref to input speed share
           .positionIn = ref to input position north east share
           .velocityIn = relf to input velocity share

           .scenario = ref to input scenario dropout

        """
        self.group = group

        self.parm = self.store.create(group + '.parm')#create if not exist
        if not parms:
            parms = dict(noiseBand = 5.0, noiseJitter = 2.5, noiseVelocity = 0.1)

        self.parm.create(**parms)
        self.parm.data.noiseBand = abs(self.parm.data.noiseBand)
        self.parm.data.noiseJitter = abs(self.parm.data.noiseJitter)
        self.parm.data.noiseVelocity = abs(self.parm.data.noiseVelocity)

        self.elapsed = self.store.create(group + '.elapsed').create(value = 0.0)#create if not exist

        #outputs create share if not exist but force update of value
        self.positionOut = self.store.create(positionOut)
        self.positionOut.update(north = 0.0) #preserves order
        self.positionOut.update(east = 0.0)

        self.velocityOut = self.store.create(velocityOut)
        self.velocityOut.update(north = 0.0) #preserves order
        self.velocityOut.update(east = 0.0)

        self.error = self.store.create(error)
        self.error.update(north = 0.0) #preserves order
        self.error.update(east = 0.0)

        #inputs create share if not exists and create value if not exist
        self.heading = self.store.create(heading).create(value = 0.0)
        self.speed = self.store.create(speed).create(value = 0.0)

        self.positionIn = self.store.create(positionIn)
        self.positionIn.create(north = 0.0)#preserves order
        self.positionIn.create(east = 0.0)

        self.velocityIn = self.store.create(velocityIn)
        self.velocityIn.create(north = 0.0)#preserves order
        self.velocityIn.create(east = 0.0)

        self.scenario = self.store.create(scenario).create(dropout = 0)
        #self.position.update(self.idealPosition.items()) #init position

    def restart(self):
        """Restart motion  simulator

        """
        self.stamp = self.store.stamp
        self.lapse = 0.0

    def action(self, **kw):
        """Updates simulated motion state of vehicle
        """
        super(SimulatorSensorGps,self).action(**kw) #lapse updated here

        #self.elapsed.updateJointly(value = self.lapse, stamp = stamp) #store lapse for logging
        self.elapsed.value = self.lapse

        if self.lapse <= 0.0: #only evaluate controller if lapse positive so rate calc good
            return

        if self.scenario.data.dropout: #location where no gps
            return

        #not used speed & heading
        speed = self.speed.value
        heading = self.heading.value

        en = self.error.data.north
        ee = self.error.data.east

        #jitter = self.parm.data.noiseJitter * self.lapse
        jitter = self.parm.data.noiseJitter
        band = self.parm.data.noiseBand
        vsigma = self.parm.data.noiseVelocity

        stamp = self.stamp

        en = min(band, max(-band, 0.6 * en + 0.4 * random.gauss(0.0, jitter)))
        #en = min(band, max(-band, 3 * jitter * math.cos(stamp * math.pi/2.0) + random.gauss(0.0, jitter/3.0)))
        #en = min(band, max(-band, 0.8 * en + 0.2 * random.gauss(0.0, jitter)))
        #en = min(band, max(-band, 0.9 * errorNorth + 0.1 * random.uniform(-jitter, jitter)))

        ee = min(band, max(-band, 0.6 * ee + 0.4 * random.gauss(0.0, jitter)))
        #ee = min(band, max(-band, 3 *jitter * math.cos(stamp * math.pi/2.0) + random.gauss(0.0, jitter/3.0)))
        #ee = min(band, max(-band, 0.8 * ee + 0.2 * random.gauss(0.0, jitter)))
        #ee = min(band, max(-band, 0.9 * errorEast + 0.1 * random.uniform(-jitter, jitter)))

        vsigma3 = 3.0 * vsigma
        evn = min(vsigma3, max(-vsigma3, random.gauss(0.0, vsigma)))
        eve = min(vsigma3, max(-vsigma3, random.gauss(0.0, vsigma)))

        self.positionOut.update(north = self.positionIn.data.north + en,
                                east = self.positionIn.data.east + ee)
        self.velocityOut.update(north = self.velocityIn.data.north + evn,
                                east = self.velocityIn.data.east + eve)
        self.error.update(north = en, east = ee)

    def _expose(self):
        """
           prints out sensor state

        """
        print("Simulator %s stamp = %s  lapse = %0.3f" % (self.name, self.stamp,self.lapse))
        print("north = %0.3f east = %0.3f, vel north = %0.3f vel east = %0.3f" %\
              (self.position.data.north, self.position.data.east,
               self.velocity.data.north, self.velocity.data.east))

class SimulatorSensorDvl(SimulatorBase):
    """DVLSensorSimulator DeedLapse Deed Class
       DVL sensor simulator class
    """
    Ioinits=odict(
        group = 'simulator.sensor.dvl',
        velocity = 'dvl.velocity', currentOut = 'dvl.current',
        altitude = 'dvl.altitude',
        heading = 'heading.output', speed = 'state.speed',
        currentIn = 'scenario.current',
        bottom = 'scenario.bottom',
        scenario = 'scenario.dvl',
        parms = dict(velSigma = 0.01, bias = 0.1, altSigma = 0.01))

    def __init__(self, **kw):
        """Initialize instance.
        """
        #call super class method
        super(SimulatorSensorDvl,self).__init__(**kw)

    def _prepio(self, group, velocity, currentOut, altitude,
                 heading, speed, currentIn, bottom,
                 scenario, parms = None, **kw):
        """ Override since legacy interface

            group is path name of group in store, group has following subgroups or shares:
              group.parm = share for data structure of fixed parameters or coefficients
                 parm has the following fields:
                    velSigma = noise parameter  in velocity measurement
                    bias = bias parameter in velocity measurement
                    altSigma = noise parameter altitude measurements


              group.elapsed = share copy of time lapse for logging

           velocity = share path name output velocity mm/s forward starboard sim
           currentOut = share path name output current m/s forward starboard sim
           altitude = share path name output altitude m sim

           heading = share path name input heading deg north =0 positive clock wise
           speed = share path name input speed m/s

           currentIn = share path name input current vector (north, east) m wrt origin on plane
           bottom = share path name input bottom depth m
           scenario = share path name input scenario (for dropouts etc)
           parms = dictionary to initialize group.parm fields

           instance attributes

           .group = copy of group name
           .parm = reference to input parameter share

           .velocity = ref to dvl velocity share
           .current = ref to dvl current share
           .altitude = ref to altitude share

           .heading = ref to heading share
           .speed = ref to speed share

           .currentIn = ref to input current north east share
           .bottom = ref to input bottom
           .scenario = ref to input dvl scenario for dropout
        """
        self.group = group

        self.parm = self.store.create(group + '.parm')#create if not exist
        if not parms:
            parms = dict(velSigma = 0.01, bias = 0.001, altSigma = 0.01)

        self.parm.create(**parms)
        self.parm.data.velSigma = abs(self.parm.data.velSigma)
        self.parm.data.altSigma = abs(self.parm.data.altSigma)

        self.elapsed = self.store.create(group + '.elapsed').create(value = 0.0)#create if not exist

        #outputs create share if not exist but force update of value

        self.velocity = self.store.create(velocity)
        self.velocity.update(forward = 0.0) #preserves order
        self.velocity.update(starboard = 0.0)

        self.currentOut = self.store.create(currentOut)
        self.currentOut.update(forward = 0.0) #preserves order
        self.currentOut.update(starboard = 0.0)
        self.currentOut.update(north = 0.0) #preserves order
        self.currentOut.update(east = 0.0)

        self.altitude = self.store.create(altitude).create(value = 0.0)

        #inputs create share if not exists and create value if not exist
        self.heading = self.store.create(heading).create(value = 0.0)
        self.speed = self.store.create(speed).create(value = 0.0)
        self.currentIn = self.store.create(currentIn)
        self.currentIn.create(north = 0.0)#preserves order
        self.currentIn.create(east = 0.0)
        self.bottom = self.store.create(bottom).create(value = 0.0)
        self.scenario = self.store.create(scenario).create(dropout = 0)


    def restart(self):
        """Restart motion  simulator

        """
        self.stamp = self.store.stamp
        self.lapse = 0.0

    def action(self, **kw):
        """Updates simulated motion state of vehicle
        """
        super(SimulatorSensorDvl,self).action(**kw) #lapse updated here

        #self.elapsed.updateJointly(value = self.lapse, stamp = stamp) #store lapse for logging
        self.elapsed.value = self.lapse

        if self.lapse <= 0.0: #only evaluate controller if lapse positive so rate calc good
            return

        if self.scenario.data.dropout: #location where no dvl
            return


        heading = self.heading.value #need for position change
        speed = self.speed.value

        cn = self.currentIn.data.north
        ce = self.currentIn.data.east
        alt = self.bottom.value

        vsigma = self.parm.data.velSigma
        bias = self.parm.data.bias
        asigma = self.parm.data.altSigma

        #transform to body forward starboard
        cf, cs = navigating.RotateNEToFS(heading, cn, ce)
        vf = speed + cf
        vs = cs

        vsigma3 = vsigma * 3.0
        noise = min(vsigma3, max(-vsigma3, random.gauss(0.0, vsigma)))
        #vf += noise + bias * self.lapse
        #vs += noise + bias * self.lapse

        vf += noise + bias
        vs += noise + bias

        noise = min(vsigma3, max(-vsigma3, random.gauss(0.0, vsigma)))
        cf += noise
        cs += noise
        cn, ce = navigating.RotateFSToNE(heading, cf, cs)

        asigma3 = asigma * 3.0
        noise = min(asigma3, max(-asigma3, random.gauss(0.0, asigma)))
        alt += noise

        self.velocity.update(forward = vf, starboard = vs)
        self.currentOut.update(forward = cf, starboard = cs, north = cn, east = ce)
        self.altitude.value = alt

    def _expose(self):
        """
           prints out sensor state

        """
        print("Simulator %s stamp = %s  lapse = %0.3f" % (self.name, self.stamp,self.lapse))
        format = "vel forward = %0.3f vel starboard = %0.3f"
        format += "cur forward = %0.3f cur starboard = %0.3f altitude = %0.3f"
        print(format %\
              (self.velocity.data.forward, self.velocity.data.starboard,
               self.current.data.forward, self.current.data.starboard,
               self.altitude.value))

class SimulatorSensorCompass(SimulatorBase):
    """compass sensor simulator class
    """
    Ioinits = odict(
        group = 'simulator.sensor.compass',
        output = 'compass',
        input = 'state.heading', depth = 'state.depth',
        scenario = 'scenario.magnetic',
        parms = dict(phase = 24.0, amp = 1.0, sigma = 0.1))

    def __init__(self, **kw):
        """Initialize instance.
        """
        #call super class method
        super(SimulatorSensorCompass,self).__init__(**kw)

    def _prepio(self, group, output,input, scenario, parms = None, **kw):
        """ Override since legacy interface

            group is path name of group in store, group has following subgroups or shares:
              group.parm = share for data structure of fixed parameters or coefficients
                 parm has the following fields:
                    phase = phase of sinusoid error component degrees
                    amp = amplitude of sinusoid error component degrees
                    sigma = noise stdev of error component degrees


              group.elapsed = share copy of time lapse for logging

           output = share path name output magnetic heading degrees

           input = share path name input heading true deg north =0 positive clock wise
              true = mag + declination
           scenario = share path name input scenario (for scenario.declination)
           parms = dictionary to initialize group.parm fields

           instance attributes

           .group = copy of group name
           .parm = reference to input parameter share

           .output = ref to dvl velocity share
           .input = ref to heading share
           .scenario = ref to input scenario declination

        """
        self.group = group

        self.parm = self.store.create(group + '.parm')#create if not exist
        if not parms:
            parms = dict(phase = 45, amp = 1.0, sigma = 0.1)

        self.parm.create(**parms)
        #phase can be negative
        self.parm.data.amp = abs(self.parm.data.amp)
        self.parm.data.sigma = abs(self.parm.data.sigma)

        self.elapsed = self.store.create(group + '.elapsed').create(value = 0.0)#create if not exist

        #outputs
        self.output = self.store.create(output).update(value = 0.0)
        #inputs
        self.input = self.store.create(input).create(value = 0.0)
        self.scenario = self.store.create(scenario).create(declination = 0.0)

    def restart(self):
        """Restart motion  simulator

        """
        self.stamp = self.store.stamp
        self.lapse = 0.0

    def action(self, **kw):
        """Updates simulated sensor
        """
        super(SimulatorSensorCompass,self).action(**kw) #lapse updated here

        #self.elapsed.updateJointly(value = self.lapse, stamp = stamp) #store lapse for logging
        self.elapsed.value = self.lapse

        if self.lapse <= 0.0: #only evaluate controller if lapse positive so rate calc good
            return

        trueHeading = self.input.value #need for position change
        declination =  self.scenario.data.declination

        phase = self.parm.data.phase
        amp = self.parm.data.amp
        sigma = self.parm.data.sigma

        sigma3 = sigma * 3.0
        noise = min(sigma3, max(-sigma3, random.gauss(0.0, sigma)))

        error = amp * math.cos(DEGTORAD * (trueHeading + phase)) + noise

        heading = trueHeading - declination + error #magnetic heading with error
        heading %= 360.0 #mod 360 in case wrapped around
        if (heading < 0.0): #if negative make equiv positive
            heading += 360.0

        self.output.value = heading

    def _expose(self):
        """
           prints out sensor state

        """
        print("Simulator %s stamp = %s  lapse = %0.3f" % (self.name, self.stamp,self.lapse))
        format = "heading = %0.3f phase = %0.3f amp = %0.3f sigma = %0.3f"
        print(format %\
              (self.output.value, self.parm.data.phase,
               self.parm.data.amp, self.parm.data.sigma))

class SimulatorSalinityLinear(SimulatorBase):
    """linear salinity simulator class
    """
    Ioinits = odict(
        group = 'simulator.salinity.linear',
        output = 'ctdsim', depth = 'state.depth',
        input = 'state.position',
        parms = dict(track = 0.0, north = 0.0, east = 0.0,
                     middle = 32.0, spread = 4.0, rising = True, width = 500.0,
                     layer = 20.0, shift = 2.0))

    def __init__(self, **kw):
        """Initialize instance.


           inherited instance attributes
           .stamp = time stamp
           .lapse = time lapse between updates of controller
           .name
           .store

        """
        #call super class method
        super(SimulatorSalinityLinear,self).__init__(**kw)


    def _prepio(self, group, output,input, depth, parms = None, **kw):
        """ Override since legacy interface

                       group is path name of group in store, group has following subgroups or shares:
              group.parm = share for data structure of fixed parameters or coefficients
                 parm has the following fields:
                    track = heading of gradient middle
                    north = north coord for gradient middle
                    east = east coord for gradient middle
                    middle = salinity at center of front
                    spread = total variation in salinity middle - spread/2 to middle + spread/2
                    rising = direction of gradient rising from right to left is True
                    width = distance over which total variation occurs
                                spread occurs over trackline - width/2 to trackline + width/2
                    layer = depth where center of gradient is at middle value
                    shift = shift in center of gradient with depth

              group.elapsed = share copy of time lapse for logging

           output = share path name output ctd

           input = share path name input position of vehicle

           depth = share path name depth of vehicle

           parms = dictionary to initialize group.parm fields

           instance attributes

           .group = copy of group name
           .parm = reference to input parameter share

           .output = ref to ctd salinity share
           .input = ref to vehicle position share
           .depth = ref to vehicle depth share
        """
        self.group = group

        self.elapsed = self.store.create(group + '.elapsed').create(value = 0.0)#create if not exist

        #outputs
        self.output = self.store.create(output).update(salinity = 0.0)

        #inputs
        self.input = self.store.create(input)
        self.input.create(north = 0.0)
        self.input.create(east = 0.0)
        self.depth = self.store.create(depth).create(value = 0.0)

        #parms
        self.parm = self.store.create(group + '.parm')#create if not exist
        if not parms:
            parms = dict(track = 15, north = 0.0, east = 0.0, middle = 32.0,
                         spread  = 3.0, rising = True, width = 1000,
                         layer = 20.0, shift = 2.0)

        self.parm.create(**parms)

    def restart(self):
        """Restart sensor  simulator

        """
        self.stamp = self.store.stamp
        self.lapse = 0.0

    def action(self, **kw):
        """Updates simulated sensor
        """
        super(SimulatorSalinityLinear,self).action(**kw) #lapse updated here

        #self.elapsed.updateJointly(value = self.lapse, stamp = stamp) #store lapse for logging
        self.elapsed.value = self.lapse

        #if self.lapse <= 0.0: #only evaluate simulator if lapse positive so rate calc good
        #   return

        pn = self.input.data.north  #vehicle position
        pe = self.input.data.east

        track = self.parm.data.track
        north = self.parm.data.north #front center line formed from point and track
        east = self.parm.data.east
        middle = self.parm.data.middle #salinity at center of front
        spread = self.parm.data.spread
        rising = self.parm.data.rising #direction of gradient True = rising from right to left across center
        width = self.parm.data.width
        layer = self.parm.data.layer
        shift = self.parm.data.shift

        #generate distance of vehicle from center track
        d = navigating.DistancePointToTrack2D([east,north],track, [pe,pn])
        #shift center pos to right so shift d neg to left
        d -= (self.depth.value - layer) * shift
        d = max(- width/2.0, min( width/2.0, d)) #saturate

        if rising:  #sign of gradient rising from right to left
            s = 1.0
        else: #falling from right to left
            s = -1.0

        salinity = (s * d * 2.0/width) * spread/2.0 + middle

        self.output.update(salinity = salinity)

    def _expose(self):
        """
           prints out sensor state

        """
        print("Simulator %s stamp = %s  lapse = %0.3f" % (self.name, self.stamp,self.lapse))
        format = "salinity = %0.3f track = %0.3f north = %0.3f east = %0.3f"
        format += " middle = %0.3f spread = %0.3f, rising = %s, width = %0.3f"
        format += " layer = %0.3f shift = %0.3f"
        print(format %\
              (self.output.salinity, self.parm.data.track,
               self.parm.data.north, self.parm.data.east, self.parm.data.middle,
               self.parm.data.spread, self.parm.data.rising, self.parm.data.width,
               self.parm.data.layer, self.parm.data.shift))

class SimulatorSalinitySinusoid(SimulatorBase):
    """salinity sensor simulator class
    """
    Ioinits = odict(
        group = 'simulator.salinity.sinusoid',
        output = 'ctdsim',
        input = 'state.position', depth = 'state.depth',
        parms = dict(track = 0.0, north = 0.0, east = 0.0,
                     middle = 32.0, spread = 4.0, rising = True, width = 500.0,
                     layer = 20.0, shift = 2.0))


    def __init__(self, **kw):
        """Initialize instance.
        """
        #call super class method
        super(SimulatorSalinitySinusoid,self).__init__(**kw)

    def _prepio(self, group, output,input, parms = None, **kw):
        """ Override since legacy interface

                       group is path name of group in store, group has following subgroups or shares:
              group.parm = share for data structure of fixed parameters or coefficients
                 parm has the following fields:
                    track = heading of gradient center
                    north = north coord for gradient center
                    eath = east coord for gradient center
                    middle = salinity at center of front
                    spread = total variation in salinity = middle +- spread
                    rising = direction of gradient rising from right to left is True
                    width = distance over which spread occurs track line +- width
                    amp = amplitude of sinusoid

              group.elapsed = share copy of time lapse for logging

           output = share path name output ctd

           input = share path name input position of vehicle

           parms = dictionary to initialize group.parm fields

           instance attributes

           .group = copy of group name
           .parm = reference to input parameter share

           .output = ref to ctd salinity share
           .input = ref to vehicle position share

        """
        self.group = group

        self.elapsed = self.store.create(group + '.elapsed').create(value = 0.0)#create if not exist

        #outputs
        self.output = self.store.create(output).update(salinity = 0.0)

        #inputs
        self.input = self.store.create(input).create(north = 0.0, east = 0.0)

        #parms
        self.parm = self.store.create(group + '.parm')#create if not exist
        if not parms:
            parms = dict(track = 15, north = 0.0, east = 0.0, middle = 32.0,
                         spread  = 3.0, rising = True, width = 1000)

        self.parm.create(**parms)

    def restart(self):
        """Restart sensor  simulator

        """
        self.stamp = self.store.stamp
        self.lapse = 0.0

    def action(self, **kw):
        """Updates simulated sensor
        """
        super(SimulatorSalinitySinusoid,self).action(**kw) #lapse updated here

        #self.elapsed.updateJointly(value = self.lapse, stamp = stamp) #store lapse for logging
        self.elapsed.value = self.lapse

        #if self.lapse <= 0.0: #only evaluate simulator if lapse positive so rate calc good
        #   return

        pn = self.input.data.north  #vehicle position
        pe = self.input.data.east

        # center line (ray) of salinity front
        track = self.parm.data.track #direction = track
        north = self.parm.data.north #north coord of ref point base of ray
        east = self.parm.data.east #east coord of ref point base of ray

        middle = self.parm.data.middle #salinity at center of front
        spread = self.parm.data.spread #salinity range = middle +- spread
        #direction of gradient True = rising from right to left across center
        rising = self.parm.data.rising
        width = self.parm.data.width #spacial width of salinity front spread

        #generate signed distance of vehicle from center track (positive left)
        d = navigating.DistancePointToTrack2D([east,north],track, [pe,pn])

        d = max(- width/2.0, min( width/2.0, d)) #saturate

        if rising:  #sign of gradient rising from right to left
            s = 1.0
        else: #falling from right to left
            s = -1.0

        salinity = (s * d * 2.0/width) * spread + middle

        self.output.update(salinity = salinity)

    def _expose(self):
        """
           prints out sensor state

        """
        print("Simulator %s stamp = %s  lapse = %0.3f" % (self.name, self.stamp,self.lapse))
        format = "salinity = %0.3f track = %0.3f north = %0.3f east = %0.3f"
        format += " middle = %0.3f spread = %0.3f, rising = %s, width = %0.3f"
        print(format %\
              (self.output.salinity, self.parm.data.track,
               self.parm.data.north, self.parm.data.east, self.parm.data.middle,
               self.parm.data.spread, self.parm.data.rising, self.parm.data.width))

class SimulatorGradient(SimulatorBase):
    """gradient simulator class
    """
    Ioinits = odict(
        group = 'simulator.gradient.depth',
        output = 'ctdsim', field = 'depth',
        position = 'state.position', depth = 'state.depth',
        parms = dict(track = 0.0, north = 0.0, east = 0.0,
                     middle = 32.0, spread = 4.0, rising = True, width = 500.0,
                     layer = 20.0, shift = 2.0, span = 10.0, height = 20.0, duct = 0))

    def __init__(self, **kw):
        """Initialize instance.
        """
        #call super class method
        super(SimulatorGradient,self).__init__(**kw)

    def _prepio(self, group, output, field, position, depth, parms = None, **kw):
        """ Override since legacy interface

                       group is path name of group in store, group has following subgroups or shares:
              group.parm = share for data structure of fixed parameters or coefficients
                 parm has the following fields:
                    track = heading of gradient middle
                    north = north coord for gradient middle
                    east = east coord for gradient middle
                    middle = salinity at center of front
                    spread = total horizontal variation in output middle - spread/2 to middle + spread/2
                    rising = direction of gradient rising from right to left is True
                    width = horisontal distance over which spread = total variation occurs
                                spread occurs over trackline - width/2 to trackline + width/2
                    layer = depth where center of gradient is at middle value
                    shift = shift in center of gradient with depth
                    span = total vertical variation
                    height = vertical distance over which span occurs to saturation
                    duct = type of vertical variation
                          -1 = cold at bottom, 0 = cold mid at layer, 1 = cold surface
              group.elapsed = share copy of time lapse for logging

           output = share path name output ctd
           field = field name of simulated output measurable
              also outputs depth field since filter needs depth

           position = share path name input position of vehicle

           depth = share path name input depth of vehicle

           parms = dictionary to initialize group.parm fields

           instance attributes

           .group = copy of group name
           .parm = reference to input parameter share

           .output = ref to ctd salinity share
           .position = ref to vehicle position share
           .depth = ref to vehicle depth share
        """
        self.group = group

        self.elapsed = self.store.create(group + '.elapsed').create(value = 0.0)#create if not exist

        #outputs
        self.field = field
        self.output = self.store.create(output)
        self.output.update({self.field : 0.0})
        self.output.update(depth = 0.0)

        #inputs
        self.position = self.store.create(position)
        self.position.create(north = 0.0)
        self.position.create(east = 0.0)
        self.depth = self.store.create(depth).create(value = 0.0)

        #parms
        self.parm = self.store.create(group + '.parm')#create if not exist
        if not parms:
            parms = dict(track = 15, north = 0.0, east = 0.0, middle = 32.0,
                         spread  = 3.0, rising = True, width = 1000,
                         layer = 20.0, shift = 2.0, span = 10.0, height = 20.0, duct = 0 )

        self.parm.create(**parms)

    def restart(self):
        """Restart gradient  simulator

        """
        self.stamp = self.store.stamp
        self.lapse = 0.0

    def action(self, **kw):
        """Updates simulated sensor
        """
        super(SimulatorGradient,self).action(**kw) #lapse updated here

        #self.elapsed.updateJointly(value = self.lapse, stamp = stamp) #store lapse for logging
        self.elapsed.value = self.lapse

        #if self.lapse <= 0.0: #only evaluate simulator if lapse positive so rate calc good
        #   return

        pn = self.position.data.north  #vehicle position
        pe = self.position.data.east

        track = self.parm.data.track
        north = self.parm.data.north #front center line formed from point and track
        east = self.parm.data.east
        middle = self.parm.data.middle #salinity at center of front
        spread = self.parm.data.spread #horizontal variation of output
        rising = self.parm.data.rising #direction of gradient True = rising from right to left across center
        width = self.parm.data.width #horizontal distance over which spread occurs
        layer = self.parm.data.layer #depth of middle
        shift = self.parm.data.shift #horizontal shift of middle with depth
        span = self.parm.data.span #veritical variation of output
        height = self.parm.data.height #vertical distrance over which span occurs
        duct = self. parm.data.duct #Type of variation of output with depth in depth

        #horizontal distance of vehicle from center track
        dh = navigating.DistancePointToTrack2D([east,north],track, [pe,pn])
        #vertical distance from layer (pos below)
        dv = self.depth.value - layer

        #shift effective center of track as a function of depth
        dh -= dv * shift #shift center pos to right so shift d neg to left

        dh = max(- width/2.0, min( width/2.0, dh)) #saturate

        dv = max(- height/2.0, min( height/2.0, dv)) #saturate

        #compute temperature offset for duct type
        if duct == 0: #warmer as move away from later up and down
            dv = abs(dv)
        elif duct == -1: #colder down warmer up
            offset = -dv * span/float(height)
        elif duct == +1: #colder up warmer down
            offset = dv * span/float(height)
        else:
            offset = 0.0

        #sign of gradient rising = true then rising from right to left
        # else falling from right to left
        if not rising:
            dh = - dh

        out = middle + (dh * spread/float(width)) + (dv * span/float(height))

        self.output.update({self.field : out, 'depth' : self.depth.value})

    def _expose(self):
        """
           prints out gradient state

        """
        print("Simulator %s stamp = %s  lapse = %0.3f" % (self.name, self.stamp,self.lapse))
        format = "output = %0.3f track = %0.3f north = %0.3f east = %0.3f"
        format += " middle = %0.3f spread = %0.3f, rising = %s, width = %0.3f"
        format += " layer = %0.3f shift = %0.3f span = %0.3f height = %0.3f duct = %s"
        print(format %\
              (self.output[self.field], self.parm.data.track,
               self.parm.data.north, self.parm.data.east, self.parm.data.middle,
               self.parm.data.spread, self.parm.data.rising, self.parm.data.width,
               self.parm.data.layer, self.parm.data.shift, self.parm.data.span,
               self.parm.data.height, self.parm.data.duct))

SimulatorGradient.__register__('SimulatorGradientTemperature', ioinits=odict(
    group = 'simulator.gradient.temperature',
    output = 'ctdsim', field = 'temperature',
    position = 'state.position', depth = 'state.depth',
    parms = dict(track = 0.0, north = 0.0, east = 0.0,
                 middle = 32.0, spread = 4.0, rising = True, width = 500.0,
                 layer = 20.0, shift = 2.0, span = 10.0, height = 20.0, duct = 0)) )

SimulatorGradient.__register__('SimulatorGradientSalinity', ioinits=odict(
    group = 'simulator.gradient.salinity',
    output = 'ctdsim', field = 'salinity',
    position = 'state.position', depth = 'state.depth',
    parms = dict(track = 0.0, north = 0.0, east = 0.0,
                 middle = 32.0, spread = 4.0, rising = True, width = 500.0,
                 layer = 20.0, shift = 2.0, span = 10.0, height = 20.0, duct = 0)) )

