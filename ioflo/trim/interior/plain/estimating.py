"""estimating.py estimator deed module


"""
#print("module {0}".format(__name__))

import math
import time
import struct
from collections import deque
import inspect


from ....aid.sixing import *
from ....aid.odicting import odict
from ....base.globaling import *

from ....aid import aiding, navigating, blending
from ....aid.navigating import DEGTORAD, RADTODEG
from ....base import doing

from ....aid.consoling import getConsole
console = getConsole()

class EstimatorPositionNfl(doing.DoerLapse):
    """Estimator Position NonlinearFusion class
    """
    Ioinits = odict(
        group = 'estimator.position.nlf',
        position = 'nlf.position',
        drPosition = 'dr.position', drBias = 'dr.bias',
        speed = 'state.speed', heading = 'heading.output',
        current = 'dvl.current',
        dvlVelocity = 'dvl.velocity',
        gpsPosition = 'gps.position', gpsVelocity = 'gps.velocity',
        parms = dict(upsilon = 5.0, scale = 2.0, gain = 0.01,
                     dvlStamp = 0.0, stale = 1.0,
                     gpsPosStamp = 0.0, gpsVelStamp = 0.0))

    def __init__(self, **kw):
        """Initialize instance.

           inherited instance attributes
           .stamp = time stamp
           .lapse = time lapse between updates of controller
           .name
           .store

        """
        #call super class method
        super(EstimatorPositionNfl,self).__init__(**kw)

    def _initio(self, ioinits):
        """
        Initialize Actor data store interface from ioinits odict

        Wrapper for backwards compatibility to new _initio signature
        """
        self._prepio(**ioinits)
        return odict()

    def _prepio(self, group, position, drPosition, drBias,
                 speed, heading, current, dvlVelocity, gpsPosition, gpsVelocity,
                 parms = None, **kw):
        """ Override since uses legacy interface
            group is path name of group in store, group has following subgroups or shares:
              group.parm = share for data structure of fixed parameters or coefficients
                 parm has the following fields:
                    upsilon = fusion parameter related to uncertainty
                    scale = fusion scale factor
                    gain = bias filter gain
                    dvlStamp = time stamp last dvl update
                    stale = time delay for stale pos estimate
                    gpsPosStamp = time stamp last gps position update
                    gpsVelStamp = time stamp last gps velocity update

              group.elapsed = share copy of time lapse for logging

           position = share path name output fused position north east m
           drPosition = share path name output dead reckoned position
           drBias = share path name output dead reckoned forward starboard bias (drift rate m/s)

           speed = share path name input speed m/s
           heading = share path name input heading deg north =0 positive clock wise
           current = share path name input current vector (north, east) m wrt origin on plane
           dvlVelocity = share path name input dvl velocity forward starboard
           gpsPosition = share path name input gps position north sourth
           gpsVelocity = share path name input gps velocity

           parms = dictionary to initialize group.parm fields

           instance attributes

           .group = copy of group name
           .parm = reference to input parameter share

           .position = ref to output position share
           .drPosition = ref to output dr position share
           .drBias = ref to output dr bias share

           .speed = ref to speed share
           .heading = ref to heading share
           .current = ref to input current north east share
           .dvlVelocity = ref to input dvl velocity
           .gpsPosition = ref to input gps position
           .gpsVelocity = ref to input gps velocity


        """
        self.group = group

        self.parm = self.store.create(group + '.parm')#create if not exist
        if not parms:
            parms = dict(upsilon = 5.0, scale = 2.0, gain = 0.01,
                         dvlStamp = 0.0, stale = 1.0,
                         gpsPosStamp = 0.0, gpsVelStamp = 0.0)

        self.parm.create(**parms)
        self.parm.data.upsilon = abs(self.parm.data.upsilon)
        self.parm.data.scale = abs(self.parm.data.scale)
        self.parm.data.gain = abs(self.parm.data.gain)
        self.parm.data.stale = abs(self.parm.data.stale)

        self.elapsed = self.store.create(group + '.elapsed').create(value = 0.0)#create if not exist

        #outputs create share if not exist but force update of value

        self.position = self.store.create(position)
        self.position.create(north = 0.0).update(north = 0.0) #preserves order
        self.position.create(east = 0.0).update(east = 0.0)

        self.drPosition = self.store.create(drPosition)
        self.drPosition.update(north = 0.0) #preserves order
        self.drPosition.update(east = 0.0)

        self.drBias = self.store.create(drBias)
        self.drBias.update(forward = 0.0) #preserves order
        self.drBias.update(starboard = 0.0)

        #inputs create share if not exists and create value if not exist
        self.speed = self.store.create(speed).create(value = 0.0)
        self.heading = self.store.create(heading).create(value = 0.0)
        self.current = self.store.create(current)
        self.current.create(north = 0.0)#preserves order
        self.current.create(east = 0.0)

        self.dvlVelocity = self.store.create(dvlVelocity)
        self.dvlVelocity.create(forward = 0.0)#preserves order
        self.dvlVelocity.create(starboard = 0.0)

        self.gpsPosition = self.store.create(gpsPosition)
        self.gpsPosition.create(north = 0.0)#preserves order
        self.gpsPosition.create(east = 0.0)

        self.gpsVelocity = self.store.create(gpsVelocity)
        self.gpsVelocity.create(north = 0.0)#preserves order
        self.gpsVelocity.create(east = 0.0)

    def restart(self):
        """Restart

        """
        self.stamp = self.store.stamp
        self.lapse = 0.0

        self.parm.data.dvlStamp = self.dvlVelocity.stamp
        self.parm.data.gpsPosStamp = self.gpsPosition.stamp
        self.parm.data.gpsVelStamp = self.gpsVelocity.stamp

    def action(self, **kw):
        """Updates estimater
        """
        super(EstimatorPositionNfl,self).action(**kw) #.lapse & .stamp updated here
        #.lapse is time since last run
        #.stamp is current time

        self.elapsed.value = self.lapse #store lapse for logging

        #check here because rate calc divide by lapse
        #only finish update if lapse positive
        if self.lapse <= 0.0: #lapse non positive so return
            return

        #Two DR estimates: one uses DVL, other uses HSC (heading water speed current)
        #we need a DR estimate any time we get a GPS to make correction.
        #If we don't get new DVL data at same time that we get new gps then must use HSC
        #Also we don't want to go too long between DR estimates even if we
        #Don't get any DVL or GPS so we use HSC if last time since either new DVL
        #or new GPS is too long (stale)

        #generate events: newDVL, newGPS, newHSC
        staleNLF = False
        newDVL = False
        newGPS = False
        newHSC = False

        if (self.dvlVelocity.stamp > self.parm.data.dvlStamp):
            newDVL = True  #new dvl data since last time we used it

        if (self.gpsPosition.stamp > self.parm.data.gpsPosStamp):
            newGPS = True #new gps fix since last time we used it

        dvlAge = self.stamp - self.parm.data.dvlStamp
        gpsAge = self.stamp - self.parm.data.gpsPosStamp

        if (min(dvlAge, gpsAge) >= self.parm.data.stale):
            staleNLF = True #dvl and gps data are stale

        if not newDVL and (newGPS or staleNLF):
            newHSC = True #need to compute hsc

        if not (newDVL or newGPS or newHSC): #nothing to do so return
            return

        #compute DR displacement
        heading = self.heading.value #need for position change
        #get time lapse since last nlf position update
        nlfLapse = self.stamp - self.position.stamp

        if newDVL:
            #use nlfLapse here because we may update position even when no dvl update
            dvlForward = self.dvlVelocity.data.forward * nlfLapse #make distance
            dvlStarboard = self.dvlVelocity.data.starboard * nlfLapse #make distance
            nDisp, eDisp = navigating.RotateFSToNE(heading, dvlForward, dvlStarboard)

            self.parm.data.dvlStamp = self.stamp #update dvl last used Stamp

        else: #newHSC  we wouldn't be here unless we needed to update
            #use nlfLapse here because we may update position even when no hsc update
            speed = self.speed.value
            cn = self.current.data.north
            ce = self.current.data.east

            nDisp = (speed * math.cos(DEGTORAD * heading) + cn) * nlfLapse
            eDisp = (speed * math.sin(DEGTORAD * heading) + ce) * nlfLapse

        #compute positions (nlf and pure dr)
        #get last nlf position
        north = self.position.data.north
        east = self.position.data.east
        #compute dr based nlf position with dr displacement
        north += nDisp
        east += eDisp

        #get last pure deadreckoned position
        drNorth = self.drPosition.data.north
        drEast = self.drPosition.data.east
        #Update pure deadreckoned estimate
        drNorth += nDisp
        drEast += eDisp
        self.drPosition.update(north = drNorth, east = drEast)

        #best nlf estimate so far is (north, east)
        if newGPS: #new gps fix so make correction to (north, east)
            gpsNorth = self.gpsPosition.data.north
            gpsEast = self.gpsPosition.data.east

            nError = gpsNorth - north
            eError = gpsEast - east

            upsilon = self.parm.data.upsilon
            scale = self.parm.data.scale

            nDelta = nError * blending.blend1(nError, upsilon, scale)
            eDelta = eError * blending.blend1(eError, upsilon, scale)

            north += nDelta #make correction to dr disp
            east += eDelta #make correction to dr disp

            #update bias estimate
            #get old bias
            fBias = self.drBias.data.forward
            sBias = self.drBias.data.starboard

            gpsLapse = self.stamp - self.parm.data.gpsPosStamp

            fDelta, sDelta = navigating.RotateNEToFS(heading, nDelta, eDelta)
            gain = self.parm.data.gain

            fBias = (1.0 - gain) * fBias + gain * fDelta/gpsLapse
            sBias = (1.0 - gain) * sBias + gain * sDelta/gpsLapse
            self.drBias.update(forward = fBias, starboard = sBias)

            self.parm.data.gpsPosStamp = self.stamp #update gps used last stamp

        #update nlf position using best estimate (north, east)
        self.position.update(north = north, east = east)


    def _expose(self):
        """
           prints out sensor state

        """
        print("Estimator %s stamp = %s  lapse = %0.3f" % (self.name, self.stamp,self.lapse))
        format = "north = %0.3f east = %0.3f"
        print(format %\
              (self.position.data.north, self.position.data.east))
