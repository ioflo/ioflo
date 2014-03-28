""" fancy package

"""
#print "\nPackage at {0}".format( __path__[0])

__all__ = ['cloning']

for m in __all__:
    exec("from . import {0}".format(m)) #relative import

