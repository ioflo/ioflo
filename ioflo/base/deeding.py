"""deeding.py deed module


"""
#print("module {0}".format(__name__))

import time
import struct
from collections import deque, Mapping
from functools import wraps
import inspect
import copy

from .globaling import *
from .odicting import odict
from . import aiding
from . import excepting
from . import registering
from . import storing
from . import acting

from .consoling import getConsole
console = getConsole()

from .aiding import nonStringIterable, just, nameToPath

def deedify(name, base=None, registry=None, inits=None, ioinits=None, parms=None,
            parametric=None):
    """ Parametrized decorator function that converts the decorated function
        into an Actor sub class with .action method and with class name name
        and registers the new subclass in the registry under name.
        If base is not provided then use Deed

        The parameters  registry, parametric, inits, ioinits, and parms if provided,
        are used to create the class attributes for the new subclass

    """
    base = base or Deed
    if not issubclass(base, Deed):
        msg = "Base class '{0}' not subclass of Deed".format(base)
        raise excepting.RegisterError(msg)

    #name = aiding.reverseCamel(name, lower=False)

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

class Deed(acting.Actor):
    """ Provides object of 'do' command verb
        Base class has Deed specific Registry of Classes

         deeds are natively recur actions
        Deeds default to converting iois into attributes
    """
    Registry = odict()
    _Parametric = False # convert iois into attributes

class DeedParam(Deed):
    """ Iois are converted to parms not attributes """
    _Parametric = True # convert iois into parms

class DeedSince(Deed):
    """ DeedSince
        Generic Super Class acts if input updated Since last time ran
        knows time of current iteration and last time processed input

        Should be subclassed

        unique attributes
            .stamp = current time of deed evaluation in seconds

    """
    def __init__(self, **kw):
        """Initialize Instance """
        super(DeedSince,self).__init__( **kw)
        self.stamp = None

    def action(self, **kw):
        """Should call this on superclass  as first step of subclass action method  """
        console.profuse("Actioning DeedSince  {0}\n".format(self.name))
        self.stamp = self.store.stamp

    def _expose(self):
        """     """
        print("Deed %s stamp = %s" % (self.name, self.stamp))

class DeedLapse(Deed):
    """ DeedLapse
        Generic base class for Deeds that need to
        keep track of lapsed time between iterations.
        Should be subclassed

        unique attributes
            .stamp =  current time deed evaluation in seconds
            .lapse = elapsed time betweeen evaluations of a behavior

       has restart method when resuming after noncontiguous time interruption
       builder creates implicit entry action of restarter for deed
    """
    def __init__(self, **kwa):
        """Initialize Instance """
        super(DeedLapse,self).__init__( **kwa)

        self.stamp = None
        self.lapse = 0.0 #elapsed time in seconds between updates calculated on update

    def restart(self):
        """ Restart Deed
            Override in subclass
            This is called by restarter action in enter context
        """
        console.profuse("Restarting DeedLapse  {0}\n".format(self.name))

    def updateLapse(self):
        """Calculates a new time lapse based on stamp or if stamp is None then use store stamp
           updates .stamp
        """
        stampLast, self.stamp = self.stamp, self.store.stamp

        #lapse must not be negative
        try:
            self.lapse = max( 0.0, self.stamp - stampLast) #compute lapse

        except TypeError: #either/both self.store.stamp or self.stamp is not a number
            #So if store is number then makes stamp number so next time lapse is non zero
            #If store.stamp is not a number then lapse will always be zero
            self.stamp = self.store.stamp #so make stamp same as store
            self.lapse = 0.0

    def action(self, **kwa):
        """    """
        console.profuse("Actioning DeedLapse  {0}\n".format(self.name))
        self.updateLapse()

    def _expose(self):
        """     """
        print("Deed %s stamp = %s lapse = %s" % (self.name, self.stamp, self.lapse))

    def _resolve(self, **kwa):
        """ Create enact with restart SideAct to restart this Actor """
        parms = super(DeedLapse, self)._resolve( **kwa)

        restartActParms = {}
        restartAct = acting.SideAct(   actor=self,
                                parms=restartActParms,
                                action='restart',
                                human=self._act.human,
                                count=self._act.count)
        # need to insert restartAct before self._act so restartAct runs first
        found = False
        for i, enact in enumerate(self._act.frame.enacts):
            if enact is self._act:
                found = True
                self._act.frame.insertEnact(restartAct, i)
                break
        if not found:
            self._act.frame.addEnact(restartAct)

        console.profuse("{0}Added enact {1} SideAct for {2} with {3} in {4}\n".format(
                INDENT_ADD, 'restart', self.name, restartAct.parms, self._act.frame.name))
        restartAct.resolve()
        return parms
