""" plain package

"""
#print("\nPackage at {0}".format( __path__[0]))
import importlib

_modules = [ 'controlling', 'detecting', 'estimating',
            'filtering',  'simulating' ]

for m in _modules:
    importlib.import_module(".{0}".format(m), package='ioflo.trim.interior.plain')

