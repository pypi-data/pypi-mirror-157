from __future__ import annotations

from collections import UserDict

from typing import Mapping, Type

from utilicity._types import T
from utilicity.items.helpers import *

__all__ = (
    'dicto',
    'fallbackdicto',
    'recurdicto',
    'objectdict'
)


class dicto(UserDict, dict):  # <- allows passing isinstance(dict, d)
    """Wrapper over a dict adding some convenient methods.

    The methods are following same name convention that is described
    in utilicity.items.helpers.

    Note:
        If you don't want this class, all the methods are also available
        in utilicity.items.helpers.

    Examples:
        >>> d = dicto(a=1, b=2)
        >>> d.setz('c', 3)
        {'a': 1, 'b': 2, 'c': 3}

    """

    def __init__(self, data=None, wrap=False, /, **kwargs):
        """Initialize a new instance.

        The class is a subclass of collections.UserDict and thus it works like
        a proxy around internal dict. It's also a subclass of dict to pass
        isinstance(d, dict) checks.

        Args:
            data: The data to initialize the instance with that can be any
                  Mapping subclass or iterable of key-value pairs.
            wrap: Use the data as
            """
        if wrap:
            if not isinstance(data, Mapping):
                raise TypeError(f'When wrap is True, data must be of Mapping.')
            self.dict = data
        else:
            self.data = {}
            if data is not None:
                super().update(data)
            if kwargs:
                super().update(kwargs)

    getd = getd
    getf = getf
    setz = setz
    setv = setv
    setdz = setdz
    setdv = setdv
    setfz = setfz
    setfv = setfv
    has = has
    hasd = hasd
    hasf = hasf
    incv = incv
    incz = incz
    decv = decv
    decz = decz
    update = update
    merge = merge
    flip = flip
    replacekey = replacekey
    removekeys = removekeys
    take = take
    taked = taked
    takef = takef


class fallbackdicto(dicto):
    """Like defaultdict but fallback() receives missing key as the argument.

    Example:
        >>> d = fallbackdicto(lambda k: (k, k))
        >>> d['foo']
        ('foo', 'foo')
        >>> d
        {'foo': ('foo', 'foo')}
    """

    def __init__(self, fallback: callable, *args, **kwargs):
        self.fallback = fallback
        super().__init__(*args, **kwargs)

    def __missing__(self, key):
        res = self[key] = self.fallback(key)
        return res

    @classmethod
    def wrapdict(cls: Type[T], d: Mapping, fallback: callable) -> T:
        """Uses d as the underlying dict."""
        inst = cls(fallback)
        inst.data = d
        return inst


class recurdicto(dicto):
    """Dict where items can be accessed indefinitely, even if they don't exist.

    Example:
        >>> d = recurdicto()
        >>> d[1][2] # no KeyError raised
        {}
        >>> d
        {1: {2: {}}}
        >>> d[1][2] = 1
        >>> d
        {1: {2: 1}}
    """

    def __missing__(self, key):
        res = self[key] = __class__()
        return res


class objectdict(dict):
    """Dict where keys are accessable as attributes.

    Beware that dict instance methods are not directly available.
    So calling dict.items() will not work (is now same as d['items']()).
    If standard methods are needed, use type methods, e.g. `dict.items(d)`.

    Example:
        >>> d = objectdict(items='bar')
        >>> d.foo = 1
        >>> d.foo
        1
        >>> d
        {'items': 'bar', 'foo': 1}
        >>> d.items()  # <-- will not work
        Traceback (most recent call last):
        ...
        TypeError: 'str' object is not callable
        >>> dict.items(d)  # <-- but this will
        dict_items([('items', 'bar'), ('foo', 1)])
    """

    def __getattribute__(self, item):
        return self[item]

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]
