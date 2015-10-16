"""__init__.py file for package

"""
#print("\nPackage at {0}".format( __path__[0]))
import importlib

_modules = []


for m in _modules:
    importlib.import_module(".{0}".format(m), package='ioflo.trim.exterior')


