"""__init__.py file for package

"""
#print("\nPackage at {0}".format( __path__[0]))
import importlib

__all__ = ['plain', 'fancy']

for m in __all__:
    importlib.import_module(".{0}".format(m), package='ioflo.trim.interior')

