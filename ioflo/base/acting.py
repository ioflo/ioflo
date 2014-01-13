"""acting.py action module

"""
#print "module %s" % __name__

import time
import struct
from collections import deque
import inspect
import copy

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
    transiter = Transiter(name = 'transiter', store = store)
    suspender = Suspender(name = 'suspender', store = store)
    deactivator = Deactivator(name = 'deactivator', store = store)
    restarter = Restarter(name = 'restarter', store = store)
    printer = Printer(name = 'printer', store = store)
    markerUpdate = UpdateMarker(name = 'markerUpdate', store = store)
    markerChange = ChangeMarker(name = 'markerChange', store = store)

#Class definitions

class Act(object):
    """lightweight container class for action references and parameters

    """
    __slots__ = ('actor', 'parms', 'frame', 'context', 'act', 'iois')

    def __init__(self, actor=None, parms=None, frame=None, context=None,
                     act=None, iois=None, **kwa ):
        """ Initialization method for instance.

            attributes
                .actor = Actor instance callable , call performs instances method action
                .parms = dictionary of keyword arguments for .act
                .frame = Frame reference to frame holding act
                .context = Action execution context name string set when added to frame
                .act = Act reference if act in embedded in another act such as Need
                .iois = dictionary of share initializers of parms with same key

        """
        super(Act,self).__init__()

        self.actor = actor #callable instance performs action
        self.parms = parms or {}
        self.frame = frame
        self.context = context
        self.act = act
        self.iois = iois
        
        self.parms['_act'] = self

    def __call__(self): #make Act instance callable as function
        """ Define act as callable object """
        return (self.actor(**self.parms))

    def expose(self):
        """ Show attributes"""
        cconsole.terse("Act Actor {0} Parms {1} in Frame {2} Context {3} SuperAct {4}\n".format(
                    self.actor, self.parms, self.frame, self.context, self.act))
        if self.actor:
            self.actor.expose()
            
    def clone(self, clones):
        """ Return clone of self in support of framer cloning
            clones is dict whose items keys are original framer names
            and values are duples of (original,clone) framer references
        """
        clone = Act(actor=self.actor.clone(), parms=copy.copy(self.parms))
        clone.cloneParms(clones)
        return clone
    
    def cloneParms(self, clones):
        """ Fixup parms in actor for framer cloning.
            clones is dict whose items keys are original framer names
            and values are are duples of (original,clone) framer references
            
        """
        parms = self.actor.cloneParms(parms=self.parms, clones=clones)
        self.parms.update(parms)

    def resolveLinks(self, *pa, **kwa):
        """ Resolve .frame attribute and any links in associated parms for .actor"""
        if self.act: # sub act such as need of another act .act
            self.frame = self.act.frame
            self.context = self.act.context
        self.frame = framing.resolveFrame(self.frame, who=self)
        
        parms = self.actor.resolveLinks(**self.parms)
        self.parms.update(parms) 

class Nact(Act):
    """ Negating Act used for actor needs to give Not Need
    """
    __slots__ = ('actor', 'parms', 'frame', 'context', 'act', 'iois')

    def __init__(self, **kwa ):
        """ Initialization method for instance.

            Inherited attributes
                .actor = Actor instance callable , call performs instances method action
                .parms = dictionary of keyword arguments for .act
                .frame = Frame reference to frame holding act
                .context = Action execution context name string
                .act = Act reference if act in embedded in another act such as Need
                .iois = dictionary of share initializers of parms with same key

        """
        super(Nact,self).__init__(**kwa)


    def __call__(self): #make Act instance callable as function
        """Define act as callable object
           Negate the output
        """
        return not (self.actor(**self.parms))


    def expose(self):
        """ Show attributes """
        console.terse("Nact Actor {0} Parms {1} in Frame {2} Context {3} SuperAct {4}\n".format(
                    self.actor, self.parms, self.frame, self.context, self.act))
        if self.actor:
            self.actor.expose()


class Actor(registering.StoriedRegistry):
    """Actor Patron Registry Class 
       for executing actions
       via its action method 
    """
    Counter = 0  
    Names = {}

    def __init__(self, name = '', **kwa ):
        """ Initialization method for instance.

            inherited attributes
                .name = unique name for actor instance
                .store = shared data store
              
            The registry class will supply unique name when name is empty by using
            the .__class__.__name__ as the default preface to the name.
            To use a different default preface add this to the .__init__ method
            before the super call
            
            if 'preface' not in kw:
                kw['preface'] = 'MyDefaultPreface'


        """
        super(Actor,self).__init__(name = name, **kwa)
    
    def __call__(self, **kwa):
        """run .action

        """
        return self.action(**kwa)
    
    def action(self, **kwa):
        """Action called by Actor. Should override in subclass."""
        console.profuse("Actioning {0} with {1}\n".format(self.name, str(kwa)))

        pass
    
    def expose(self):
        """Show Actor."""
        console.terse("Actor {0}".format(self.name))
        
    def clone(self):
        """ Clone self in support of framer cloning.
            Actors that are fully parametrized work as singletons so just return
            self. Non fully parametrized actor classes need to override to make
            copy of instance
        """
        return self
       
    def cloneParms(self, parms, clones, **kwa):
        """ Returns parms fixed up for framer cloning. This includes:
            Reverting any Frame links to name strings,
            Reverting non cloned Framer links into name strings
            Replacing any cloned framer links with the cloned name strings from clones
            Replacing any parms that are acts, in this case the needs with clones.
            
            clones is dict whose items keys are original framer names
            and values are duples of (original,clone) framer references
        """
        parms = self.rerefShares(parms, clones)
        return parms
    
    def rerefShares(self, parms, clones):
        """ Returns parms fixed up for framer cloning.
            clones is dict whose items keys are original framer names
            and values are duples of (original,clone) framer references
            
            Generates oldPrefix and newPrefix from the original and new framer names
            Replaces refs to shares whose path starts with oldPrefix
                    with refs to new shares whose path starts with newPrefix.
            The rest of the path stays the same.
            Create new share if needed.
            Deep copy the contents of the share.
            This is to support framer cloning so typically the path prefixes
            are framer relative paths.
        """
        for key, val in parms.items():
            if isinstance(val, storing.Share):
                for original, clone in clones.values():
                    oldPrefix = "framer.{0}.".format(original.name)
                    newPrefix = "framer.{0}.".format(clone.name)                
                    if val.name.startswith(oldPrefix):
                        newPath = val.name.replace(oldPrefix, newPrefix, 1)
                        newShare = self.store.create(newPath)
                        stuff = {}
                        for k, v in val.items():
                            stuff[k] = copy.deepcopy(v)
                        newShare.create(stuff)
                        parms[key] = newShare                    

        return parms      
    
    def resolveLinks(self, _act, **kwa):
        """ Resolves any links in parms for Actor
            should be overridden by sub class
        """
        parms =  {}

        if _act.iois:
            for key, ioi in _act.iois.items():
                if key in kwa:
                    raise excepting.ResolveError("ResolveError: Parm and Ioi with same key", key, _act)
                
                parms[key] = storing.resolvePath(   store=self.store,
                                                    ipath=ioi['ipath'],
                                                    ival=ioi.get('ival'), 
                                                    iown=ioi.get('iown'),
                                                    act=_act)
        return parms


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
    __slots__ = ('_interruptive', )
    
    def __init__(self,**kw ):
        """Initialization method for instance. """
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
        
    def cloneParms(self, parms, clones, **kw):
        """ Returns parms fixed up for framing cloning. This includes:
            Reverting any Frame links to name strings,
            Reverting non cloned Framer links into name strings
            Replacing any cloned framer links with the cloned name strings from clones
            Replacing any parms that are acts, in this case the needs with clones.
            
            clones is dict whose items keys are original framer names
            and values are duples of (original,clone) framer references
        """
        parms = super(Transiter,self).cloneParms(parms, clones, **kw)
        
        needs = parms.get('needs')
        near = parms.get('near')
        far =  parms.get('far')

        if needs:
            needClones = []
            for act in needs:
                needClones.append(act.clone())
            parms['needs'] = needClones
        
        if isinstance(near, framing.Frame):
            parms['near'] = near.name # revert to name
        
        if isinstance(far, framing.Frame):
            parms['far'] = far.name # revert to name        
        
        return parms    
        
    def resolveLinks(self, _act, needs, near, far, human, **kw):
        """Resolve any links in far and in associated parms for actors"""

        parms = {}
        
        if not isinstance(near, framing.Frame):
            if near not in framing.Frame.Names:
                raise excepting.ResolveError("ResolveError: Bad near link",
                                            human, near)
            parms['near'] = near = framing.Frame.Names[near] #replace name with valid link        

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
            act.act = _act
            act.resolveLinks()

        return parms


class Suspender(Interrupter):
    """Suspender Interrupter Actor Patron Registry Class 
       Suspender  is a special actor that performs a conditional auxiliary
          which truncates the active outline effectively suspended the truncated
          frames

       Instance Attributes
          ._activative = flag which indicates this actor's action returns conditional aux

       Parameters
            needs = list of Act objects that are exit needs for this trans
            main = source frame of trans
            aux = target frame of trans
            human = text version of transition

    """
    __slots__ = ('_activative',)
    
    def __init__(self,**kw ):
        """Initialization method for instance. """
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

    def cloneParms(self, parms, clones, **kw):
        """ Returns parms fixed up for framing cloning. This includes:
            Reverting any Frame links to name strings,
            Reverting non cloned Framer links into name strings
            Replacing any cloned framer links with the cloned name strings from clones
            Replacing any parms that are acts, in this case the needs with clones.
            
            clones is dict whose items keys are original framer names
            and values are duples of (original,clone) framer references
        """
        parms = super(Suspender,self).cloneParms(parms, clones, **kw)
        
        needs = parms.get('needs')
        main = parms.get('main')
        aux = parms.get('aux')
        
        if needs:
            needClones = []
            for act in needs:
                needClones.append(act.clone())
            parms['needs'] = needClones
        
        if isinstance(main, framing.Frame):
            parms['main'] = main.name # revert to name
               
        if isinstance(aux, framing.Framer):
            if aux.name in clones:
                parms['aux'] = clones[aux.name][1].name #change to clone name
            else:
                parms['aux'] = aux.name # revert to name
        elif aux: # assume namestring
            if aux in clones:
                parms['aux'] = clones[aux][1].name # change to clone name
        
        return parms

    def resolveLinks(self, _act, needs, main, aux, human, **kw):
        """Resolve any links aux and in associated parms for actors"""

        parms = {}
        
        if not isinstance(main, framing.Frame):
            if main not in framing.Frame.Names:
                raise excepting.ResolveError("ResolveError: Bad main link", human, main)
            parms['main'] = main = framing.Frame.Names[main] #replace name with valid link                    

        if not isinstance(aux, framing.Framer):
            if aux not in framing.Framer.Names:
                raise excepting.ResolveError("ResolveError: Bad aux link",
                                                main.name + " " + human, aux)                
                
            parms['aux'] = aux = framing.Framer.Names[aux] #replace name with valid link
            console.terse("    Resolved aux as {0} in {1}".format(aux.name, main.name))

        if aux.schedule != AUX:
            raise excepting.ResolveError("ResolveError: Bad aux link not scheduled as AUX",
                                         main.name + " " + human, aux)

        for act in needs:
            act.act = _act
            act.resolveLinks()

        return parms


class Deactivator(Actor):
    """Deactivator Actor Patron Registry Class 

       Deactivator is a special actor that acts on an Act

       In the Deactivator's action method, 
          IF the act passed in as a parameter has an _activate attribute THEN
                       it calls the deactivate method
       This is to ensure the outline in cond aux is exited cleanly when the aux
          is preempted by higher level transition.

       Builder adds a deactivator for each Suspender preact
    """
    def action(self, actor, aux, **kw):
        """Action called by Actor
        """
        #console.profuse("{0} action {1} for {2}\n".format(self.name, actor.name, aux.name))

        if hasattr(actor, '_activative') and not aux.done:
            console.profuse("{0} deactivate {1} for {2}\n".format(self.name, actor.name, aux.name))
            return actor.deactivate(aux)

    def expose(self):
        """   """
        console.terse("Deactivator {0}\n".format(self.name))
        
    def cloneParms(self, parms, clones, **kw):
        """ Returns parms fixed up for framing cloning. This includes:
            Reverting any Frame links to name strings,
            Reverting non cloned Framer links into name strings
            Replacing any cloned framer links with the cloned name strings from clones
            Replacing any parms that are acts with clones.
            
            clones is dict whose items keys are original framer names
            and values are duples of (original,clone) framer references
        """
        parms = super(Deactivator,self).cloneParms(parms, clones, **kw)
        
        actor = parms.get('actor')
        aux = parms.get('aux')
        
        if isinstance(aux, framing.Framer):
            parms['aux'] = aux.name # revert to name
        
        if isinstance(aux, framing.Framer):
            if aux.name in clones:
                parms['aux'] = clones[aux.name][1].name
            else:
                parms['aux'] = aux.name # revert to name
        elif aux: # assume namestring
            if aux in clones:
                parms['aux'] = clones[aux][1].name        

        return parms
              
    def resolveLinks(self, actor, aux, **kw):
        """Resolve any links aux and in associated parms for actors"""

        parms = {}

        if not isinstance(aux, framing.Framer):
            if aux not in framing.Framer.Names:
                raise excepting.ResolveError("ResolveError: Bad far link",
                                                             near.name + " " + human, far)                
            parms['aux'] = aux = framing.Framer.Names[aux] #replace name with valid link
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
    def action(self, message, **kw):
        """Action called by Actor
        """
        #console.terse("{0} printer {1}\n".format(self.name, message))
        console.terse("*** {0} ***\n".format(message))

    def expose(self):
        """   """
        console.terse("Printer {0}\n".format(self.name))
        
class Marker(Actor):
    """ Base class that sets up mark in provided share reference"""
    
    def cloneParms(self, parms, clones, **kw):
        """ Returns parms fixed up for framing cloning. This includes:
            Reverting any Frame links to name strings,
            Reverting non cloned Framer links into name strings
            Replacing any cloned framer links with the cloned name strings from clones
            Replacing any parms that are acts with clones.
            
            clones is dict whose items keys are original framer names
            and values are duples of (original,clone) framer references
        """
        parms = super(Marker,self).cloneParms(parms, clones, **kw)
        
        share = parms.get('share')
        name = parms.get('name')
        
        #don't need to do anything yet since rerefShares will reref

        return parms    
    
    def resolveLinks(self, share, name, **kw):
        """Resolves share and adds mark in share"""
        parms = {}
            
        return parms    
        
class UpdateMarker(Marker):
    """ UpdateMarker Class 

        UpdateMarker is a special actor that acts on a share to mark the update by
            saving a copy of the last stamp
       
        UpdateMarker works with UpdateNeed which does the comparison against the marked stamp.
       
        Builder at parse time when it encounters an UpdateNeed,
        creates the mark in the share and creates the appropriate UpdateMarker 
    """
    def action(self, share, name, **kw):
        """ Update mark in share
            Where share is reference to share and name is frame name key of mark in
                share.marks odict
            Updates mark.stamp
            
            only one mark per frame per share is needed 
        """
        console.profuse("{0} mark {1} in {2} on {3}\n".format(
            self.name, share.name, name, 'update' ))

        mark = share.marks.get(name)
        if mark:
            mark.stamp = self.store.stamp #stamp when marker runs

    def expose(self):
        """   """
        console.terse("UpdateMarker {0}\n".format(self.name))
        
class ChangeMarker(Marker):
    """ ChangeMarker Class 

        ChangeMarker is a special actor that acts on a share to mark save a copy
        of the data in the mark for the share.
       
        ChangeMarker works with ChangeNeed which does the comparison with the mark
       
        Builder at parse time when it encounters a ChangeNeed,
        creates the mark in the share and creates the appropriate marker 
    """
    def action(self, share, name, **kw):
        """ Update mark in share
            Where share is reference to share and name is frame name key of mark in
                share.marks odict
            Updates mark.data
            
            only one mark per frame per share is needed 
        """
        console.profuse("{0} mark {1} in {2} on {3}\n".format(
            self.name, share.name, name, 'change' ))

        mark = share.marks.get(name)
        if mark:
            mark.data = storing.Data(share.items())

    def expose(self):
        """   """
        console.terse("ChangeMarker {0}\n".format(self.name))

