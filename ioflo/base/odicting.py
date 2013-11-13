"""Ordered dictionary class.


Modified 2007, 2008 by Samuel M Smith 

Modifications CopyRight 2007 by Samuel M smith

Copyright (C) 2001-2007 Orbtech, L.L.C.

For other copyright, license, and warranty, see bottom of file.

"""
#print "module %s" % __name__

import optimize

#from types import ListType, TupleType

class odict(dict):
    """Dictionary whose keys maintain their order of membership.

    In other words, the first key added to the dictionary is the first
    key returned in the list of odict.keys(), etc.  Note that a call
    to __setitem__() for an existing key does not change the order of
    that key."""

    __slots__ = ['_keys']


    def __new__(cls, *args, **kwargs): 
        self = dict.__new__(cls,*args, **kwargs)
        self._keys = []
        return self

    def __init__(self, *pa, **kwa):
        """dict() -> new empty dictionary.

           dict(pa1, pa2, ...) -> new dictionary initialized as if via:
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



           dict(k1 = v1, k2 = v2, ...) -> new dictionary initialized as if via:

           kwa = dictionary of keyword args, {k1: v1, k2 : v2, ...}

           d = {}
           for k, v in kwa:
              d[k] = v

           in this case ordering is not preserved
        """
        #self._keys = []  # called in __new__ which was added to support pickling protocol
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
        """x.__delitem__(y) <==> del x[y]"""
        dict.__delitem__(self, key)
        self._keys.remove(key)

    def __iter__(self):
        """x.__iter__() <==> iter(x)"""
        for key in self._keys:
            yield key

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        itemreprs = ('%r: %r' % (key, self[key]) for key in self._keys)
        return '{' + ', '.join(itemreprs) + '}'

    def __setitem__(self, key, item):
        """x.__setitem__(i, y) <==> x[i]=y"""
        dict.__setitem__(self, key, item)
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
        """Alias for D[key] = item."""
        if key in self:
            raise KeyError('append(): key %r already in dictionary' % key)
        self[key] = item

    def clear(self):
        """D.clear() -> None.  Remove all items from D."""
        dict.clear(self)
        self._keys = []

    def copy(self):
        """D.copy() -> a shallow copy of D"""
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


    def insert(self, index, key, item):
        """Insert key:item at index."""
        if key in self:
            raise KeyError('insert(): key %r already in dictionary' % key)
        dict.__setitem__(self, key, item)
        self._keys.insert(index, key)

    def items(self):
        return [(key, self[key]) for key in self._keys]

    def iterkeys(self):
        """D.iterkeys() -> an iterator over the keys of D"""
        return iter(self)

    def iteritems(self):
        """D.iteritems() -> an iterator over the (key, value) items of D"""
        return ((key, self[key]) for key in self._keys)

    def itervalues(self):
        """D.itervalues() -> an iterator over the values of D"""
        return (self[key] for key in self._keys)

    def keys(self):
        """D.keys() -> list of D's keys"""
        return self._keys[:]

    def pop(self, key, *failobj):
        """D.pop(k[,d]) -> v, remove specified key and return the
        corresponding value

        If key is not found, d is returned if given, otherwise
        KeyError is raised
        """
        value = dict.pop(self, key, *failobj)
        if key in self._keys:
            self._keys.remove(key)
        return value

    def popitem(self):
        """D.popitem() -> (k, v), remove and return last (key, value)
        pair as a 2-tuple; but raise KeyError if D is empty"""
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('popitem(): dictionary is empty')
        value = self[key]
        del self[key]
        return (key, value)


    def reorder(self, other):
        """Update values in this odict based on the `other` odict or dict.
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


    def setdefault(self, key, failobj=None):
        """D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D"""
        value = dict.setdefault(self, key, failobj)
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


optimize.bind_all(odict)


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
    print x
    print y

    #empty odict
    x = odict()
    s = StringIO.StringIO()
    pickle.dump(x,s,2)
    s.seek(0)
    y = pickle.load(s)
    print x
    print y


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


    print "Intialized from sequence of duples 'seq' = %s" % seq
    x = odict(seq)
    print "   odict(seq) = %s" % x

    print "Initialized from unordered dictionary 'dct' = %s" % dct
    x = odict(dct)
    print "   odict(dct) = %s" % x

    print "initialized from ordered dictionary 'odct' = %s" % odct
    x = odict(odct)
    print "   odict(odct) = %s" % x

    print "Initialized from keyword arguments 'b = 1, c = 2, a = 3'"
    x = odict(b = 1, c = 2, a = 3)
    print "   odict(b = 1, c = 2, a = 3) = %s" % x

    print "Initialized from mixed arguments"
    x = odict(odct, seq, [('e', 4)], d = 5)
    print "   odict(odct, seq, d = 4) = %s" % x



## # Bind the docstrings from dict to odict.
## for k, v in odict.__dict__.iteritems():
##    if k != '_keys' and hasattr(v, '__doc__') and v.__doc__ is None:
##       v.__doc__ = getattr(dict, v.__name__).__doc__





# Copyright (C) 2001-2007 Orbtech, L.L.C.
#
# Schevo
# http://schevo.org/
#
# Orbtech
# Saint Louis, MO
# http://orbtech.com/
#
# This toolkit is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This toolkit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.   See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA