"""acting.py action module

"""
#print "module %s" % __name__

import time
import struct
from collections import deque
import inspect

from .globaling import *

from . import aiding
from . import excepting
from . import registering
from . import storing 
from . import framing

from .consoling import getConsole
console = getConsole()


def CreateInstances(store):
    """Create action instances
       must be function so can recreate after clear registry
    """
    #global restarter, deactivator, printer

    transiter = Transiter(name = 'transiter', store = store)
    suspender = Suspender(name = 'suspender', store = store)
    deactivator = Deactivator(name = 'deactivator', store = store)
    restarter = Restarter(name = 'restarter', store = store)
    printer = Printer(name = 'printer', store = store)

#Class definitions

class Act(object):
    """lightweight container class for action references and parameters

    """
    __slots__ = ('actor', 'parms')

    def __init__(self, actor=None, parms=None, **kw ):
        """Initialization method for instance.

           attributes
           .actor = Actor instance callable , call performs instances method action
           .parms = dictionary of keyword arguments for .act

        """
        super(Act,self).__init__(**kw)

        self.actor = actor #callable instance performs action
        self.parms = parms or {}

    def __call__(self): #make Act instance callable as function
        """Define act as callable object

        """
        return (self.actor(**self.parms))


    def expose(self):
        """Show Actor and parms"""
        console.terse("Act Actor {0} Parms {1}\n".format(self.actor, self.parms))
        if self.actor:
            self.actor.expose()

    def resolveLinks(self, *pa, **kwa):
        """Resolve any links in associated parms for actors
           Should be overridden if use arguments
        """
        parms = self.actor.resolveLinks(**self.parms)
        for key, value in parms.items():
            self.parms[key] = value

class Nact(Act):
    """lightweight container class for action references and parameters
       Negating Act used for actor needs to give Not Need
    """
    __slots__ = ('actor', 'parms')

    def __init__(self, **kw ):
        """Initialization method for instance.

           Inherited attributes
              .actor = Actor instance callable , call performs instances method action
              .parms = dictionary of keyword arguments for .act

        """
        super(Nact,self).__init__(**kw)


    def __call__(self): #make Act instance callable as function
        """Define act as callable object
           Negate the output
        """
        return not (self.actor(**self.parms))


    def expose(self):
        """Show Actor and Parms"""
        console.terse("Nact Actor {0} Parms {1}\n".format(self.actor, self.parms))
        if self.actor:
            self.actor.expose()


class Actor(registering.StoriedRegistry):
    """Actor Patron Registry Class 
       for executing actions
       via its action method 
    """
    Counter = 0  
    Names = {}

    def __init__(self, name = 'actor', **kw ):
        """Initialization method for instance.

           inherited attributes
              .name = unique name for actor instance
              .store = shared data store

        """
        if 'preface' not in kw:
            kw['preface'] = 'Actor'

        super(Actor,self).__init__(name = name, **kw)
    
    def __call__(self, **kw):
        """run .action

        """
        return self.action(**kw)
    
    def action(self, **kw):
        """Action called by Actor. Should override in subclass."""
        console.profuse("Actioning {0} with {1}\n".format(self.name, str(kw)))

        pass
    
    def expose(self):
        """Show Actor."""
        console.terse("Actor {0}".format(self.name))
    
    def resolveLinks(self, **kw):
        """Resolves any links in parms for Actor
           should be overridden by sub class
        """
        return {} #empty parms


class Interrupter(Actor):
    """Interrupter Actor Patron Registry Class 
       Interrupter is a base clase for all actor classes that interrupt normal precur
       processing and result in a change in the frame or the frame processing.

       This class must be subclassed. This is a convenience so can either use
         isinstance to test or has_attr interruptive

       Specifically and Interrupter's action() method returns truthy when its action
       will interrupt the normal frame processing examples are
       Transitors which interrupt by changing to a new frame
       Suspenders which interrupt when the conditional aux condition is true and
          further processing of the frame and sub frames is stopped


    """
    __slots__ = ('_interruptive')
    
    def __init__(self,**kw ):
        """Initialization method for instance. """

        if 'preface' not in kw:
            kw['preface'] = 'Interrupter'

        super(Interrupter,self).__init__(**kw)

        self._interruptive = None

class Transiter(Interrupter):
    """Transiter Interrupter Actor Patron Registry Class 
       Transiter  is a special actor that performs transitions between frames

       Parameters
            needs = list of Act objects that are exit needs for this trans
            near = source frame of trans
            far = target frame of trans
            human = text version of transition

    """

    def __init__(self,**kw ):
        """Initialization method for instance. """

        if 'preface' not in kw:
            kw['preface'] = 'Transiter'

        super(Transiter,self).__init__(**kw)

    def action(self, needs, near, far, human, **kw):
        """Action called by Actor  """

        framer = near.framer #to speed up

        console.profuse("Attempt segue from {0} to {1}\n".format(near.name, far.name))

        for act in needs: 
            if not act(): #return None if not all true
                return None

        console.profuse("     active outline: {0}\n".format([frame.name for frame in framer.actives]))
        console.profuse("     far outline: {0}\n".format([frame.name for frame in far.outline]))   

        #find uncommon entry and exit lists associated with transition
        #exits, enters = framing.Framer.Uncommon(framer.actives,far.outline)
        #find uncommon and common entry and exit lists associated with transition
        exits, enters, reexens = framing.Framer.ExEn(framer.actives,far)

        #check enters, if successful, perform transition
        if not framer.checkEnter(enters): 
            return None

        msg = "To: {0}<{1} at {2} Via: {3} ({4}) From: {5} after {6:0.3f}\n".format(
            framer.name, far.human, framer.store.stamp, near.name, human, 
            framer.human, framer.elapsed)
        console.terse(msg)

        console.profuse("     exits: {0}\n".format([frame.name for frame in exits]))
        console.profuse("     enters: {0}\n".format([frame.name for frame in enters]))
        console.profuse("     reexens: {0}\n".format([frame.name for frame in reexens]))

        framer.exit(exits) #exit uncommon frames in near outline reversed in place
        framer.rexit(reexens[:]) #make copy since reversed in place
        framer.renter(reexens) 
        framer.enter(enters)
        framer.activate(active = far)
        return far


    def expose(self):
        """      """
        console.terse("Transiter {0}\n".format(self.name))

    def resolveLinks(self, needs, near, far, human, **kw):
        """Resolve any links in far and in associated parms for actors"""

        parms = {}

        if not isinstance(far, framing.Frame):
            if far == 'next':
                if not isinstance(near.next, framing.Frame):
                    raise excepting.ResolveError("ResolveError: Bad next frame",
                                                 near.name, near.next)
                far = near.next

            elif far == 'me':
                far = near

            elif far in framing.Frame.Names:
                far = framing.Frame.Names[far]

            else:
                raise excepting.ResolveError("ResolveError: Bad far link",
                                             near.name + " " + human, far)

        parms['far'] = far #replace name with valid link

        for act in needs:
            act.resolveLinks()

        return parms


class Suspender(Interrupter):
    """Suspender Interrupter Actor Patron Registry Class 
       Suspender  is a special actor that performs a conditional auxiliary
          which truncates the active outline effectively suspended the truncated
          frames

       Instance Attributes
          ._activative = flag to indicate that the Suspender has been _activative

       Parameters
            needs = list of Act objects that are exit needs for this trans
            main = source frame of trans
            aux = target frame of trans
            human = text version of transition

    """
    __slots__ = ('_activative',)
    
    def __init__(self,**kw ):
        """Initialization method for instance. """

        if 'preface' not in kw:
            kw['preface'] = 'Suspender'

        super(Suspender,self).__init__(**kw)
        self._activative = None

    def action(self, needs, main, aux, human, **kw):
        """Action called by Actor  """

        framer = main.framer #to speed up

        if aux.done: #not active

            console.profuse("Attempt segue from {0} to aux {1}\n".format(main.name, aux.name))

            for act in needs: 
                if not act(): #return None if not all true
                    return None

            if aux.main: #see if aux still belongs to another frame
                return None

            if not aux.checkStart(): #performs entry checks
                return None

            msg = "To: {0} in {1}<{2} at {3} Via: {4} ({5}) From: {6} after {7:0.3f}\n".format(
                aux.name, framer.name, main.headHuman, framer.store.stamp, main.name, 
                human, framer.human, framer.elapsed)
            console.terse(msg)

            #self._activative = True
            aux.main = main  #assign aux's main to this frame
            aux.enterAll() #starts at aux.first frame
            aux.recur()

            if aux.done: #if done after first iteration then clean up
                self.deactivate(aux)
                return None

            #truncate active outline to suspend lower frames
            framer.change(main.head, main.headHuman)
            return aux

        if not aux.done: #not done so active
            aux.segue()
            aux.recur()

            if aux.done: #if done after this iteraion clean up
                self.deactivate(aux)
                framer.reactivate()
                return None

            return aux


    def expose(self):
        """      """
        console.terse("Suspender {0}\n".format(self.name))

    def deactivate(self, aux):
        """Called by deactivator actor to cleanly exit      """
        console.profuse("Deactivating {0}\n".format(aux.name))

        aux.exitAll() # also sets .done = True
        aux.main = None

    def resolveLinks(self, needs, main, aux, human, **kw):
        """Resolve any links aux and in associated parms for actors"""

        parms = {}

        if not isinstance(aux, framing.Framer):
            if aux in framing.Framer.Names:
                aux = framing.Framer.Names[aux]

            else:
                raise excepting.ResolveError("ResolveError: Bad far link",
                                             near.name + " " + human, far)

        parms['aux'] = aux #replace name with valid link

        console.terse("    Resolved aux as {0}".format(aux.name))

        if aux.schedule != AUX:
            raise excepting.ResolveError("ResolveError: Bad aux link not scheduled as AUX",
                                         main.name + " " + human, aux)

        for act in needs:
            act.resolveLinks()

        return parms


class Deactivator(Actor):
    """Deactivator Actor Patron Registry Class 

       Deactivator is a special actor that acts on an Act

       In the Deactivator's action method, 
          IF the act passed in as a parameter has a activate attribute THEN
                       it calls the deactivate method
       This is to ensure the outline in cond aux is exited cleanly when the aux
          is preempted by higher level transition.

       Builder adds a deactivator for each Suspender preact
    """

    def __init__(self,  **kw):
        """Initialization method for instance.

           inherited instance attributes:
           .name
           .store
        """
        if 'preface' not in kw:
            kw['preface'] = 'Deactivator'

        super(Deactivator,self).__init__(**kw)  


    def action(self, actor, aux, **kw):
        """Action called by Actor
        """
        #console.profuse("{0} action {1} for {2}\n".format(self.name, actor.name, aux.name))

        if hasattr(actor, '_activative') and not  aux.done:
            console.profuse("{0} deactivate {1} for {2}\n".format(self.name, actor.name, aux.name))
            return actor.deactivate(aux)

    def expose(self):
        """   """
        console.terse("Deactivator {0}\n".format(self.name))

    def resolveLinks(self, actor, aux, **kw):
        """Resolve any links aux and in associated parms for actors"""

        parms = {}

        if not isinstance(aux, framing.Framer):
            if aux in framing.Framer.Names:
                aux = framing.Framer.Names[aux]

            else:
                raise excepting.ResolveError("ResolveError: Bad far link",
                                             near.name + " " + human, far)

        parms['aux'] = aux #replace name with valid link

        console.terse("    Resolved aux as {0}".format(aux.name))

        if aux.schedule != AUX:
            msg = "ResolveError: Bad deactivator aux link not scheduled as AUX"
            raise excepting.ResolveError(msg, actor.name, aux)

        return parms

class Restarter(Actor):
    """RestarterActor Patron Registry Class 

       Restarter is a special actor that acts on other actor
       In the Restarter's action method, 
       if the actor passed in as a parameter has a restart attribute
          it calls the restart method

       Builder checks at parse time
       If deed instance has restart attribute then
          adds enter restarter action for the deed
    """

    def __init__(self,  **kw):
        """Initialization method for instance.

           inherited instance attributes:
           .name
           .store
        """
        if 'preface' not in kw:
            kw['preface'] = 'Restarter'

        super(Restarter,self).__init__(**kw)  


    def action(self, actor, **kw):
        """Action called by Actor
        """
        console.profuse("{0} restart {1}\n".format(self.name, actor.name))

        if hasattr(actor, 'restart'):
            return actor.restart()

    def expose(self):
        """   """
        console.terse("Restarter {0}\n".format(self.name))



class Printer(Actor):
    """Printor Actor Patron Registry Class 

       Printer is a special actor that just prints to console its message 

    """

    def __init__(self,  **kw):
        """Initialization method for instance.

           inherited instance attributes:
           .name
           .store
        """
        if 'preface' not in kw:
            kw['preface'] = 'Printer'

        super(Printer,self).__init__(**kw)  


    def action(self, message, **kw):
        """Action called by Actor
        """
        #console.terse("{0} printer {1}\n".format(self.name, message))
        console.terse("*** {0} ***\n".format(message))

    def expose(self):
        """   """
        console.terse("Printer {0}\n".format(self.name))


def Test():
    """Module Common self test

    """

    import framing

    store = storing.Store()

    actor = Actor(store = store)
    actor()

    depthNeed = DepthNeed(name = 'checkDepth', store = store)
    depthNeed(depth = 1.0)

    depthGoal = DepthGoal(name = 'setDepth', store = store)
    depthGoal(depth = 2.0)

    depthDeed = DepthDeed(name = 'doDepth', store = store)
    depthDeed(depth = 3.0)

    depthTrait = DepthTrait(name = 'useDepth', store = store)
    depthTrait(depth = 4.0)

    depthSpec = DepthSpec(name = 'optDepth', store = store)
    depthSpec(depth = 5.0)

    fr = framing.Framer(store = store)
    f = framing.Frame(store = store)
    fr.startFrame = f

    startFiat = StartFiat(name = 'tellStart', store = store)
    startFiat(framer = fr)

    startWant = StartWant(name = 'askStart', store = store)
    startWant(framer = fr)

    poke = Poke(name = 'put', store = store)
    poke(name = 'autopilot.depth', value = dict(depth = 5))



if __name__ == "__main__":
    test()
