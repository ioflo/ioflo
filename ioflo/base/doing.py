"""
doing.py doer module for do verb behaviors
"""
import time
import struct
from collections import deque, Mapping
from functools import wraps
import inspect
import copy

from ..aid.sixing import *
from .globaling import INDENT_ADD
from ..aid.odicting import odict
from ..aid import aiding
from . import excepting
from . import registering
from . import storing
from . import acting

from ..aid.consoling import getConsole
console = getConsole()

from ..aid.classing import nonStringIterable
from ..aid.aiding import  just, nameToPath

def doify(name,
          base=None,
          registry=None,
          parametric=None,
          inits=None,
          ioinits=None,
          parms=None):
    """ Parametrized decorator function that converts the decorated function
        into an Actor sub class with .action method and with class name name
        and registers the new subclass in the registry under name.
        If base is provided then register as subclass of base.
        Default base is Doer

        The parameters registry, parametric, inits, ioinits, and parms if provided,
        are used to create the class attributes for the new subclass
    """
    base = base or Doer
    if not issubclass(base, Doer):
        msg = "Base class '{0}' not subclass of Doer".format(base)
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

class Doer(acting.Actor):
    """
    Provides object of 'do' command verb
    The Doer's action method is the 'deed'
    Base class has Doer specific Registry of Classes
    Doer instance native actions context is recur
    Doer defaults to converting iois into attributes
    """
    Registry = odict()  # create doer specific register
    _Parametric = False # convert iois into attributes

class DoerParam(Doer):
    """
    Iois are converted to parms not attributes
    """
    _Parametric = True # convert iois into parms

class DoerSince(Doer):
    """
    Generic Super Class acts if input updated Since last time ran
    knows time of current iteration and last time processed input

    Should be subclassed

    Attributes
        .stamp = current time of doer evaluation in seconds

    """
    def __init__(self, **kw):
        """Initialize Instance """
        super(DoerSince,self).__init__( **kw)
        self.stamp = None

    def action(self, **kw):
        """Should call this on superclass  as first step of subclass action method  """
        console.profuse("Actioning DoerSince  {0}\n".format(self.name))
        self.stamp = self.store.stamp

    def _expose(self):
        """     """
        print("Doer %s stamp = %s" % (self.name, self.stamp))

class DoerLapse(Doer):
    """
    Generic base class for Doers that need to
    keep track of lapsed time between iterations.
    Should be subclassed

    Attributes
        .stamp =  current time stamp of doer evaluation in seconds
        .lapse = elapsed time betweeen current and previous evaluation

    has restart method when resuming after noncontiguous time interruption
    builder creates implicit entry action of restarter for Doer
    """
    def __init__(self, **kwa):
        """Initialize Instance """
        super(DoerLapse,self).__init__( **kwa)

        self.stamp = None
        self.lapse = 0.0 #elapsed time in seconds between updates calculated on update

    def restart(self):
        """
        Restart Doer
        Override in subclass
        This is called by restarter action in enter context
        """
        console.profuse("Restarting DoerLapse  {0}\n".format(self.name))

    def updateLapse(self):
        """
        Calculates a new time lapse based on stamp
        or if stamp is None then use store stamp
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
        console.profuse("Actioning DoerLapse  {0}\n".format(self.name))
        self.updateLapse()

    def _expose(self):
        """     """
        print("Doer %s stamp = %s lapse = %s" % (self.name, self.stamp, self.lapse))

    def _resolve(self, **kwa):
        """ Create enact with restart SideAct to restart this Actor """
        parms = super(DoerLapse, self)._resolve( **kwa)

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
