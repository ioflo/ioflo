""" base package


"""
#print "Package at {0}".format(__path__[0])

__all__ = ['globaling', 'aiding', 'excepting', 'interfacing',
           'registering', 'storing', 'skedding',
           'tasking', 'framing', 'logging', 'serving', 'monitoring',
           'acting', 'poking', 'goaling', 'needing', 'traiting',
           'fiating', 'wanting','completing','deeding', 'arbiting',
           'housing', 'building',  'testing']


for m in __all__:
    exec("from . import {0}".format(m)) #relative import
    #print "Imported {0}".format(globals().get(m,''))

