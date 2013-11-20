""" plain package

"""
#print "\nPackage at%s" % __path__[0]

__all__ = [ 'controlling', 'detecting', 'estimating',
            'filtering',  'simulating' ]

for m in __all__:
    exec "from . import %s" % m  #relative import
    #print "Imported %s" % globals().get(m,'')

#used by CreateAllInstances                 
_InstanceModules = [controlling, detecting, estimating,
                    filtering, simulating]
