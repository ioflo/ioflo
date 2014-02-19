""" ioflo package

"""
#print "\nPackage at%s" % __path__[0]

__version__ = "0.9.06"
__author__ = "Samuel M. Smith"
__license__ =  "MIT"


from .base.consoling import getConsole

console = getConsole()

console.profuse("{0} version {1}\n".format(__path__[0], __version__))

__all__ = ['base', 'trim']

for m in __all__:
    exec "from . import %s" % m  #relative import
