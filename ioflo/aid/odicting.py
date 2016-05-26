"""
Ordered dictionary class with more flexible initialization and convenience methods.


Modified 2007-2015 by Samuel M Smith

Modifications CopyRight 2007-2015 by Samuel M smith

Based on various ordered dict implementations found in the wild

"""
from __future__ import absolute_import, division, print_function

from .sixing import *


class odict(dict):
    """
    Dictionary whose keys maintain the order they are added to the dict. Not
    order they are updated.

    Similar to the collections OrderedDict but with more flexible initialization
    and additional methods.

    The first key added to the dictionary is the first key in .keys()
    Changing the value of a key does not affect the order of the key

    """
    __slots__ = ['_keys']

    def __new__(cls, *args, **kwargs):
        self = dict.__new__(cls,*args, **kwargs)
        self._keys = []
        return self

    def __init__(self, *pa, **kwa):
        """
        Create new empty odict
        odict() returns new empty dictionary.

        odict(pa1, pa2, ...) creates new dictionary from
        pa = tuple of positional args, (pa1, pa2, ...)

        d = {}
        for a in pa:
           if hasattr(a,'get'):
              for k, v in a.items():
                 d[k] = v
           else:
              for k, v in a:
                 d[k] = v

        if pa is a sequence of duples (k,v) then ordering is preserved
        if pa is an ordered dictionary then ordering is preserved
        if pa is not an ordered dictionary then ordering is not preserved

        odict(k1 = v1, k2 = v2, ...) creates new dictionary from

        kwa = dictionary of keyword args, {k1: v1, k2 : v2, ...}

        d = {}
        for k, v in kwa:
           d[k] = v

        in this case key ordering is not preserved due to limitation of python
        """
        dict.__init__(self)

        for a in pa:
            if hasattr(a,'get'): #positional arg is dictionary
                for k in a:
                    self[k] = a[k]
            else: #positional arg is sequence of duples (k,v)
                for k, v in a:
                    self[k] = v

        for k in kwa:
            self[k] = kwa[k]

    def __delitem__(self, key):
        """ del x[y] """
        dict.__delitem__(self, key)
        self._keys.remove(key)

    def __iter__(self):
        """ iter(x)"""
        for key in self._keys:
            yield key

    def __repr__(self):
        """
        odict representation
        """
        return ("{0}({1})".format(self.__class__.__name__,
                                  repr(self.items())))

    def __setitem__(self, key, val):
        """ x[key]=val"""
        dict.__setitem__(self, key, val)
        if not hasattr(self, '_keys'):
            self._keys = [key]
        if key not in self._keys:
            self._keys.append(key)

    def __getnewargs__(self):
        """
        Needed to force __new__ which creates _keys.
        if empty odict then __getstate__ returns empty list which is logically false so
        __setstate__ is not called.
        """
        return tuple()

    def __getstate__(self):
        """
        return state as items list. need this so pickle works since defined slots
        """
        return self.items()

    def __setstate__(self, state):
        """
        restore from state items list
        """
        self.__init__(state)

    def append(self, key, item):
        """
        D[key] = item.
        """
        if key in self:
            raise KeyError('append(): key %r already in dictionary' % key)
        self[key] = item

    def clear(self):
        """ Remove all items from odict"""
        dict.clear(self)
        self._keys = []

    def copy(self):
        """
        Make a shallow copy of odict
        """
        items = [(key, dict.__getitem__(self, key)) for key in self._keys]
        return self.__class__(items) #creates new odict and populates with items

    def create(self, *pa, **kwa):
        """
        Create items in this odict but only if key not already existent
        pa may be sequence of duples (k,v) or dict
        kwa is dict of keyword arguments
        """
        for a in pa:
            if hasattr(a,'get'): #positional arg is dictionary
                for k in a:
                    if k not in self._keys:
                        self[k] = a[k]
            else: #positional arg is sequence of duples (k,v)
                for k, v in a:
                    if k not in self._keys:
                        self[k] = v

        for k in kwa:
            if k not in self._keys:
                self[k] = kwa[k]

    def sift(self, fields=None):
        """
        Return shallaw copy odict of items keyed by field name strings
        provided in optional fields sequence in that order with each value
        given by the associated
        item in self
        If fields is not provided then return odict copy of self with all
        the fields
        Raises KeyError if no entry for a given field name
        """
        if fields is None:
            return self.copy()

        items = [(key, dict.__getitem__(self, key)) for key in fields]
        return self.__class__(items) #creates new odict and populates with items

    def insert(self, index, key, val):
        """
        Insert val at index if key not in odict
        """
        if key in self:
            raise KeyError('Key %r already exists.' % key)
        dict.__setitem__(self, key, val)
        self._keys.insert(index, key)

    def items(self):
        return [(key, dict.__getitem__(self, key)) for key in self._keys]

    def iterkeys(self):
        """
        Return an iterator over the keys of odict
        """
        return iter(self)

    def iteritems(self):
        """
        Return an iterator over the items (key, value)  of odict.
        """
        return ((key, dict.__getitem__(self, key)) for key in self._keys)

    def itervalues(self):
        """
        Return an iterator over the values of odict.
        """
        return (dict.__getitem__(self, key) for key in self._keys)

    def keys(self):
        """
        Return the list of keys of odict.
        """
        return self._keys[:]

    def pop(self, key, *default):
        """
        Remove key and the associated item and return the associated value
        If key not found return default if given otherwise raise KeyError
        """
        value = dict.pop(self, key, *default)
        if key in self._keys:
            self._keys.remove(key)
        return value

    def popitem(self):
        """
        Remove and return last item (key, value) duple
        If odict is empty raise KeyError
        """
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('Empty odict.')
        value = dict.__getitem__(self, key)
        del self[key]
        return (key, value)

    def reorder(self, other):
        """
        Update values in this odict based on the `other` odict.
        Raises ValueError if other is not an odict
        """
        if not isinstance(other, odict):
            raise ValueError('other must be an odict')

        if other is self:
            #raise ValueError('other cannot be the same odict')
            pass #updating with self makes no changes

        dict.update(self, other)
        keys = self._keys

        for key in other:
            if key in keys:
                keys.remove(key)
            keys.append(key)

    def setdefault(self, key, default=None):
        """
        If key in odict, return value at key
        Otherwise set value at key to default and return default
        """
        value = dict.setdefault(self, key, default)
        if key not in self._keys:
            self._keys.append(key)
        return value

    def update(self, *pa, **kwa):
        """
        Update values in this odict
        pa may be sequence of duples (k,v) or dict
        kwa is dict of keyword arguments
        """
        for a in pa:
            if hasattr(a,'get'): #positional arg is dictionary
                for k in a:
                    self[k] = a[k]
            else: #positional arg is sequence of duples (k,v)
                for k, v in a:
                    self[k] = v

        for k in kwa:
            self[k] = kwa[k]

    def values(self):
        return [dict.__getitem__(self, key) for key in self._keys]

ODict = odict  # alias

#from . import optimize
#optimize.bind_all(odict)


class lodict(odict):
    """
    Lowercase odict ensures that all keys are lower case.
    """
    def __init__(self, *pa, **kwa):
        """
        lodict() -> new empty lodict instance.

            lodict(pa1, pa2, ...) where pa = tuple of positional args,
            (pa1, pa2, ...) each paX may be  a sequence of duples (k,v) or a dict

            lodict(k1 = v1, k2 = v2, ...) where kwa = dictionary of keyword args,
            {k1: v1, k2 : v2, ...}
        """
        super(lodict, self).__init__()  # must do this first
        self.update(*pa, **kwa)

    def update(self, *pa, **kwa):
        """
        lodict.update(pa1, pa2, ...) where pa = tuple of positional args,
        (pa1, pa2, ...) each paX may be  a sequence of duples (k,v) or a dict

        lodict.update(k1 = v1, k2 = v2, ...) where kwa = dictionary of keyword args,
        {k1: v1, k2 : v2, ...}
        """
        d = odict()
        for a in pa:
            if hasattr(a, 'get'): #positional arg is dictionary
                for k in a:
                    d[k.lower()] = a[k]

            else: #positional arg is sequence of duples (k,v)
                for k, v in a:
                    d[k.lower()] = v

        for k in kwa:
            d[k.lower()] = kwa[k]

        super(lodict, self).update(d)


    def __setitem__(self, key, val):
        """
        Make key lowercalse then setitem
        """
        super(lodict, self).__setitem__(key.lower(), val)

    def __delitem__(self, key):
        """
        Make key lowercase then delitem
        """
        super(lodict, self).__delitem__(key.lower())

    def __contains__(self, key):
        """
        Make key lowercase then test for inclusion
        """
        return super(lodict, self).__contains__(key.lower())

    def __getitem__(self, key):
        """
        Make key lowercase then getitem
        """
        return super(lodict, self).__getitem__(key.lower())


class modict(odict):
    """
    Multiple Ordered Dictionary. Inspired by other MultiDicts in the wild.
    Associated with each key is a list of values.
    Setting the value of an item appends the value to the list
    associated with the item key.
    Getting the value of an item returns the last
    item in the list associated with the item key.
    It behaves like an ordered dict
    in that the order of item insertion is remembered.

    There are special methods available to access or replace or append to
    the full list of values for a given item key.
    Aliases method names to match other multidict like interfaces like
    webob.
    """

    def __init__(self, *pa, **kwa):
        """
        modict() -> new empty modict instance.

        modict(pa1, pa2, ...) where pa = tuple of positional args,
        (pa1, pa2, ...) each paX may be  a sequence of duples (k,v) or a dict

        modict(k1 = v1, k2 = v2, ...) where kwa = dictionary of keyword args,
        {k1: v1, k2 : v2, ...}
        """
        super(modict, self).__init__()  # must do this first
        self.update(*pa, **kwa)

    def update(self, *pa, **kwa):
        """
        modict.update(pa1, pa2, ...) where pa = tuple of positional args,
        (pa1, pa2, ...) each paX may be  a sequence of duples (k,v) or a dict

        modict.update(k1 = v1, k2 = v2, ...) where kwa = dictionary of keyword args,
        {k1: v1, k2 : v2, ...}
        """
        for a in pa:
            if isinstance(a, modict): #positional arg is modict
                for k, v in a.iterallitems():
                    self.append(k, v)
            elif hasattr(a, 'get'): #positional arg is dictionary
                for k, v in a.iteritems():
                    self.append(k, v)
            else: #positional arg is sequence of duples (k,v)
                for k, v in a:
                    self.append(k, v)

        for k,v in kwa.items():
            self.append(k, v)

    def __getitem__(self, key):
        return super(modict, self).__getitem__(key)[-1] #newest
    def __setitem__(self, key, value):
        self.append(key, value) #append
    def values(self):
        return [v[-1] for v in super(modict, self).itervalues()]
    def listvalues(self):
        return [v for v in super(modict, self).itervalues()]
    def allvalues(self):
        return [v for k, vl in super(modict, self).iteritems() for v in vl]
    def items(self):
        return [(k, v[-1]) for k, v in super(modict, self).iteritems()]
    def listitems(self):
        return [(k, v) for k, v in super(modict, self).iteritems()]
    def allitems(self):
        return [(k, v) for k, vl in super(modict, self).iteritems() for v in vl]

    def itervalues(self):
        return (v[-1] for v in super(modict, self).itervalues())
    def iterlistvalues(self):
        return (v for v in super(modict, self).itervalues())
    def iterallvalues(self):
        return (v for k, vl in super(modict, self).iteritems() for v in vl)
    def iteritems(self):
        return ((k, v[-1]) for k, v in super(modict, self).iteritems())
    def iterlistitems(self):
        return ((k, v) for k, v in super(modict, self).iteritems())
    def iterallitems(self):
        return ((k, v) for k, vl in super(modict, self).iteritems() for v in vl)

    def has_key(self, key):
        return key in self

    def append(self, key, value):
        """
        Add a new value to the list of values for this key.
        """
        super(modict, self).setdefault(key, []).append(value)

    def copy(self):
        return self.__class__(self)

    def get(self, key, default=None, index=-1, kind=None):
        """
        Return the most recent value for a key, that is, the last element
        in the keyed item's value list.

        default = value to be returned if the key is not
            present or the type conversion fails.
        index = index into the keyed item's value list.
        kind = callable is used to cast the value into a specific type.
            Exception are suppressed and result in the default value
            to be returned.
        """
        try:
            val = self[key][index]
            return kind(val) if kind else val
        except Exception:
            pass
        return default

    def getlist(self, key):
        """
        Return a (possibly empty) list of values for a key.
        """
        return super(modict, self).get(key) or []

    def replace(self, key, value):
        """
        Replace the list of values with a single item list of value.
        """
        super(modict, self).__setitem__(key, [value])

    def setdefault(self, key, default=None, kind=None):
        """
        If key is in the dictionary, return the last (most recent) element
        from the keyed items's value list.

        If not, insert key with a value of default and return default.
        The default value of default is None.

        kind = callable is used to cast the returned value into a specific type.

        Exceptions are suppressed and result in the default value being set
        """
        try:
            val = super(modict, self).__getitem__(key)
            return kind(val[-1]) if kind else val[-1]
        except Exception:
            self.append(key, default)
        return default


    def pop(self, key, *pa, **kwa):
        """
        If key exists remove and return the indexed element of the key element
        list else return the optional following positional argument.
        If the optional positional arg is not provided and key does not exit
        then raise KeyError. If provided the index keyword arg determines
        which value in the key element list to return. Default is last element.
        """
        index = kwa.get('index', -1)
        try:
            val = super(modict, self).pop(key)
        except KeyError:
            if pa:
                return pa[0]
            else:
                raise

        return val[index]

    def poplist(self, key, *pa):
        """
        If key exists remove and return keyed item's value list,
        else return the optional following positional argument.
        If the optional positional arg is not provided and key does not exit
        then raise KeyError.

        """
        try:
            val = super(modict, self).pop(key)
        except KeyError:
            if pa:
                return pa[0]
            else:
                raise

        return val

    def popitem(self, last=True, index=-1):
        """
        Return and remove a key value pair. The index determines
        which value in the keyed item's value list to return.
        If last is True pop in LIFO order.
        If last is False pop in FIFO order.
        """
        key, val = super(modict, self).popitem(last=last)
        return (key, val[index])

    def poplistitem(self, last=True):
        """
        Return and remove a key value list pair.
        If last is True pop in LIFO order.
        If last is False pop in FIFO order.
        """
        return (super(modict, self).popitem(last=last))

    def fromkeys(self, seq, default=None):
        """
        Return new modict with keys from sequence seq with values set to default
        """
        return modict((k, default) for k in seq)

    # aliases to mimic other multi-dict APIs
    getone = get
    add = append
    popall = poplist



def TestPickle():
    """tests ability of odict to be pickled and unpickled


       New-style types can provide a __getnewargs__() method that is used for protocol 2.

       Note that last phrase about requiring protocol 2.  Your
       example works if you add a third parameter to pickle.dump()
       with the value of 2.  Version 2 is not default.

    """
    import pickle
    import StringIO

    x = odict([('z',1),('a',2),('r',3)])
    s = StringIO.StringIO()
    pickle.dump(x,s,2)
    s.seek(0)
    y = pickle.load(s)
    print(x)
    print(y)

    #empty odict
    x = odict()
    s = StringIO.StringIO()
    pickle.dump(x,s,2)
    s.seek(0)
    y = pickle.load(s)
    print(x)
    print(y)

def Test():
    """Self test

    """
    seq = [('b', 1), ('c', 2), ('a', 3)]
    dct = {}
    for k,v in seq:
        dct[k] = v

    odct = odict()
    for k,v in seq:
        odct[k] = v


    print("Intialized from sequence of duples 'seq' = %s" % seq)
    x = odict(seq)
    print("   odict(seq) = %s" % x)

    print("Initialized from unordered dictionary 'dct' = %s" % dct)
    x = odict(dct)
    print("   odict(dct) = %s" % x)

    print("Initialized from ordered dictionary 'odct' = %s" % odct)
    x = odict(odct)
    print("   odict(odct) = %s" % x)

    print("Initialized from keyword arguments 'b = 1, c = 2, a = 3'")
    x = odict(b = 1, c = 2, a = 3)
    print("   odict(b = 1, c = 2, a = 3) = %s" % x)

    print("Initialized from mixed arguments")
    x = odict(odct, seq, [('e', 4)], d = 5)
    print("   odict(odct, seq, d = 4) = %s" % x)

