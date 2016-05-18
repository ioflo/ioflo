""" base package


"""
#print("Package at {0}".format(__path__[0]))
import importlib

_modules = ['globaling', 'excepting', 'interfacing',
           'registering', 'storing', 'skedding',
           'tasking', 'framing', 'logging', 'serving', 'monitoring',
           'acting', 'poking', 'goaling', 'needing', 'traiting',
           'fiating', 'wanting','completing','doing', 'deeding', 'arbiting',
           'housing', 'building']


for m in _modules:
    importlib.import_module(".{0}".format(m), package='ioflo.base')

from .storing import Store, Node, Share, Data, Deck
from .doing import doify, Doer, DoerParam, DoerSince, DoerLapse
