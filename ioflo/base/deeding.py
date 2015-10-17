"""
deeding.py deed module

Backwards compatibility module
Future use doing module instead

"""
from . import doing

# for backwards compatibility

deedify = doing.doify
class Deed(doing.Doer):
    pass

class DeedParam(doing.DoerParam):
    pass

class DeedSince(doing.DoerSince):
    pass

class DeedLapse(doing.DoerLapse):
    pass

