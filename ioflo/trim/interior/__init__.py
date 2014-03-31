"""__init__.py file for package

"""
#print("\nPackage at {0}".format( __path__[0]))

__all__ = ['plain', 'fancy']

for m in __all__:
    exec("from . import {0}".format(m)) #relative import
    #print "Imported {0}".format(globals().get(m,''))

