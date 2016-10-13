"""acting.py action module

"""
#print("module {0}".format(__name__))

import time
import struct
from collections import deque, Mapping
from functools import wraps
import inspect
import copy
try:
    from itertools import izip
except ImportError: #python 3 zip is same as izip
    izip = zip

from ..aid.sixing import *
from .globaling import AUX, MOOT, INDENT_ADD, ScheduleNames, TRANSIT, ActionSubContextNames
from ..aid.odicting import odict

from ..aid.classing import metaclassify, nonStringIterable
from ..aid.aiding import nameToPath
from . import excepting
from . import registering
from . import storing
from . import framing

from ..aid.consoling import getConsole
console = getConsole()


#Class definitions

class Act(object):
    """ Container class for actor resolve time initialization and runtime operation """
    __slots__ = ('frame', 'context', 'act', 'actor',
                 'registrar', 'inits', 'ioinits', 'parms',
                 'prerefs', 'human', 'count', 'inode')

    def __init__(self, frame=None, context=None, act=None, actor=None,
                 registrar=None, inits=None, ioinits=None, parms=None,
                 prerefs=None, human='', count=0, inode=None, **kwa ):
        """
        Initialization method for instance.

        Attributes:
            .frame = ref to Frame holding this Act
            .context = name string of actioning context set when added to frame
            .act = ref to super Act if self is embedded in another Act such as Need
            .actor = ref to Actor instance or actor name to be resolved
                    call performs instances method action
            .registrar = ref to Actor class holding .Registry
            .parms = dictionary of keyword arguments for Actor instance call
            .inits = dictionary of arguments to Actor.__init__()
            .ioinits = dictionary of arguments to Actor._initio()
            .prerefs = dictionary of init, ioinit, and parm refs to resolve
            .human = human friendly version of action declaration
            .count = line count in floscript of action declaration
            .inode = actor level inode for ioinits if any

        Share path resolution
            act.resolve aggregates ioinits from registry,  act.ioinits, and act.prerefs
            act.resolve calls .actor._initio with ionits as parameters to get iois
            then for each ioi act.resolve calls .resolvePath to get share or node
            and then assigns share/node to to attribute/parameter of .actor

        """
        super(Act,self).__init__(**kwa) # in case of MRO

        self.frame = frame
        self.context = context
        self.act = act # should normally not be set until resolve time
        self.actor = actor #callable instance performs action
        self.registrar = registrar or Actor
        self.parms = parms if parms is not None else odict() # parms must always be not None
        self.inits = inits if inits else None # store None if empty dict
        self.ioinits = ioinits if ioinits else None # store None if empty dict
        self.prerefs = prerefs if prerefs else None # store None if empty dict
        self.human = human  # human readable version of FloScript declaration
        self.count = count  # line number or count of FloScript declaration
        self.inode = inode  # inode None means ignore

    def clone(self):
        """ Return clone of self in support of framer cloning
            clones is dict whose items keys are original framer names
            and values are duples of (original,clone) framer references
        """
        if isinstance(self.frame, framing.Frame):
            msg = ("CloneError: Attempting to clone resolved frame link"
                "  '{0}'.".format(self.frame.name))
            raise excepting.CloneError(msg)

        if self.act:
            msg = ("CloneError: Attempting to clone resolved act link"
                   "  '{0}'.".format(self.act))
            raise excepting.CloneError(msg)

        if isinstance(self.actor, Actor):
            msg = ("CloneError: Attempting to clone resolved actor"
                "  '{0}'.".format(self.actor.name))
            raise excepting.CloneError(msg)

        # frame and context for Act set when add Act to frame later
        clone = copy.deepcopy(self)
        return clone

    def __call__(self): #make Act instance callable as function
        """ Define act as callable object """
        return (self.actor(**self.parms))

    def expose(self):
        """ Show attributes"""
        console.terse("Act Actor {0} Parms {1} in Frame {2} Context {3} SuperAct {4}\n".format(
                    self.actor, self.parms, self.frame, self.context, self.act))
        if self.actor:
            self.actor._expose()

    def resolve(self, **kwa):
        """ Resolve .frame attribute and .actor. Cause .actor to resolve its parms """
        if self.act: # this is sub act of another act self.act so get super act context
            self.frame = self.act.frame
            self.context = self.act.context
        self.frame = framing.resolveFrame(self.frame,
                                          who="Act for {0}".format(self.actor),
                                          desc="act's",
                                          human=self.human,
                                          count=self.count)

        if not isinstance(self.actor, Actor): # Need to resolve .actor
            # .actor is currently unresolved name string for actor
            actor, inits, ioinits, parms = self.registrar.__fetch__(self.actor)

            if self.prerefs: # preinits inits dict items  'do qua'
                # each key is share src path, and value is list of src fields
                for src, fields in self.prerefs.get('inits', {}).items():
                    src = self.resolvePath(ipath=src, warn=True) # now a share
                    if not fields:  # default is use existing fields
                        fields = self._prepareSrcFields(src, fields)
                    for field in fields:  # requires src pre inited
                        if field in src:  # only update if src has field
                            inits[field] = src[field]
            inits.update(self.inits or odict())  # 'do cum' overrides qua, self.inits may be None
            if 'name' not in inits:
                inits['name'] = self.actor  # as yet unresolved name string
            inits['store'] = self.frame.store
            inits['act'] = self
            self.actor = actor = actor(**inits) # instantiate and convert

            if self.prerefs: # preinits parms dict items 'do from'
                # each key is share src path, and value is list of src fields
                for src, fields in self.prerefs.get('parms', {}).items():
                    src = self.resolvePath(ipath=src, warn=True) # now a share
                    if not fields:  # default is use existing fields
                        fields = self._prepareSrcFields(src, fields)
                    for field in fields:  # requires src pre inited
                        if field in src:  # only update if src has field
                            parms[field] = src[field]
            parms.update(self.parms or odict())  # 'do with' overrides from, self.parms may be None

            #  compute .inode
            self.inode = (self.ioinits or odict()).get('inode', ioinits.get('inode', self.inode))
            if self.inode is not None and not isinstance(self.inode, basestring):
                raise ValueError("Nonstring inode '{0}'".format(self.inode))
            if self.inode and not self.inode.endswith("."):  # ensure node not share path
                self.inode = "{0}.".format(self.inode)

            rioinits = odict(ioinits)  # save copy registry ioinits to keep ival iown
            if self.prerefs and 'ioinits' in self.prerefs:  # preinit ioinits dict items  'do for'
                # each key is share src path, and value is list of src fields
                if self.inode is None:  # since prerefs then inode may not be None
                    self.inode = ""
                for src, fields in self.prerefs['ioinits'].items():  # now resolve new src paths
                    src = self.resolvePath(ipath=src, warn=True)  # now a share
                    if not fields:  # default is use existing fields
                        fields = self._prepareSrcFields(src, fields)
                    for field in fields:  # assumes each src fld value pre inited with ipath
                        if field in src and field != "inode":  # only update if src has field
                            ioinits[field] = src[field] # clobbers ioinit odict() with ipath
            ioinits.update(self.ioinits or odict())  # 'do per', 'via inode', self.ioinits may be None
            for key, val in rioinits.items():  # restore registry ival iown defaults
                if key in ioinits:  # check ipath overridden by for or per
                    # if new val not mapping and old val is mapping
                    if not isinstance(ioinits[key], Mapping) and isinstance(val, Mapping):
                        val = val.copy()  # make copy so don't pollute registry
                        val['ipath'] = ioinits[key]  # replace old ipath witn new
                        ioinits[key] = val # restore default ival iown


            if ioinits:
                iois = actor._initio(ioinits)  # .inode may be changed in here
                if iois:
                    for key, ioi in iois.items():
                        if key == "inode":  # compute the final inode
                            share = actor._resolvePath(ipath="", # empty to force
                                                       ival=ioi.get('ival'),
                                                       iown=ioi.get('iown'))
                        else:
                            share = actor._resolvePath(ipath=ioi['ipath'],
                                                       ival=ioi.get('ival'),
                                                       iown=ioi.get('iown'))
                        if actor._Parametric:
                            if key in parms:
                                msg = "ResolveError: Parm and Ioi with same name"
                                raise excepting.ResolveError(msg,
                                                             key,
                                                             self,
                                                             self.human,
                                                             self.count)
                            parms[key] = share
                        else:
                            if hasattr(actor, key):
                                msg = "ResolveError: Attribute and Ioi with same name"
                                raise excepting.ResolveError(msg,
                                                             key,
                                                             self,
                                                             self.human,
                                                             self.count)
                            setattr(actor, key, share)
            self.parms = parms
            self.parms.update(self.actor._resolve(**self.parms)) # resolve sub acts
            self.actor._prepare(**self.parms)

    def resolvePath(self, ipath, ival=None, iown=None, warn=False):
        """
        Returns resolved Share or Node instance from ipath
        ipath may be path name of share or node
        or reference to Share or Node instance

        This method resolves inline pathname strings into share and node references
        at resolve time.

        ival is optional value for share
        iown is optional ownership if True then overwrite if exists
               otherwise do not overwrite

        if warn then will complain if the share is created.

        When ipath is empty then resolvePath returns the effective context node
        path given by .inode and nested frame inodes and framer inodes

        It allows for substitution into ipath of
        inode, framer,  main framer, frame, main frame, or actor relative names.
        So that lexically relative pathnames can
        be dynamically resolved in support of framer cloning.
        It assumes that any implied variants have been reconciled.
        If .actor is not yet instantiated then raises exception if ipath
           uses actor relative addressing. This may occur for init prerefs.

        When ipath is a string:  (not a Node or Share reference)
            the following syntax is used:

            If the path name starts with a leading '.' dot then path name is
            fully reconciled and no contextual substitutions are to be applied.

            If the path name begins with 'me' then the path is framer inode relative

            Otherwise make subsitutions in pathname strings that begin
            with 'framer.'
                Substitute for special path part 'framer' with names of 'me' or 'main'
                Substitute for special path part 'frame' with names  of 'me' or 'main'
                Substitute for special path part 'actor' with name of 'me'

                'me' indicates substitute the current framer, frame, or actor name
                respectively.

                'main' indicates substitute the current .main.frame.name or
                .main.frame.framer.name respectively obtained from aux .main link



        If ipath ends with a '.' then it resolves to a node
        Otherwise if not trailing dot it resolves to a share

        When  ipath is a pathname string that resolves to a Share and ival is not None
        Then ival is used to initialize the share values.
            ival should be a share initializer:
               valid initializers are:
                   a dict of fields and values
                   a list of duples, each a (key, value) item

            If own is True then .update(ival) is used
            Otherwise .create(ival) is used

        Requires that:
           self.store exist

           The following have already been resolved:
               self.frame
               self.frame.framer
               self.frame.framer.main
               self.frame.framer.main.framer

           If actor relative addressing is used then:
              self.actor is resolved
              self.actor.name is not empty

        Any actor could have ioinits saved for them in their ._act  Act
        If ionits exist then then an inode should be part of the ioinits
        Currently only the Do verb actors have ioinits. The inode is one of them.
        The ioinits come from two sources. The registry and the do verb per and for
        clauses

        _act.ioinits are the do and per clauses
        registry ioints are from the Actor.Ionints class variable

        So the .inode attribute indicates if the ipath being resolved is for
        an ioinit or not.  If .inode is None it is not for an ioinit.
        Otherwise even if .inode is "" then ipath comes from ioinit and
        path resolution should handle inode logic.

        This would puts all the framer inode prepend
        logic in one place and make it easier to climb the  frame and aux outline
        """
        if not (isinstance(ipath, storing.Share) or isinstance(ipath, storing.Node)): # must be pathname
            parts = ipath.split('.') if ipath else []  # [] if ipath is empty
            noded = True if not parts else False  # return node path prefix context since empty ipath
            if not parts or parts and parts[0]:  # empty or not empty and not absolute so do relative substitutions
                if not self.frame:
                    raise excepting.ResolveError("ResolveError: Missing frame context"
                                             " to resolve relative pathname.", ipath, self,
                                             self.human, self.count)
                if not self.frame.framer:
                    raise excepting.ResolveError("ResolveError: Missing framer context"
                                                 " to resolve relative pathname.", ipath, self.frame,
                                                 self.human, self.count)

                framer = self.frame.framer
                fparts = framer.inode.rstrip(".").split(".") if framer.inode else []
                main = framer.main  # main frame
                mainer = main.framer if main else None  # main frame's framer
                # if mainer and not (absolute or framer relative)
                # then fromer is aux framer so walk up mains processing inodes
                # need to do this first because used by both inode and ipath logic below
                while mainer and (not fparts or fparts[0] not in ("", "framer")):
                    # four aux inode cases:
                    # absolute: fparts[0] = "",
                    # framer relative: fparts[0] == "framer",
                    # empty: fparts == [],
                    # me relative: fparts[0] == "me",
                    # relative: otherwise

                    if fparts and fparts[0] == "me":
                        del fparts[0]  # me relative
                    else: # process over frame via inode
                        while main and (not fparts or fparts[0] not in ("", "framer")):
                            if main.inode:
                                fparts = main.inode.rstrip(".").split(".") + fparts  # prepend
                                if fparts and fparts[0] == "me":  # me relative
                                    del fparts[0]
                                    break  # skip any further over frames to main frame
                            main = main.over  # walk up to over frame if any
                        if fparts and fparts[0] in ("", "framer"):
                            break

                    if mainer.inode:
                        fparts = mainer.inode.rstrip(".").split(".") + fparts  # prepend
                    main = mainer.main  # main framer's main frame walk up one level
                    mainer = main.framer if main else None  # walk up one level

                if fparts and fparts[0] == "me" :
                    del fparts[0]  # me not allowed as initial inode

                # "" == ".".join([]) == ".".join([""])

                # over frame inode processing
                frame = self.frame # start at current frame
                oparts = frame.inode.rstrip(".").split(".") if frame.inode else []
                while frame and (not oparts or oparts[0] not in ("", "framer")):
                    if oparts and oparts[0] == "me":  # me relative
                        del oparts[0]
                        break  # skip any further over frames
                    frame = frame.over
                    if frame and frame.inode:
                        oparts = frame.inode.rstrip(".").split(".") + oparts

                # already know from above parts not absolute
                if (self.inode is not None and (not parts or
                        parts[0] not in ("framer", "me"))):
                    # prepend act .inode logic
                    iparts = self.inode.rstrip(".").split(".") if self.inode else []
                    if not iparts and not oparts and not fparts:  # use default inode
                        iparts = "framer.me.frame.me.actor.me".split(".")
                    parts = iparts + parts  # prepend inode parts

                if not parts or parts[0] not in ("", "framer"):  # not absolute or framer relative
                    if parts and parts[0] == 'me':  # skip frame.inode processing
                        del parts[0]  # parts could be empty now
                    else:  # prepend over frame inodes
                        parts = oparts + parts
                    if not parts or parts[0] not in ("", "framer"):
                        parts = fparts + parts  # prepend fparts framer inodes

            if parts and parts[0]:  # not absolute so do relative substitutions
                if parts[0] == 'framer':  #  framer relative addressing
                    if parts[1] == 'me': # current framer
                        parts[1] = self.frame.framer.name
                    elif parts[1] == 'main': # current main framer
                        if not self.frame.framer.main:
                            raise excepting.ResolveError("ResolveError: Missing main framer"
                                " context to resolve relative pathname.", ipath,
                                self.frame.framer,
                                self.human, self.count)
                        parts[1] = self.frame.framer.main.framer.name

                    if (len(parts) >= 3):
                        if parts[2] == 'frame':
                            if parts[3] == 'me':
                                parts[3] = self.frame.name
                            elif parts[3] == 'main':
                                if not self.frame.framer.main:
                                    raise excepting.ResolveError("ResolveError: "
                                        "Missing main frame context to resolve "
                                        "relative pathname.", ipath,
                                        self.frame.framer,
                                        self.human, self.count)
                                parts[3] = self.frame.framer.main.name
                            if (len(parts) >= 5 ) and parts[4] == 'actor':
                                if parts[5] == 'me': # slice insert multiple parts
                                    if (not isinstance(self.actor, Actor)
                                            or not self.actor.name): # unresolved actor
                                        raise excepting.ResolveError("ResolveError: Unresolved actor"
                                            " context to resolve relative pathname.", ipath, self,
                                                        self.human, self.count)
                                    parts[5:6] = nameToPath(self.actor.name).lstrip('.').rstrip('.').split('.')
                        elif parts[2] == 'actor':
                            if parts[3] == 'me': # slice insert multiple parts
                                if (not isinstance(self.actor, Actor)
                                        or not self.actor.name):
                                    raise excepting.ResolveError("ResolveError: Unresolved actor"
                                        " context to resolve relative pathname.", ipath, self,
                                               self.human, self.count)
                                parts[3:4] = nameToPath(self.actor.name).lstrip('.').rstrip('.').split('.')

            ipath = '.'.join(parts)

            if noded and ipath and not ipath.endswith("."):
                ipath = "{0}.".format(ipath)

            if not self.frame.store:
                raise excepting.ResolveError("ResolveError: Missing store context"
                                " to resolve relative pathname.", ipath, self,
                                self.human, self.count)

            if ipath.endswith('.'): # Node not Share
                ipath = self.frame.store.createNode(ipath.rstrip('.'))
                if warn:
                    console.profuse( "     Warning: Non-existent node '{0}' "
                                        "... creating anyway\n".format(ipath))
            else: # Share
                ipath = self.frame.store.create(ipath)
                if ival is not None:
                    if iown:
                        ipath.update(ival)
                    else:
                        ipath.create(ival)
                if warn:
                    console.profuse( "     Warning: Non-existent node '{0}' "
                                     "... creating anyway\n".format(ipath))

        return ipath

    def _prepareSrcFields(self, src, fields):
        """
        Prepares and verifys list field names fields in share src
           handles default conditions when fields is empty

           src is share
           fields is list of field names

        """
        if not fields: # empty source fields so assign defaults
            if src:
                if 'value' in src:
                    fields = ['value'] #use value field
                else: #use pre-existing source fields
                    fields = src.keys()
            else: # empty src
                fields = ['value'] #use value field
        return fields

class Nact(Act):
    """ Negating Act used for actor needs to give Not Need
    """
    __slots__ = ('frame', 'context', 'act',
                 'actor', 'registrar', 'parms', 'inits', 'ioinits',
                 'human', 'count')

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
            self.actor._expose()

class SideAct(Act):
    """ Anciliary act to a main Act/Actor used to call a different 'action' method
        of the Main act.actor in support of combined activity such as restarting
        an action.

        SideActs are created in the .resolve method of an Actor and assume that
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
            raise excepting.ResolveError(msg,
                                         self.action,
                                         self,
                                         self.human,
                                         self.count)

        if not getattr(self.actor, self.action, None):
            msg = "ResolveError: Missing action in actor"
            raise excepting.ResolveError(msg,
                                         self.action,
                                         self,
                                         self.human,
                                         self.count)

def actify(name, base=None, registry=None, inits=None, ioinits=None, parms=None,
             parametric=None):
    """ Parametrized decorator function that converts the decorated function
        into an Actor sub class with .action method and with class name that
        is name and registers the new subclass in the registry under name as
        a subclass of base. The default base is Actor.

        The parameters  registry, parametric, inits, ioinits, and parms if provided,
        are used to create the class attributes for the new subclass

    """
    base = base or Actor
    if not issubclass(base, Actor):
        msg = "Base class '{0}' not subclass of Actor".format(base)
        raise excepting.RegisterError(msg)

    attrs = odict()
    if registry:
        attrs['Registry'] = odict()
    if parametric is not None:
        attrs['_Parametric'] = True if parametric else False
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

actorify = actify  # alias for backwards compatibility

@metaclassify(registering.RegisterType) # python2or3 compatible
class Actor(object):
    """ Actor Base Class
        Has Actor specific Registry of classes
    """
    Registry = odict() # Actor Registry
    Inits = odict() # class defaults support for
    Ioinits = odict() # class defaults
    Parms = odict() # class defaults
    _Parametric = True # Convert iois to action method parameters if Truthy
    __slots__ = ('name', 'store', '_act')

    def __init__(self, name='', store=None, act=None, **kwa ):
        """
        Initialization method for instance.

        Instance attributes
            .name = name string for Actor variant in class Registry
            .store = reference to shared data Store
            ._act = reference to containing Act

        If subclass has init need to call super
        super(SubClassName, self).__init__(**kwa)

        """
        self.name = name
        if store is not None:
            if  not isinstance(store, storing.Store):
                raise ValueError("Not store {0}".format(store))
            self.store = store
        self._act = act


    def __call__(self, **kwa):
        """ run .action  """
        return self.action(**kwa)

    def action(self, **kwa):
        """Action called by Actor. Should override in subclass."""
        console.profuse("Actioning {0} in {1} of {2} with {3}\n".format(self.name,
                                                                        self._act.frame.name,
                                                                        self._act.frame.framer.name,
                                                                        str(kwa)))
        pass

    def _expose(self):
        """Show Actor."""
        console.terse("Actor {0}".format(self.name))

    def _resolve(self, **kwa):
        """ Return updated parms
            Extend in subclass to resolve specific kwa items that are links or
            share refs and update parms
        """
        parms = odict()

        return parms

    def _initio(self, ioinits):
        """
        Compute initializations for ioflo shares from ioinits odict or item list
        The 'inode' item in ioinits is special. Act.resolve extracts 'inode' from
        ioinits and assigns to ._act.inode before ._initio is called.

        This implements a generic Actor interface protocol for associating the
        io data flow shares to the Actor.

        The ._act.inode attribute holds the pathname string of the default
        data store node where shares associated with the Actor instance may
        be placed when relative addressing is used.
        It is also the default data store context
        for share references by Doer iois. The inode on an actor my be set
        explicitly in the Ioinit class variable or in the actify (doify) decorator
        or by the via clause of a Doer

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

        For each ioinits item (key, val) besides the inode
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
        ioinits = odict(ioinits)  # make copy also allows for item list as parameter
        #inode = ioinits.get('inode', '')

        #if inode and not inode.endswith('.'):  # ensure is a node not share path
            #inode = "{0}.".format(inode)

        if self._act.inode is None:  # inode may not be None if ioinits
            self._act.inode = ""

        iois = odict()
        ioi = odict(ipath=self._act.inode)  # create ioi for the inode
        iois['inode'] = ioi  # inode path resolves so actor has reference to its own inode
        for key, val in ioinits.items():  # assumes keys are basestrings
            if key == 'inode':  # skip inode
                continue

            if val is None:  # use default assume no way to be inadvertent
                val = ""  # empty string for val defaults ipath to same as key

            if isinstance(val, basestring):
                ipath = val
                iown = None
                ival = odict() # effectively will not change share
            elif isinstance(val, Mapping): # dictionary
                ipath = val.get('ipath', '')
                iown = val.get('iown')

                if not 'ival' in val:
                    ival = odict() # effectively will not change share
                else:
                    ival = val['ival']
                    if isinstance(ival, Mapping):
                        if not ival: #empty mapping
                            ival = odict(value=copy.copy(ival)) #make copy so each instance unique
                        # otherwise don't change since ival is non-empty mapping
                    elif nonStringIterable(ival): # not mapping and nonStringIterable
                        ival = odict(value=copy.copy(ival))
                    else:
                        ival = odict(value=ival)
            else:
                raise ValueError("Bad ioinit for key '{0}' with value '{1}'".format(key, val))

            # inode is prepended in act.resolvePath

            if not ipath:
                ipath = key  # when ipath empty create default from key

            ioi = odict(ipath=ipath, ival=ival, iown=iown)
            iois[key] = ioi

        return iois  # inode prepended in act.resolvePath

    def _prepare(self, **kwa):
        """ Base method to be overriden in sub classes. Perform post initio setup
            after all parms and ioi parms or attributes have been created
            kwa usually parms.

            If one is using this method consider refactoring into two different
            behaviors
        """
        pass

    def _resolvePath(self, ipath, ival=None, iown=None, warn=False):
        """ Returns resolved Share or Node instance from ipath
            Calls self._act.resolvePath()
            See doc string from Act.resolvePath for detailed description of
            functionality

            Requires that
               self._act exist
        """
        if not (isinstance(ipath, storing.Share) or isinstance(ipath, storing.Node)): # must be pathname
            if not self._act:
                raise excepting.ResolveError("ResolveError: Missing act context"
                        " to resolve relative pathname.", ipath, self,
                        self._act.human, self._act.count)
            ipath = self._act.resolvePath(ipath=ipath,
                                          ival=ival,
                                          iown=iown,
                                          warn=warn)

        return ipath

    def _prepareDstFields(self, srcFields, dst, dstFields):
        """
        Prepares  for a transfer of data
           from srcFields
           to dstFields in dst
        Handles default conditions when fields are empty
            srcFields is list of field names
            dst is share
            dstFields is list of field names

        Ensure Builder.prepareDataDstFields is similar
        """
        if not dstFields: #no destinationField so use default rules
            if 'value' in dst:
                dstFields = ['value'] #use value field

            else: #use srcFields
                dstFields = srcFields

        self._verifyShareFields(dst, dstFields)

        if len(srcFields) != len(dstFields):
            msg = ("ResolveError: Unequal number of source = {0} and "
                   "destination = {2} fields".format(srcFields, dstFields))
            raise excepting.ResolveError(msg,
                                         self.name,
                                         '',
                                         self._act.human,
                                         self._act.count)

        for dstField, srcField in izip(dstFields, srcFields):
            if (dstField != srcField) and (srcField != 'value'):
                console.profuse("     Warning: Field names mismatch. '{0}' in {1} "
                                "from '{2}' ... creating anyway".format(
                                  dstField, dst.name, srcField))

        #create any non existent destination fields
        for field in dstFields: #use destination fields for destination data
            if field not in dst:
                console.profuse("     Warning: Transfer into non-existent field '{0}' in "
                       "share {1} ... creating anyway\n".format(field, dst.name))
                dst[field] = None #create

        return dstFields

    def _prepareSrcDstFields(self, src, srcFields, dst, dstFields):
        """
        Prepares and verifys a transfer of data
           from srcFields in src
           to dstFields in dst
        Handles default conditions when fields are empty
           src and dst are shares
           srcFields and dstFields are lists

        Ensure Builder.prepareSrcDstFields is the same
        """
        if not srcFields: # empty source fields so assign defaults
            if src:
                if 'value' in src:
                    srcFields = ['value'] #use value field
                elif dstFields: #use destination fields for source fields
                    srcFields = dstFields
                else: #use pre-existing source fields
                    srcFields = src.keys()
            else: # empty src
                srcFields = ['value'] #use value field

        self._verifyShareFields(src, srcFields)

        if not dstFields: #no destination fields so assign defaults
            if 'value' in dst:
                dstFields = ['value'] #use value field
            else: #use source fields for destination fields
                dstFields = srcFields

        self._verifyShareFields(dst, dstFields)

        if len(srcFields) != len(dstFields):
            msg = ("ResolveError: Unequal number of fields, source = {0} and"
                  " destination={1)".format(srcFields, dstFields))
            raise excepting.ResolveError(msg,
                                         self.name,
                                         '',
                                         self._act.human,
                                         self._act.count)

        for dstField, srcField in izip(dstFields, srcFields):
            if (dstField != srcField) and (srcField != 'value'):
                console.profuse("     Warning: Field names mismatch. '{0}' in {1} "
                                "from '{2}' in {3}  ... creating anyway".format(
                                    dstField, dst.name, srcField, src.name))

        #create any non existent source or destination fields
        for field in srcFields: #use source fields for source data
            if field not in src:
                console.profuse("     Warning: Transfer from non-existent field '{0}' "
                        "in share {1} ... creating anyway".format(field, src.name))
                src[field] = None #create

        for field in dstFields: #use destination fields for destination data
            if field not in dst:
                console.profuse("     Warning: Transfer into non-existent field '{0}' "
                        "in share {1} ... creating anyway\n".format(field, dst.name))
                dst[field] = None #create

        return (srcFields, dstFields)

    def _verifyShareFields(self, share, fields):
        """
        Verify that updating fields in share won't violate the
           condition that when a share has field == 'value'
           it will be the only field

           fields is list of field names
           share is  share

        Raises exception if condition would be violated

        Ensure Builder.verifyShareFields is same
        """
        if (len(fields) > 1) and ('value' in fields):
            msg = "ResolveError: Field = 'value' within fields = '{0}'".format(fields)
            raise excepting.ResolveError(msg,
                                         self.name,
                                         '',
                                         self._act.human,
                                         self._act.count)

        if share: #does share have fields already
            for field in fields:
                if field not in share: #so this field could be added to share
                    if ('value' in share) or (field == 'value'):
                        msg = ("ResolveError: Candidate field '{0}' when "
                               "fields = '{1}' exist".format(field, share.keys()))
                        raise excepting.ResolveError(msg,
                                                     self.name,
                                                     '',
                                                     self._act.human,
                                                     self._act.count)

class Interrupter(Actor):
    """
    Interrupter Actor Class
    Interrupter is a base clase for all actor classes that interrupt normal precur
    processing and result in a change in the frame or the frame processing.

    This class must be subclassed. This is a convenience so can either use
      isinstance to test

    Specifically an Interrupter's action() method returns truthy when its action
    interrupts the normal frame processing.

    Examples are:
    Transiters which interrupt by changing to a new frame
    Suspenders which interrupt when the conditional aux condition is true and
       further processing of the frame and sub frames is stopped
    """
    def __init__(self,**kw ):
        """
        Initialization method for instance.

        Inherited Attributes:
            .name = name string for Actor variant in class Registry
            .store = reference to shared data Store
            ._act = reference to containing Act

        Attributes:
            ._tracts = list of references to transition acts for this Actor
                transit sub-context of precur context during segue

        """
        super(Interrupter,self).__init__(**kw)
        self._tracts = []

class Transiter(Interrupter):
    """Transiter Interrupter Class
       Transiter  is a special actor that performs transitions between frames

       Parameters
            needs = list of Act objects that are exit needs for this trans
            near = source frame of trans
            far = target frame of trans
            human = text version of transition

    """
    def _resolve(self, needs, near, far, human, **kwa):
        """Resolve any links in far and in associated parms for actors"""

        parms = super(Transiter, self)._resolve( **kwa)

        if near == 'me':
            near = self._act.frame

        parms['near'] = near = framing.resolveFrame(near,
                                                    who=self.name,
                                                    desc='near',
                                                    human=self._act.human,
                                                    count=self._act.count)


        if far == 'next':
            if not isinstance(near.next_, framing.Frame):
                raise excepting.ResolveError("ResolveError: Bad next frame",
                                             near.name, near.next_,
                                             self._act.human, self._act.count)
            far = near.next_

        elif far == 'me':
            far = near

        far = framing.resolveFrame(far,
                                   who=self.name,
                                   desc='far',
                                   human=self._act.human,
                                   count=self._act.count)

        parms['far'] = far

        for act in needs:
            act.act = self._act  # so act.resolve can ref self._act.frame.framer
            act.resolve()
            self._tracts.extend(act.actor._tracts)
            del act.actor._tracts[:]

        return parms


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
        exits, enters, reexens = framing.Framer.ExEn(framer.actives, far)

        #check enters, if successful, perform transition
        if not framer.checkEnter(enters, exits):
            return None

        msg = "To: {0}<{1} at {2} Via: {3} ({4}) From: {5} after {6:0.3f}\n".format(
            framer.name, far.human, round(framer.store.stamp, 6), near.name, human,
            framer.human, framer.elapsed)
        console.terse(msg)

        console.profuse("     exits: {0}\n".format([frame.name for frame in exits]))
        console.profuse("     enters: {0}\n".format([frame.name for frame in enters]))
        console.profuse("     reexens: {0}\n".format([frame.name for frame in reexens]))

        for act in self._tracts:  # transit sub-context of segue precur
            act()

        framer.exit(exits) #exit uncommon frames in near outline reversed in place
        framer.rexit(reexens[:]) #make copy since reversed in place
        framer.renter(reexens)
        framer.enter(enters)
        framer.activate(active = far)
        return far

    def _expose(self):
        """      """
        console.terse("Transiter {0}\n".format(self.name))


class Suspender(Interrupter):
    """Suspender Interrupter Class
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

    def _resolve(self, needs, main, aux, human, **kwa):
        """Resolve any links aux and in associated parms for actors"""
        parms = super(Suspender, self)._resolve( **kwa)

        if main == 'me':
            main = self._act.frame

        parms['main'] = main = framing.resolveFrame(main,
                                                    who=main,
                                                    desc='main',
                                                    human=self._act.human,
                                                    count=self._act.count)

        parms['aux'] = aux = framing.resolveFramer(aux,
                                                   who=main.name,
                                                   desc='aux',
                                                   contexts=[AUX],
                                                   human=self._act.human,
                                                   count=self._act.count)

        for act in needs:
            act.act = self._act
            act.resolve()
            self._tracts.extend(act.actor._tracts)
            del act.actor._tracts[:]

        deActParms = odict(aux=aux)
        deAct = SideAct( actor=self,
                        parms=deActParms,
                        action='deactivize',
                        human=self._act.human,
                        count=self._act.count)
        self._act.frame.addExact(deAct)
        console.profuse("{0}Added exact {1} SideAct for {2} with {3} in {4}\n".format(
                INDENT_ADD, 'deactivize', self.name, deAct.parms, self._act.frame.name))
        deAct.resolve()

        return parms

    def action(self, needs, main, aux, human, **kw):
        """Action called by Actor  """

        framer = main.framer #to speed up

        if aux.done: #not active

            console.profuse("Attempt segue from {0} to aux {1}\n".format(main.name, aux.name))

            for act in needs:
                if not act(): #return None if not all true
                    return None

            #if aux.main: #see if aux still belongs to another frame
            #    return None

            # if aux.main is not None then it has not been released and so
            # we can't enter unless it is our act's frame
            if aux.main and (aux.main is not self._act.frame):
                console.concise("    Invalid aux '{0}' in use by another frame"
                        " '{1}'\n".format(aux.name, aux.main.name))
                return None

            if not aux.checkStart(): #performs entry checks
                return None

            msg = "To: {0} in {1}<{2} at {3} Via: {4} ({5}) From: {6} after {7:0.3f}\n".format(
                aux.name, framer.name, main.headHuman, round(framer.store.stamp, 6), main.name,
                human, framer.human, framer.elapsed)
            console.terse(msg)

            for act in self._tracts:  # transit sub-context of cond aux segue precur
                act()

            if aux.original:
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


    def _expose(self):
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
        if aux.original:
            aux.main = None



class Printer(Actor):
    """Printor Actor Class

       Printer is a special actor that just prints to console its message

    """
    def action(self, message, **kw):
        """Action called by Actor
        """
        #console.terse("{0} printer {1}\n".format(self.name, message))
        console.terse("*** {0} ***\n".format(message))

    def _expose(self):
        """   """
        console.terse("Printer {0}\n".format(self.name))

class Marker(Actor):
    """ Base class that sets up mark in provided share reference"""
    pass

class MarkerUpdate(Marker):
    """ MarkerUpdate Class

        MarkerUpdate is a special actor that acts on a share to mark the update by
            saving a copy of the last stamp

        MarkerUpdate works with NeedUpdate which does the comparison against the marked stamp.

        Builder at parse time when it encounters an NeedUpdate,
        creates the mark in the share and creates the appropriate MarkerUpdate
    """
    def action(self, share, marker, **kwa):
        """ Update mark in share
            Where share is reference to share and marker is unique name key of mark in
                share.marks odict
            Updates mark.stamp

            only one mark per marker per share is needed
        """
        console.profuse("{0} mark {1} in {2} on {3}\n".format(
            self.name, share.name, marker, 'update' ))

        mark = share.marks.get(marker)
        if mark:
            mark.stamp = self.store.stamp  # update stamp when marker runs
            if self._act.context == ActionSubContextNames[TRANSIT]:  # transit satisfied
                mark.used = mark.stamp

    def _expose(self):
        """   """
        console.terse("MarkerUpdate {0}\n".format(self.name))

class MarkerChange(Marker):
    """ MarkerChange Class

        MarkerChange is a special actor that acts on a share to mark save a copy
        of the data in the mark for the share.

        MarkerChange works with NeedChange which does the comparison with the mark

        Builder at parse time when it encounters a NeedChange,
        creates the mark in the share and creates the appropriate marker
    """
    def action(self, share, marker, **kwa):
        """ Update mark in share
            Where share is reference to share and marker is unique name key of mark in
                share.marks odict
            Updates mark.data

            only one mark per marker per share is needed
        """
        console.profuse("{0} mark {1} in {2} on {3}\n".format(
            self.name, share.name, marker, 'change' ))

        mark = share.marks.get(marker)
        if mark:
            mark.data = storing.Data(share.items())  # set date when marker runs

    def _expose(self):
        """   """
        console.terse("MarkerChange {0}\n".format(self.name))

class Rearer(Actor):
    """
    Rearer Actor Class
    Rearer is a special actor that clones a moot framer at runtime

       Parameters
            original = moot framer to be cloned
            clone = name of clone
            schedule = schedule kind of clone
            frame = frame to put auxiliary clone in

    """
    def _resolve(self, original, clone, schedule, frame, **kwa):
        """
        Resolve any links
        """
        parms = super(Rearer, self)._resolve( **kwa)

        parms['original'] = original = framing.resolveFramer(original,
                                                    who=self.name,
                                                    desc='original',
                                                    contexts=[MOOT],
                                                    human=self._act.human,
                                                    count=self._act.count)

        if schedule not in [AUX]:
            msg = ("ResolveError: Invalid schedule '{0}' for clone"
                  "of '{1}'".format(ScheduleNames.get(schedule, schedule),
                                  original.name))
            raise excepting.ResolveError(msg=msg,
                                         name=self.name,
                                         value=schedule,
                                         human=self._act.human,
                                         count=self._act.count)

        if schedule == AUX:  # only current framer
            parms['framer'] = framer = framing.resolveFramer(self._act.frame.framer,
                                            who=self._act.frame.name,
                                            desc='rear aux clone',
                                            contexts=[],
                                            human=self._act.human,
                                            count=self._act.count)

            if frame == 'me':  # cannot rear in current frame
                msg = ("ResolveError: Invalid frame 'me' for reared clone.")
                raise excepting.ResolveError(msg,
                                             name=clone,
                                             value=self.name,
                                             human=self._act.human,
                                             count=self._act.count)

            # frame required
            parms['frame'] = frame = framing.resolveFrameOfFramer(frame,
                                                                  framer,
                                                                  who=self._act.frame.name,
                                                                  desc='rear aux clone',
                                                                  human=self._act.human,
                                                                  count=self._act.count)

            if clone != 'mine':
                msg = "ResolveError: Aux insular clone name must be 'mine' not '{0}'".format(clone)
                raise excepting.ResolveError(msg,
                                             name=clone,
                                             value=self.name,
                                             human=self._act.human,
                                             count=self._act.count)

        else:
            msg = ("ResolveError: Invalid insular clone schedule '{0}' "
                                               "for {1}.".format(schedule, original))
            raise excepting.ResolveError(msg,
                                         name=clone,
                                         value=self.name,
                                         human=self._act.human,
                                         count=self._act.count)

        return parms

    def action(self, original, clone, schedule, frame, framer, **kw):
        """
        Action called by Actor

        Parameters:
           original is resolved original moot framer to be cloned
           clone is clone tag (not used currently)
           schedule is clone schedule
           frame is resolved frame for reared clone
           framer is resolved framer for frame for reared clone

        """

        console.profuse("         Cloning '{0}' as '{1}' be '{2}'\n".format(
                original.name, clone, ScheduleNames.get(schedule, schedule)))

        if schedule == AUX:
            if frame in self._act.frame.outline:
                console.terse("         Error: Cannot rear clone in own"
                              " '{0}' outline. {1} in line {2}\n".format(frame.name,
                                                                         self._act.human,
                                                                         self._act.count))
                return

            tag = framer.newAuxTag(base=original.tag)
            name = "_".join((framer.surname, tag))  # replace name with full name
            console.terse("         Rearing original '{0}' as aux insular clone"
                          " '{1}' in Frame '{2}' in Framer '{3}'"
                          "\n".format(original.name,
                                        name,
                                        frame.name,
                                        framer.name))
            clone = original.clone(name=name, tag=tag, schedule=schedule)
            clone.original = False  # main frame will be fixed
            clone.insular = True  #  local to this framer
            clone.razeable = True  # can be razed
            framer.auxes[tag] = clone
            frame.addAux(clone)
            clone.main = frame
            #self._act.frame.framer.assignFrameRegistry()  # setup for resolution
            self.store.house.presolvables.append(clone)
            self.store.house.presolvePresolvables()
            self.store.house.resolveResolvables()


class Razer(Actor):
    """
    Razer Actor Class
    Razer is a special actor that destroys a  framer clone at runtime

       Parameters
            who = auxiliary clones to be destroyed
            frame = frame holding clones to be destroyed

    """
    def _resolve(self, who, frame, **kwa):
        """
        Resolve any links
        """
        parms = super(Razer, self)._resolve( **kwa)


        parms['framer'] = framer = framing.resolveFramer(self._act.frame.framer,
                                        who=self._act.frame.name,
                                        desc='rear aux clone',
                                        contexts=[],
                                        human=self._act.human,
                                        count=self._act.count)

        if frame == 'me':  # cannot rear in current frame
            frame = self._act.frame

        # frame required
        parms['frame'] = frame = framing.resolveFrameOfFramer(frame,
                                                              framer,
                                                              who=self._act.frame.name,
                                                              desc='rear aux clone',
                                                              human=self._act.human,
                                                              count=self._act.count)

        return parms

    def action(self, who, frame, framer, **kw):
        """
        Action called by Actor

        Parameters:
           who is string describing which aux(es) to raze
           frame is frame with auxes to raze
           framer is framer of frame with auxes to raze
        """

        razeables = []
        if who == 'all':
            for aux in frame.auxes:
                if aux.insular and aux.razeable:
                    razeables.append(aux)

        elif who == 'first':
            for aux in frame.auxes:  # works even if .auxes empty
                if aux.insular and aux.razeable:
                    razeables.append(aux)
                    break

        elif who == 'last':  # works even if .auxes empty
            for aux in reversed(frame.auxes):
                if aux.insular and aux.razeable:
                    razeables.append(aux)
                    break

        for aux in razeables:
            console.concise("         Razing '{0}' in '{1}'\n".format(who, frame.name))
            aux.prune()
            frame.auxes.remove(aux)
            if aux.tag in framer.auxes:
                del framer.auxes[aux.tag]
