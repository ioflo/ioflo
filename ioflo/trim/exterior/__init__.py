"""__init__.py file for package

"""
#print "\nPackage at%s" % __path__[0]

__all__ = [] 


for m in __all__:
    exec "from . import %s" % m  #relative import
    #print "Imported %s" % globals().get(m,'')

#used by CreateAllInstances               
_InstanceModules = []
