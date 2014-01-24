""" fancy package

"""
#print "\nPackage at%s" % __path__[0]

__all__ = ['cloning']

for m in __all__:
    exec "from . import %s" % m  #relative import

