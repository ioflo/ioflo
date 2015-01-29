"""Ordered dictionary class.


Modified 2007, 2008 by Samuel M Smith

Modifications CopyRight 2007 by Samuel M smith

Based on various ordered dict implementations found in the wild

"""
#print("module {0}".format(__name__))


class odict(dict):
    """ Dictionary whose keys maintain the order they are added to the dict. Not
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
        """ Create new empty odict
            odict() returns new empty dictionary.

            odict(pa1, pa2, ...) creates new dictionary from
            pa = tuple of positional args, (pa1, pa2, ...)

            d = {}
            for a in pa:
               if isinstance(a, dict):
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
            if isinstance(a, dict): #positional arg is dictionary
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
        """ repr(x)"""
        itemreprs = ('%r: %r' % (key, self[key]) for key in self._keys)
        return '{' + ', '.join(itemreprs) + '}'

    def __setitem__(self, key, val):
        """ x[key]=val"""
        dict.__setitem__(self, key, val)
        if not hasattr(self, '_keys'):
            self._keys = [key]
        if key not in self._keys:
            self._keys.append(key)

    def __getnewargs__(self):
        """Needed to force __new__ which creates _keys.
           if empty odict then __getstate__ returns empty list which is logically false so
           __setstate__ is not called.
        """
        return tuple()

    def __getstate__(self):
        """ return state as items list. need this so pickle works since defined slots"""
        return self.items()

    def __setstate__(self, state):
        """restore from state items list"""
        self.__init__(state)

    def append(self, key, item):
        """ D[key] = item."""
        if key in self:
            raise KeyError('append(): key %r already in dictionary' % key)
        self[key] = item

    def clear(self):
        """ Remove all items from odict"""
        dict.clear(self)
        self._keys = []

    def copy(self):
        """ Make a shallow copy of odict"""
        items = [(key, self[key]) for key in self._keys]
        return self.__class__(items) #creates new odict and populates with items

    def create(self, *pa, **kwa):
        """create items in this odict but only if key not already existent
           pa may be sequence of duples (k,v) or dict
           kwa is dict of keyword arguments
        """
        for a in pa:
            if isinstance(a, dict): #positional arg is dictionary
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

    def insert(self, index, key, val):
        """ Insert val at index if key not in odict"""
        if key in self:
            raise KeyError('Key %r already exists.' % key)
        dict.__setitem__(self, key, val)
        self._keys.insert(index, key)

    def items(self):
        return [(key, self[key]) for key in self._keys]

    def iterkeys(self):
        """ Return an iterator over the keys of odict"""
        return iter(self)

    def iteritems(self):
        """ Return an iterator over the items (key, value)  of odict."""
        return ((key, self[key]) for key in self._keys)

    def itervalues(self):
        """ Return an iterator over the values of odict."""
        return (self[key] for key in self._keys)

    def keys(self):
        """ Return the list of keys of odict."""
        return self._keys[:]

    def pop(self, key, *default):
        """ Remove key and the associated item and return the associated value
            If key not found return default if given otherwise raise KeyError
        """
        value = dict.pop(self, key, *default)
        if key in self._keys:
            self._keys.remove(key)
        return value

    def popitem(self):
        """ Remove and return last item (key, value) duple
            If odict is empty raise KeyError
        """
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('Empty odict.')
        value = self[key]
        del self[key]
        return (key, value)

    def reorder(self, other):
        """ Update values in this odict based on the `other` odict or dict.
           reorder is ignored if other is not an odict
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
        """ If key in odict, return value at key
            Otherwise set value at key to default and return default
        """
        value = dict.setdefault(self, key, default)
        if key not in self._keys:
            self._keys.append(key)
        return value

    def update(self, *pa, **kwa):
        """Update values in this odict
           pa may be sequence of duples (k,v) or dict
           kwa is dict of keyword arguments
        """
        for a in pa:
            if isinstance(a, dict): #positional arg is dictionary
                for k in a:
                    self[k] = a[k]
            else: #positional arg is sequence of duples (k,v)
                for k, v in a:
                    self[k] = v

        for k in kwa:
            self[k] = kwa[k]

    def values(self):
        return [self[key] for key in self._keys]

ODict = odict  # alias

#from . import optimize
#optimize.bind_all(odict)


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

