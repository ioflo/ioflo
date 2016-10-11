"""housing.py framework entity module

"""
#print("module {0}".format(__name__))


import pdb
import copy

from collections import deque

from ..aid.sixing import *
#from .globaling import *
from ..aid.odicting import odict

from . import excepting
from . import registering

from . import storing #needed by house and for Registries

from . import acting  #needed for Registries
from . import poking  #needed for Registries
from . import needing  #needed for Registries
from . import goaling  #needed for Registries
from . import traiting  #needed for Registries
from . import fiating  #needed for Registries
from . import wanting  #needed for Registries
from . import completing  #needed for Registries
from . import doing  #needed for Registries
from . import tasking  #needed for Registries
from . import framing  #needed for Registries
from . import logging  #needed for Registries
from .. import trim  #needed for Registries

from ..aid.consoling import getConsole
console = getConsole()

# Dict of Registry Objects so can Clear and assign Names and Counter variables
# Frame names registry is held by each framer. Separate frame name space per framer

Registries = odict(store = storing.Store,
                  tasker = tasking.Tasker,
                  log = logging.Log,)

def ClearRegistries():
    """Clear the registries in Registries

    """
    for value in Registries.values():
        value.Clear()

#Class definitions

class House(registering.StoriedRegistrar):
    """House Class for managing framework(s)
       includes store for framework and name registries for framers, frames, and actions


       iherited instance attributes
          .name = unique name for machine
          .store = data store for house should be same for all frameworks

         instance attributes
          .taskers = list of taskers in house for resolve links
          .framers = list of framers needed to trace outlines

          .fronts = list of taskables to go in front of taskables
          .mids = list of taskables to go in middle of taskables
          .backs = list of taskables to go in back of taskables

          .taskables = list of active/inactive taskers (fronts + mids + backs)
          .auxes = list of aux  framers in house subset of .taskers
          .slaves = list of slave taskers in house subset of .taskers
          .moots = list of moot framers in house subset of .taskers

          .clones = list of tuples for cloning (original, clone, human, count)

          .names = dictonary of names from each name registry
          .counters = dictionary of counters from each name registry

          .metas = dictionary of (name, share) items of meta data for access by skedder
                  name is how skedder accesses the associated share
    """
    Counter = 0
    Names = {}

    def __init__(self, **kw):
        """Initialize instance. """
        super(House,self).__init__(**kw)

        self.taskers = [] #all taskers, framers servers loggers etc needed for resolving links
        self.framers = [] #list of all framers in house needed for tracing outlines

        self.fronts = [] #list of taskable taskers to go in front order
        self.mids = [] #list of taskable taskers to go in mid order
        self.backs = [] #list of taskable taskers to bo in back order

        self.taskables = [] #list taskable (active inactive) taskers (fronts + mids + backs)
        self.auxes = [] #list of aux framers in house
        self.slaves = [] #list of slave taskers in house
        self.moots = [] #list of moot framers in house

        self.presolvables = deque()  # deque of framer to be presolved
        self.resolvables = deque()  # deque of framers to be resolved

        self.names = odict() #houses dict of registry Names
        self.counters = odict() #houses dict of registry Name Counters

        self.metas = odict() # dict of meta data items (name, share) for skedder to access

        for key in Registries: #initialize names dicts for registry Names
            self.names[key] = odict()
            self.counters[key] = 0

        if not self.store:
            self.store = storing.Store(name = self.name)

        self.store.house = self #this allows bid all stop etc

    def orderTaskables(self):
        """Place taskables in order
        """
        console.terse("   Ordering taskable taskers for House '{0}' ...\n".format(self.name))
        self.taskables = self.fronts + self.mids + self.backs

    def assignRegistries(self):
        """Point class Names registries dicts and counters to local version in house
           Subsequent creation of instances will then be registered locally
           Idempotent operation
        """
        for key, value in Registries.items():
            value.Names = self.names[key]
            value.Counter = self.counters[key]

    def resolve(self):
        """ resolves links from building where links are name strings of objects
            resolution looks up name string in appropriate registry and replaces
            name string with link to object
        """
        console.terse("   Resolving House '{0}' ...\n".format(self.name))
        self.assignRegistries()

        for tasker in self.taskers:
            if not tasker.presolved and tasker not in self.moots:
                self.presolvables.append(tasker)

        self.presolvePresolvables()

        self.resolveResolvables()

    def presolvePresolvables(self):
        """
        Continually presolve presolvables deque until empty.
        Because a tasker (framer) may clone new framers
        each presolve may add more presolvables

        Once presolved add to resolvables
        """
        while self.presolvables:
            tasker = self.presolvables.popleft()
            tasker.presolve()
            self.resolvables.append(tasker)

    def resolveResolvables(self):
        """
        Continually resolve resolvables deque until empty.
        Because a tasker (framer) may clone new framers
        each resolve may add more resolvables
        """
        while self.resolvables:
            tasker = self.resolvables.popleft()
            tasker.resolve()

    def showAllTaskers(self):
        """Show all Taskers and Slaves and Auxes and Moots and Framers."""

        console.terse("Taskables in House '{0}':\n     {1}\n".format(
            self.name, ' '.join([tasker.name for tasker in self.taskables])))

        console.terse("Slaves in House '{0}':\n     {1}\n".format(
            self.name, ' '.join([tasker.name for tasker in self.slaves])))

        console.terse("Auxes in House '{0}':\n     {1}\n".format(
            self.name, ' '.join([tasker.name for tasker in self.auxes])))

        console.terse("Moots in House '{0}':\n     {1}\n".format(
                    self.name, ' '.join([tasker.name for tasker in self.moots])))

        console.terse("Framers in House '{0}':\n     {1}\n".format(
            self.name, ' '.join([tasker.name for tasker in self.framers])))
