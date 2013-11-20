"""controlling.py controller deed module

"""
#print "module %s" % __name__

import math
import time
import struct
from collections import deque
import inspect


from ....base.odicting import odict
from ....base.globaling import *

from ....base import aiding

from ....base import storing 
from ....base import deeding

from ....base.consoling import getConsole
console = getConsole()

def CreateInstances(store):
    """Create action instances
       must be function so can recreate after clear registry
       globals useful for module self tests
    """

    PIDController(name = 'controllerPidSpeed', store = store).ioinit.update(
            group = 'controller.pid.speed', output = 'goal.rpm',
            input = 'state.speed', rate = 'state.speedRate', rsp = 'goal.speed',
            parms = dict(wrap = 0.0, drsp = 0.01, calcRate = True,
                         ger = 1.0, gff = 400.0, gpe = 0.0, gde = 0.0, gie = 0.0,
                         esmax = 0.0, esmin = 0.0, ovmax = 1500.0, ovmin = 0.0))

    PIDController(name = 'controllerPidHeading', store = store).ioinit.update(
            group = 'controller.pid.heading', output = 'goal.rudder', 
            input = 'state.heading', rate = 'state.headingRate', rsp = 'goal.heading',
            parms = dict(wrap = 180.0, drsp = 0.01, calcRate = True,
                         ger = 1.0, gff = 0.0, gpe = 3.0, gde = 0.0, gie = 0.0,
                         esmax = 0.0, esmin = 0.0, ovmax = 20.0, ovmin = -20.0))


    PIDController(name = 'controllerPidDepth', store = store).ioinit.update(
            group = 'controller.pid.depth', output = 'goal.pitch',
            input = 'state.depth', rate = 'state.depthRate', rsp = 'goal.depth',
            parms = dict(wrap = 0.0, drsp = 0.01, calcRate = True,
                         ger = 1.0, gff = 0.0, gpe = 8.0, gde = 0.0, gie = 1.0,
                         esmax = 5.0, esmin = -5.0, ovmax = 10.0, ovmin = -10.0))

    PIDController(name = 'controllerPidPitch', store = store).ioinit.update(
            group = 'controller.pid.pitch', output = 'goal.stern',
            input = 'state.pitch', rate = 'state.pitchRate', rsp = 'goal.pitch',
            parms = dict(wrap = 180.0, drsp = 0.01, calcRate = True,
                         ger = 1.0, gff = 0.0, gpe = 2.0, gde = 0.0, gie = 0.0,
                         esmax = 0.0, esmin = 0.0, ovmax = 20.0, ovmin = -20.0))

#Class definitions

class PIDController(deeding.LapseDeed):
    """PIDController LapseDeed Deed Class
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
        super(PIDController,self).__init__(**kw)  

        self.lapse = 0.0 #time lapse in seconds calculated on update
    
    def preinitio(self,  **kw):
        """ Parse-time re-initio
            This just prints warning for now since not yet supported by this class.
            
        """
        console.terse("     Warning: Parse time init not supported on this deed"
                      " '{0}'\n".format(self.name))
        return self    
        

    def initio(self, group, output, input, rate, rsp, parms = None, **kw):
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
        super(PIDController,self).action(**kw) #computes lapse here

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
        e = aiding.Wrap2(angle = (input - rsp), wrap = self.parm.data.wrap)
        self.e.value = e

        if self.parm.data.calcRate: #calculate error rate with time derivative
            er = (e - pe)/self.lapse
        else: #get error rate from rate sensor
            er= self.parm.data.ger * rate #convert measured rate sign and units
        self.er.value = er

        es = self.es.value
        ae =  self.lapse * (e + pe)/2.0 #use average error over time lapse
        #update errorSum filter only when small error and small error rate
        es += ae * aiding.Blend0(ae,0.0, 3.0) * aiding.Blend0(er,0.0, 0.1)
        es = min(self.parm.data.esmax,max(self.parm.data.esmin,es)) #hard limit so no windup
        self.es.value = es


        out =  self.parm.data.gff * rsp +\
            self.parm.data.gpe * e +\
            self.parm.data.gde * er +\
            self.parm.data.gie * es

        out = min(self.parm.data.ovmax,max(self.parm.data.ovmin,out))
        self.output.value = out

        return None

    def expose(self):
        """
           prints out controller state

        """
        print "Controller PID %s stamp = %s lapse = %0.3f input = %0.3f set point = %0.3f " %\
              (self.name, self.stamp, self.lapse, self.input.value, self.rsp.value)
        print "    error = %0.3f errorRate = %0.3f errorSum = %0.3f output = %0.3f truth = %s" %\
              (self.e.value, self.er.value, self.es.value, self.output.value, self.output.truth)



def TestPID():
    """

    """
    #clear registries
    storing.Store.Clear()
    deeding.Deed.Clear()

    store = storing.Store(name = 'Test')
    CreateInstances(store)


    print "\nTesting PID Controller"
    controller = PIDController(name = 'controllerPIDTest', store = store, 
                               group = 'controller.pid.test', output = 'goal.testoutput',
                               input = 'state.testinput', rate = 'state.testrate', rsp = 'goal.testrsp',
                               parms = dict(wrap = 0.0, drsp = 0.01, calcRate = True,
                                            ger = 1.0, gff = 0.0, gpe = 3.0, gde = 0.0, gie = 0.0,
                                            esmax = 0.0, esmin = 0.0, ovmax = 20.0, ovmin = -20.0))


    store.expose()

    input = store.fetch('state.testinput').update(value = 0.0)
    rate = store.fetch('state.testrate').update(value = 0.0)
    rsp = store.fetch('goal.testrsp').update(value = 45.0)
    controller.update()
    controller.expose()

    input.value = 22.5
    store.advanceStamp(0.125)
    controller.update()
    controller.expose()

    print "\nTesting Speed PID Controller"
    input = store.fetch('state.speed').update(value = 0.0)
    rate = store.fetch('state.speedRate').update(value = 0.0)
    rsp = store.fetch('goal.speed').update(value = 2.0)
    controllerPIDSpeed.expose()
    store.advanceStamp(0.125)
    controllerPIDSpeed.update()
    controllerPIDSpeed.expose()

    print "\nTesting Heading PID Controller"
    input = store.fetch('state.heading').update(value = 0.0)
    rate = store.fetch('state.headingRate').update(value = 0.0)
    rsp = store.fetch('goal.heading').update(value = 45.0)
    controllerPIDHeading.expose()
    store.advanceStamp(0.125)
    controllerPIDHeading.update()
    controllerPIDHeading.expose()

    print "\nTesting Depth PID Controller"
    input = store.fetch('state.depth').update(value = 0.0)
    rate = store.fetch('state.depthRate').update(value = 0.0)
    rsp = store.fetch('goal.depth').update(value = 5.0)
    controllerPIDDepth.expose()
    store.advanceStamp(0.125)
    controllerPIDDepth.update()
    controllerPIDDepth.expose()

    print "\nTesting Pitch PID Controller"
    input = store.fetch('state.pitch').update(value = 0.0)
    rate = store.fetch('state.pitchRate').update(value = 0.0)
    rsp = store.fetch('goal.pitch').update(value = 5.0)
    controllerPIDPitch.expose()
    store.advanceStamp(0.125)
    controllerPIDPitch.update()
    controllerPIDPitch.expose()



def TestMotion():
    """

    """
    
    #clear registries
    storing.Store.Clear()
    deeding.Deed.Clear()

    store = storing.Store(name = 'Test')
    #CreateInstances(store)


    print "\nTesting Motion Sim Controller"
    controller = MotionController(name = 'controllerMotionTest', store = store, 
                                  group = 'controller.motion.test',
                                  speed = 'state.speed', speedRate = 'state.speedRate',
                                  depth = 'state.depth', depthRate = 'state.depthRate',
                                  pitch = 'state.pitch', pitchRate = 'state.pitchRate', 
                                  altitude = 'state.altitude',
                                  heading = 'state.heading', headingRate = 'state.headingRate',
                                  position = 'state.position',
                                  rpm = 'goal.rpm', stern = 'goal.stern', rudder = 'goal.rudder',
                                  current = 'scenario.current', bottom = 'scenario.bottom', 
                                  prevPosition = 'state.position',
                                  parms = dict(rpmLimit = 1000.0, sternLimit = 20.0, rudderLimit = 20.0, 
                                               gs = 0.0025, gpr = -0.5, ghr = -0.5))

    store.expose()

    rpm = store.fetch('goal.rpm').update(value = 500.0)
    stern = store.fetch('goal.stern').update(value = 0.0)
    rudder = store.fetch('goal.rudder').update(value = 0.0)
    current = store.fetch('scenario.current').update(north = 0.0, east = 0.0)
    bottom = store.fetch('scenario.bottom').update(value =  50.0)
    prevPosition = store.fetch('scenario.startposition').update(north = 0.0, east = 0.0)

    controller.restart()
    controller.expose()
    store.advanceStamp(0.125)
    controller.update()
    controller.expose()



def Test():
    """Module Common self test

    """
    
    #clear registries
    print "\nTesting Controllers\n"
    storing.Store.Clear()
    deeding.Deed.Clear()

    store = storing.Store(name = 'Test')
    CreateInstances(store)
    store.expose()


    current = store.fetch('scenario.current').update(north = 0.0, east = 0.0)
    bottom = store.fetch('scenario.bottom').update(value =  50.0)
    prevPosition = store.fetch('state.position').update(north = 0.0, east = 0.0)

    headinggoal =  store.fetch('goal.heading').update(value = 45.0)
    depthgoal =  store.fetch('goal.depth').update(value = 5.0)
    speedgoal =  store.fetch('goal.speed').update(value = 2.0)
    duration = 10.0

    controllerMotionVehicle.restart()

    controllerPidSpeed.expose()
    controllerPidHeading.expose()
    controllerPidDepth.expose()
    controllerPidPitch.expose()
    controllerMotionVehicle.expose()

    while (store.stamp <= duration):
        print
        controllerPidSpeed.action()
        controllerPidHeading.action()
        controllerPidDepth.action()
        controllerPidPitch.action()
        controllerMotionVehicle.action()
        controllerMotionVehicle.expose()

        store.advanceStamp(0.125)



if __name__ == "__main__":
    Test()
