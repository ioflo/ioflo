"""acting.py action module

"""
#print "module %s" % __name__

import time
import struct
from collections import deque, Mapping
from functools import wraps
import inspect
import copy

from .globaling import *
from .odicting import odict

from . import aiding
from .aiding import NonStringIterable, nameToPath
from . import excepting
from . import registering
from . import storing
from . import framing

from .consoling import getConsole
console = getConsole()


#Class definitions

class Act(object):
    """ Container class for actor resolve time initialization and runtime operation """
    __slots__ = ('frame', 'context', 'act',
                 'actor', 'registrar', 'parms', 'inits', 'ioinits')

    def __init__(self, frame=None, context=None, act=None, actor=None, registrar=None,
                 parms=None, inits=None, ioinits=None, action='', **kwa ):
        """ Initialization method for instance.

            Attributes:
            .frame = ref to Frame holding this Act
            .context = name string of actioning context set when added to frame
            .act = ref to super Act if self is embedded in another Act such as Need
            .actor = ref to Actor instance or actor name to be resolved
                    call performs instances method action
            .registrar = ref to Actor class holding .Registry
            .parms = dictionary of keyword arguments for Actor instance call
            .inits = dictionary of arguments to Actor.__init__()
            .ioinits = dictionary of arguments to Actor.initio()
        """
        super(Act,self).__init__()

        self.frame = frame
        self.context = context
        self.act = act
        self.actor = actor #callable instance performs action
        self.registrar = registrar or Actor
        self.parms = parms if parms else None # parms must always be not None
        self.inits = inits if inits else None # store None if empty dict
        self.ioinits = ioinits if ioinits else None # store None if empty dict

    def __call__(self): #make Act instance callable as function
        """ Define act as callable object """
        return (self.actor(**self.parms))

    def expose(self):
        """ Show attributes"""
        console.terse("Act Actor {0} Parms {1} in Frame {2} Context {3} SuperAct {4}\n".format(
                    self.actor, self.parms, self.frame, self.context, self.act))
        if self.actor:
            self.actor.expose()

    def resolve(self, **kwa):
        """ Resolve .frame attribute and .actor. Cause .actor to resolve its parms """
        if self.act: # this is sub act of another act self.act so get super act context
            self.frame = self.act.frame
            self.context = self.act.context
        self.frame = framing.resolveFrame(self.frame, who=self)

        if not isinstance(self.actor, Actor): # Need to resolve .actor
            actor, inits, ioinits, parms = self.registrar.__fetch__(self.actor)
            inits.update(self.inits or odict())
            if 'name' not in inits:
                inits['name'] = self.actor
            inits['store'] = self.frame.store
            inits['act'] = self
            self.actor = actor = actor(**inits)

            parms.update(self.parms or odict())
            ioinits.update(self.ioinits or odict())
            if ioinits:
                iois = actor.initio(**ioinits)
                if iois:
                    for key, ioi in iois.items():
                        share = actor.resolvePath(   ipath=ioi['ipath'],
                                                     ival=ioi.get('ival'),
                                                     iown=ioi.get('iown'))
                        if actor._Parametric:
                            if key in parms:
                                msg = "ResolveError: Parm and Ioi with same name"
                                raise excepting.ResolveError(msg, key, self)
                            parms[key] = share
                        else:
                            if hasattr(actor, key):
                                msg = "ResolveError: Attribute and Ioi with same name"
                                raise excepting.ResolveError(msg, key, self)
                            setattr(actor, key, share)
            self.parms = parms
            self.parms.update(self.actor.resolve(**self.parms))
            self.actor.postinitio(**self.parms)

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

class Nact(Act):
    """ Negating Act used for actor needs to give Not Need
    """
    __slots__ = ('frame', 'context', 'act',
                 'actor', 'registrar', 'parms', 'inits', 'ioinits')

    def __init__(self, **kwa ):
        """ Initialization method for instance. """
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

class SideAct(Act):
    """ Anciliary act to a main Act/Actor used to call a different 'action' method
        of the Main act.actor in support of combined activity such as restarting
        an action.

        SideActa are created in the .resolve method of an Actor and assume that
        all attributes and parms have already been resolved.

        Unique Attributes:
            .action = name of method to call in .actor
    """
    __slots__ = ('action')

    def __init__(self, action='', **kwa ):
        """ Initialization method for instance. """
        super(SideAct, self).__init__(**kwa)
        self.action = action

    def __call__(self): #make Act instance callable as function
        """ Define call method named .action of .actor """
        return (getattr(self.actor, self.action)(**self.parms))

    def resolve(self, **kwa):
        """ Assumes all has been resolved.
            Check for valid action
        """
        if not isinstance(self.actor, Actor): # Woops
            msg = "ResolveError: Unresolved actor"
            raise excepting.ResolveError(msg, self.actor, self)

        if not self.action : # Woops
            msg = "ResolveError: Empty action"
            raise excepting.ResolveError(msg, self.action, self)

        if not getattr(self.actor, self.action, None):
            msg = "ResolveError: Missing action in actor"
            raise excepting.ResolveError(msg, self.action, self)

def actorify(name, base=None, registry=None, inits=None, ioinits=None, parms=None,
             parametric=None):
    """ Parametrized decorator function that converts the decorated function
        into an Actor sub class with .action method and with class name that
        is the reverse camel case of name and registers the
        new subclass in the registry under name.
        If base is not provided then use Actor

        The parameters  registry, parametric, inits, ioinits, and parms if provided,
        are used to create the class attributes for the new subclass

    """
    base = base or Actor
    if not issubclass(base, Actor):
        msg = "Base class '{0}' not subclass of Actor".format(base)
        raise excepting.RegisterError(msg)

    name = aiding.reverseCamel(name, lower=False)

    attrs = odict()
    if registry:
        attrs['Registry'] = odict()
    if parametric is not None:
        attrs['_Parametric'] = parametric
    if inits:
        attrs['Inits'] = odict(inits)
    if ioinits:
        attrs['Ioinits'] = odict(ioinits)
    if parms:
        attrs['Parms'] = odict(parms)
    cls = type(name, (base, ), attrs )

    def implicit(func):
        @wraps(func)
        def inner(*pa, **kwa):
            return func(*pa, **kwa)
        cls.action = inner
        return inner
    return implicit

class Actor(object): # old registering.StoriedRegistry
    """ Actor Base Class
        Has Actor specific Registry of classes
    """
    __metaclass__ = registering.RegisterType
    Registry = odict() # Actor Registry
    Inits = odict() # class defaults support for
    Ioinits = odict() # class defaults
    Parms = odict() # class defaults
    _Parametric = True # Convert iois to action method parameters if Truthy
    __slots__ = ('name', 'store', 'act')

    def __init__(self, name='', store=None, act=None, **kwa ):
        """ Initialization method for instance.

            Instance attributes
                .name = name string for Actor variant in class Registry
                .store = reference to shared data Store
                .act = reference to containing Act
        """
        self.name = name
        if store is not None:
            if  not isinstance(store, storing.Store):
                raise ValueError("Not store %s" % store)
            self.store = store
        self.act = act

    def __call__(self, **kwa):
        """ run .action  """
        return self.action(**kwa)

    def action(self, **kwa):
        """Action called by Actor. Should override in subclass."""
        console.profuse("Actioning {0} with {1}\n".format(self.name, str(kwa)))
        pass

    def expose(self):
        """Show Actor."""
        console.terse("Actor {0}".format(self.name))

    def resolve(self, **kwa):
        """ Return updated parms
            Extend in subclass to resolve specific kwa items that are links or
            share refs and update parms
        """
        parms = odict()

        return parms

    def initio(self, inode='', **kwa):
        """ Intialize and hookup ioflo shares from node pathname inode and kwa arguments.
            This implements a generic Actor interface protocol for associating the
            io data flow shares to the Actor.

            inode is the computed pathname string of the default share node
            where shares associated with the Actor instance may be placed when
            relative addressing is used.

            The values of the items in the **kwa argument may be either strings or
            mappings

            For each key,val in **kwa.items() there are the following 2 forms for val:

            1- string:
               ipath = pathnamestring
            2- dict of items (mapping) of form:
                {
                    ipath: "pathnamestring", (optional)
                    ival: initial value, (optional)
                    iown: truthy, (optional)
                }

            In either case, three init values are produced, these are:
                ipath, ival, iown,
            Missing init values from ipath, ival, iown will be assigned a
            default value as per the rules below:

            For each kwa item (key, val)
                key is the name of the associated instance attribute or action parm.
                Extract ipath, ival, iown from val

                Shares are initialized with mappings passed into share.create or
                share.update. So to assign ival to share.value pass into share.create
                or share.update a mapping of the form {'value': ival} whereas
                passing in an empty mapping does nothing.

                If ipath not provided
                    ipath is the default path inode.key
                Else ipath is provided
                    If ipath starts with dot "." Then absolute path
                    Else ipath does not start with dot "." Then relative path from inode

                    If ipath ends with dot Then the path is to a node not share
                            node ref is created and remaining init values are ignored


                If ival not provided
                     set ival to empty mapping which when passed to share.create
                     will not change share.value
                Else ival provided
                    If ival is an empty Mapping Then
                        assign a shallow copy of ival to share.value by passing
                        in {value: ival (copy)} to share.create/.update
                    Else If ival is a non-string iterable and not a mapping
                        assign a shallow copy of ival to share.value by passing
                        in {value: ival (copy)} to share.create/.update
                    Else If ival is a non-empty Mapping Then
                        Each item in ival is assigned as a field, value pair in the share
                        by passing ival directly into share.create or share.update
                        This means there is no way to init a share.value to a non empty mapping
                        It is possible to init a share.value to an empty mapping see below
                    Else
                        assign ival to share.value by by passing
                        in {value: ival} to share.create or share.update

                Create share with pathname given by ipath

                If iown Then
                    init share with ival value using update
                Else
                    init share with ival value using create ((change if not exist))

        """
        if not isinstance(inode, basestring):
            raise ValueError("Nonstring inode arg '{0}'".format(inode))

        if not inode:
            inode = aiding.nameToPath(self.name)

        if not inode.endswith('.'):
            inode = "{0}.".format(inode)

        iois = odict()

        for key, val in kwa.items():
            if val == None:
                continue

            if isinstance(val, basestring):
                ipath = val
                iown = None
                ival = odict() # effectively will not change share
            elif isinstance(val, Mapping): # dictionary
                ipath = val.get('ipath')
                iown = val.get('iown')

                if not 'ival' in val:
                    ival = odict() # effectively will not change share
                else:
                    ival = val['ival']
                    if isinstance(ival, Mapping):
                        if not ival: #empty mapping
                            ival = odict(value=copy.copy(ival)) #make copy so each instance unique
                        # otherwise don't change since ival is non-empty mapping
                    elif isinstance(ival, NonStringIterable): # not mapping and NonStringIterable
                        ival = odict(value=copy.copy(ival))
                    else:
                        ival = odict(value=ival)
            else:
                raise ValueError("Bad init kw arg '{0}'with Value '{1}'".format(key, val))

            if ipath:
                if not ipath.startswith('.'): # full path is inode joined to ipath
                    ipath = '.'.join((inode.rstrip('.'), ipath)) # when inode empty prepends dot
            else:
                ipath = '.'.join(inode.rstrip('.'), key)
            ioi = odict(ipath=ipath, ival=ival, iown=iown)
            iois[key] = ioi

        ioi = odict(ipath=inode)
        iois['inode'] = ioi

        return iois # non-empty when _parametric

    def postinitio(self, **kwa):
        """ Base method to be overriden in sub classes. Perform post initio setup
            after all parms and ioi parms or attributes have been created
            kwa usually parms
        """
        pass

    def resolvePath(self, ipath, ival=None, iown=None):
        """ Returns resolved Share or Node instance from ipath
            ipath may be path name of share or node
            or reference to Share or Node instance

            This method resolves pathname strings into share and node references
            at resolve time.

            It allows for substitution into ipath of
            frame, framer, main frame, or main framer relative names.
            So that lexically relative pathnames can
            be dynamically resolved in support of framer cloning.
            It assumes that any implied variants have been reconciled.

            When ipath is a string:  (not a Node or Share reference)
                the following syntax is used:

                If the path name starts with a leading '.' dot then path name is
                fully reconciled and no contextual substitutions are to be applied.

                Otherwise make subsitutions in pathname strings that begin
                with 'framer.' and have the special framer and/or frame names
                of 'me' or 'main'.

                'me' indicates substitute the current framer or frame name respectively.

                'main' indicates substitute the current frame's main framer or main frame
                name respectively.

            When  ipath is a pathname string that resolves to a Share and ival is not None
            Then ival is used to initialize the share values.
                ival should be a dict of fields and values

                If own is True then .update(ival) is used
                Otherwise .create(ival) is used

            Requires that
               self.name is not empty
               self.store exist
               self.act exist

               The following have already been resolved:
               self.act.frame
               self.act.frame.framer
               self.act.frame.framer.main
               self.act.frame.framer.main.framer

        """
        if not (isinstance(ipath, storing.Share) or isinstance(ipath, storing.Node)): # must be pathname
            if not ipath.startswith('.'): # not reconciled so do relative substitutions
                parts = ipath.split('.')
                if parts[0] == 'framer':  #  relative addressing
                    if not self.act:
                        raise excepting.ResolveError("ResolveError: Missing act context"
                                " to resolve relative pathname.", ipath, self)
                    if not self.act.frame:
                        raise excepting.ResolveError("ResolveError: Missing frame context"
                            " to resolve relative pathname.", ipath, self.act)
                    if not self.act.frame.framer:
                        raise excepting.ResolveError("ResolveError: Missing framer context"
                            " to resolve relative pathname.", ipath, self.act.frame)

                    if parts[1] == 'me': # current framer
                        parts[1] = self.act.frame.framer.name
                    elif parts[1] == 'main': # current main framer
                        if not self.act.frame.framer.main:
                            raise excepting.ResolveError("ResolveError: Missing main frame"
                                " context to resolve relative pathname.", ipath,
                                self.act.frame.framer)
                        parts[1] = self.act.frame.framer.main.framer.name

                    if (len(parts) >= 3):
                        if parts[2] == 'frame':
                            if parts[3] == 'me':
                                parts[3] = self.frame.name
                            elif parts[3] == 'main':
                                if not self.act.frame.framer.main:
                                    raise excepting.ResolveError("ResolveError: "
                                        "Missing main frame context to resolve "
                                        "relative pathname.", ipath,
                                        self.act.frame.framer)
                                parts[3] = self.act.frame.framer.main.name
                            if (len(parts) >= 5 ) and parts[4] == 'actor':
                                if parts[5] == 'me': # slice insert multiple parts
                                    if not self.name:
                                        raise excepting.ResolveError("ResolveError: Missing name"
                                            " context to resolve relative pathname.", ipath, self)
                                    parts[5:6] = nameToPath(self.name).rstrip('.').split('.')
                        elif parts[2] == 'actor':
                            if parts[3] == 'me': # slice insert multiple parts
                                if not self.name:
                                    raise excepting.ResolveError("ResolveError: Missing name"
                                        " context to resolve relative pathname.", ipath, self)
                                parts[3:4] = nameToPath(self.name).rstrip('.').split('.')

                ipath = '.'.join(parts)

            if not self.store:
                raise excepting.ResolveError("ResolveError: Missing store context"
                                " to resolve relative pathname.", ipath, self)
            if ipath.endswith('.'): # Node not Share
                ipath = self.store.createNode(ipath.rstrip('.'))
            else: # Share
                ipath = self.store.create(ipath)
                if ival != None:
                    if iown:
                        ipath.update(ival)
                    else:
                        ipath.create(ival)

        return ipath

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

class Interrupter(Actor):
    """Interrupter Actor Patron Registry Class
       Interrupter is a base clase for all actor classes that interrupt normal precur
       processing and result in a change in the frame or the frame processing.

       This class must be subclassed. This is a convenience so can either use
         isinstance to test

       Specifically and Interrupter's action() method returns truthy when its action
       will interrupt the normal frame processing examples are
       Transitors which interrupt by changing to a new frame
       Suspenders which interrupt when the conditional aux condition is true and
          further processing of the frame and sub frames is stopped


    """
    def __init__(self,**kw ):
        """Initialization method for instance. """
        super(Interrupter,self).__init__(**kw)

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

    def resolve(self, needs, near, far, human, **kwa):
        """Resolve any links in far and in associated parms for actors"""

        parms = super(Transiter, self).resolve( **kwa)

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
            act.act = self.act
            act.resolve()

        return parms

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

class Suspender(Interrupter):
    """Suspender Interrupter Actor Patron Registry Class
       Suspender  is a special actor that performs a conditional auxiliary
          which truncates the active outline effectively suspended the truncated
          frames

       Parameters
            needs = list of Act objects that are exit needs for this trans
            main = source frame of trans
            aux = target frame of trans
            human = text version of transition

    """
    def __init__(self,**kw ):
        """Initialization method for instance. """
        super(Suspender,self).__init__(**kw)

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

    def deactivize(self, aux, **kwa):
        """ If not aux.done Then force deactivate. Used in exit action."""
        if not aux.done:
            console.profuse("{0} deactivate {1}\n".format(self.name, aux.name))
            self.deactivate(aux)

    def deactivate(self, aux):
        """Called by deactivator actor to cleanly exit      """
        console.profuse("Deactivating {0}\n".format(aux.name))

        aux.exitAll() # also sets .done = True
        aux.main = None

    def resolve(self, needs, main, aux, human, **kwa):
        """Resolve any links aux and in associated parms for actors"""
        parms = super(Suspender, self).resolve( **kwa)

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
            act.act = self.act
            act.resolve()

        deActParms = dict(aux=aux)
        deAct = SideAct( actor=self,
                        parms=deActParms,
                        action='deactivize')
        self.act.frame.addExact(deAct)
        console.profuse("     Added Exact {0} with {1}\n".format(deAct.actor, deAct.parms))
        deAct.resolve()

        return parms

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


class Restarter(Actor):
    """ Restarter is a special actor that acts on other act's actor
        In the Restarter's action method,
            if the act.actor passed in as a parameter has a restart attribute
                 it calls the act.actor.restart() method

        Doesn't need to resolve its action method's 'act' parm because the act has
        own entry in Frame it will get resolved normally

        Restarter act is created in .resolve of Deed's that need restarting.
    """
    def action(self, act, **kw):
        """ Action called by Actor
        """
        console.profuse("{0} restart {1}\n".format(self.name, act.actor.name))

        if hasattr(act.actor, 'restart'):
            return act.actor.restart()

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

class UpdateMarker(Marker):
    """ UpdateMarker Class

        UpdateMarker is a special actor that acts on a share to mark the update by
            saving a copy of the last stamp

        UpdateMarker works with UpdateNeed which does the comparison against the marked stamp.

        Builder at parse time when it encounters an UpdateNeed,
        creates the mark in the share and creates the appropriate UpdateMarker
    """
    def action(self, share, frame, **kwa):
        """ Update mark in share
            Where share is reference to share and frame is frame name key of mark in
                share.marks odict
            Updates mark.stamp

            only one mark per frame per share is needed
        """
        console.profuse("{0} mark {1} in {2} on {3}\n".format(
            self.name, share.name, frame, 'update' ))

        mark = share.marks.get(frame)
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
    def action(self, share, frame, **kwa):
        """ Update mark in share
            Where share is reference to share and frame is frame name key of mark in
                share.marks odict
            Updates mark.data

            only one mark per frame per share is needed
        """
        console.profuse("{0} mark {1} in {2} on {3}\n".format(
            self.name, share.name, frame, 'change' ))

        mark = share.marks.get(frame)
        if mark:
            mark.data = storing.Data(share.items())

    def expose(self):
        """   """
        console.terse("ChangeMarker {0}\n".format(self.name))

