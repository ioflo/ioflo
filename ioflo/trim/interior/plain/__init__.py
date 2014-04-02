""" plain package

"""
#print("\nPackage at {0}".format( __path__[0]))
import importlib

__all__ = [ 'controlling', 'detecting', 'estimating',
            'filtering',  'simulating' ]

for m in __all__:
    importlib.import_module(".{0}".format(m), package='ioflo.trim.interior.plain')

