"""controlling.py controller deed module

"""
#print("module {0}".format(__name__))

import math
import time
import struct
from collections import deque
import inspect

from ....aid.sixing import *
from ....aid.odicting import odict

from ....aid import aiding, navigating, blending

from ....base import storing
from ....base import doing

from ....aid.consoling import getConsole
console = getConsole()

class ControllerBase(doing.DoerLapse):
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


#Class definitions
class ControllerPid(ControllerBase):
    """PIDController DeedLapse Deed Class
       PID Controller Class

    """

    def __init__(self, **kw):
        """Initialize instance


           inherited instance attributes
           .stamp = time stamp
           .lapse = time lapse between updates of controller
           .name
           .store

        """
        #call super class method
        super(ControllerPid,self).__init__(**kw)

        self.lapse = 0.0 #time lapse in seconds calculated on update

    def _prepio(self, group, output, input, rate, rsp, parms = None, **kw):
        """ Override default since legacy deed interface

            group is path name of group in store, group has following subgroups or shares:
              group.parm = share for data structure of fixed parameters or coefficients
                 parm has the following fields:
                    wrap = where setpoint wraps around must be positive
                    drsp = delta rsp needed to indicate change in rsp avoids rounding error
                    calcRate = True rate is time difference, False rate is rate sensor input
                    ger = error rate to rate conversion gain
                    gff = feedforward reference to controller gain
                    gpe = proportional error gain
                    gde = derivative error gain
                    gie = integral error gain
                    esmax = maximum error sum
                    esmin = minimum error sum
                    ovmax = maximum controller output value
                    ovmin = minimum controller output value

              group.elapsed = share copy of lapse for logging
              group.prsp = share of prior reference set point needed to compute if changed
              group.e = share of error between rsp and input value appropriately scaled
              group.er = share of rate of change of error
              group.es = share of summation of error

           output is path name of share for output/truth of arbiter

           input = path name of input controlled variable
           rate = path name to input sensed rate of change of controlled variable
           rsp = path name of reference set point for controlled variable
           parms is optional dictionary of initial values for group.parm fields

           instance attributes

           .output = reference to output share
           .group = copy of group name
           .parm = reference to input parameter share
           .elapsed = referenceto lapse share
           .prsp = reference to prior ref set point share
           .e = reference to error share
           .er = reference to error rate share
           .es = reference to error sum share

           .input = reference to input share
           .rate = reference to input rate share
           .rsp = reference to input reference set point

        """

        self.group = group
        self.parm = self.store.create(group + '.parm')#create if not exist
        if not parms:
            parms = dict(wrap = 0.0, drsp = 0.01, calcRate = True,
                         ger = 1.0, gff = 0.0, gpe = 0.0, gde = 0.0, gie = 0.0,
                         esmax = 0.0, esmin = 0.0, ovmax = 0.0, ovmin = 0.0)
        self.parm.create(**parms)

        self.elapsed = self.store.create(group + '.elapsed').create(value = 0.0)#create if not exist
        self.prsp = self.store.create(group + '.prsp').create(value = 0.0)#create if not exist
        self.e = self.store.create(group + '.error').create(value = 0.0)#create if not exist
        self.er = self.store.create(group + '.errorRate').create(value = 0.0)#create if not exist
        self.es = self.store.create(group + '.errorSum').create(value = 0.0)#create if not exist

        self.output = self.store.create(output).update(value = 0.0) #force update not just create

        self.input = self.store.create(input).create(value = 0.0) #create if not exist
        self.rate = self.store.create(rate).create(value = 0.0)
        self.rsp = self.store.create(rsp).create(value = 0.0)


    def restart(self):
        """Restart controller   """
        self.es.value = 0.0 #reset integrator error sum to zero


    def action(self, **kw):
        """update will use inputs from store
           assumes all inputs come from deeds that use value as their output attribute name
        """
        super(ControllerPid,self).action(**kw) #computes lapse here

        self.elapsed.value = self.lapse  #update share

        if self.lapse <= 0.0: #only evaluate controller if lapse positive so rate calc good
            return

        input = self.input.value #get from store
        rate = self.rate.value #get from store
        rsp = self.rsp.value #get from store
        prsp = self.prsp.value #get from store

        if abs(rsp - prsp) > self.parm.data.drsp: #rsp changed
            self.prsp.value = rsp
            self.es.value = 0.0 #reset integrator
        else: #to minimize noise use prsp in case changed a little
            rsp = prsp

        pe = self.e.value #prior error
        # update error, unwrap error if setpoint wraps
        #error = input - self.rsp but may wrap so wan't shortest error if wraps
        e = navigating.wrap2(angle = (input - rsp), wrap = self.parm.data.wrap)
        self.e.value = e

        if self.parm.data.calcRate: #calculate error rate with time derivative
            er = (e - pe)/self.lapse
        else: #get error rate from rate sensor
            er= self.parm.data.ger * rate #convert measured rate sign and units
        self.er.value = er

        es = self.es.value
        ae =  self.lapse * (e + pe)/2.0 #use average error over time lapse
        #update errorSum filter only when small error and small error rate
        es += ae * blending.blend0(ae,0.0, 3.0) * blending.blend0(er,0.0, 0.1)
        es = min(self.parm.data.esmax,max(self.parm.data.esmin,es)) #hard limit so no windup
        self.es.value = es


        out =  self.parm.data.gff * rsp +\
            self.parm.data.gpe * e +\
            self.parm.data.gde * er +\
            self.parm.data.gie * es

        out = min(self.parm.data.ovmax,max(self.parm.data.ovmin,out))
        self.output.value = out

        return None

    def _expose(self):
        """
           prints out controller state

        """
        print("Controller PID %s stamp = %s lapse = %0.3f input = %0.3f set point = %0.3f " %\
              (self.name, self.stamp, self.lapse, self.input.value, self.rsp.value))
        print("    error = %0.3f errorRate = %0.3f errorSum = %0.3f output = %0.3f truth = %s" %\
              (self.e.value, self.er.value, self.es.value, self.output.value, self.output.truth))

ControllerPid.__register__('ControllerPidSpeed', ioinits=odict(
    group = 'controller.pid.speed', output = 'goal.rpm',
    input = 'state.speed', rate = 'state.speedRate', rsp = 'goal.speed',
    parms = dict(wrap = 0.0, drsp = 0.01, calcRate = True,
                 ger = 1.0, gff = 400.0, gpe = 0.0, gde = 0.0, gie = 0.0,
                 esmax = 0.0, esmin = 0.0, ovmax = 1500.0, ovmin = 0.0)) )

ControllerPid.__register__('ControllerPidHeading', ioinits=odict(
    group = 'controller.pid.heading', output = 'goal.rudder',
    input = 'state.heading', rate = 'state.headingRate', rsp = 'goal.heading',
    parms = dict(wrap = 180.0, drsp = 0.01, calcRate = True,
                 ger = 1.0, gff = 0.0, gpe = 3.0, gde = 0.0, gie = 0.0,
                 esmax = 0.0, esmin = 0.0, ovmax = 20.0, ovmin = -20.0)) )

ControllerPid.__register__('ControllerPidDepth', ioinits=odict(
    group = 'controller.pid.depth', output = 'goal.pitch',
    input = 'state.depth', rate = 'state.depthRate', rsp = 'goal.depth',
    parms = dict(wrap = 0.0, drsp = 0.01, calcRate = True,
                 ger = 1.0, gff = 0.0, gpe = 8.0, gde = 0.0, gie = 1.0,
                 esmax = 5.0, esmin = -5.0, ovmax = 10.0, ovmin = -10.0)) )

ControllerPid.__register__('ControllerPidPitch', ioinits=odict(
    group = 'controller.pid.pitch', output = 'goal.stern',
    input = 'state.pitch', rate = 'state.pitchRate', rsp = 'goal.pitch',
    parms = dict(wrap = 180.0, drsp = 0.01, calcRate = True,
                 ger = 1.0, gff = 0.0, gpe = 2.0, gde = 0.0, gie = 0.0,
                 esmax = 0.0, esmin = 0.0, ovmax = 20.0, ovmin = -20.0)) )

