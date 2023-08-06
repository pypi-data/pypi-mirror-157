from typing import Any, Callable, Iterable, Mapping, MutableMapping, Type, Union

from utilicity._types import T, TCallableOrAny, TNumber
from utilicity.sentinels import _Unset

__all__ = (
    'throw',
    'func',
    'getresult',
    'attrget',
    'attrset',
    'attrcheck',
    'first',
    'last',
    'isnone',
    'notnone',
    'coalesce',
    'default',
    'ifset',
    'perform',
    'inc',
    'dec',
    'attrinc',
    'attrdec',
)


def throw(exc: Union[Exception, Type[Exception]]):
    """Raise exception.

    Useful for throwing exceptions from expressions.

    Example:
        >>> False or throw(ValueError())
        Traceback (most recent call last):
        ...
        ValueError
    """
    raise exc


def func(arg):
    """Wraps the arg within a function.

    Useful for returning callable arg itself when passing it to functions that
    expect f/callbacks and would call the arg otherwise.

    Example:
        >>> func(1)()
        1
    """

    def _func():
        return arg

    return _func


def getresult(arg: TCallableOrAny):
    """Returns the result of calling arg() if callable, or the arg itself.

    Example:
        >>> getresult(lambda: True)
        True
        >>> getresult(True)
        True
    """
    return arg() if callable(arg) else arg


def first(iterable: Iterable, fallback: TCallableOrAny = _Unset):
    """Returns first element of iterable.

    If iterable is empty, the result of fallback() will be returned instead.
    If fallback is not set, ValueError will be raised.

    Example:
        >>> first([1, 2, 3])
        1
        >>> first([], fallback=1)
        1
        >>> first([], fallback=lambda: 1)
        1
        >>> first([])
        Traceback (most recent call last):
        ...
        ValueError: iterable is empty
    """
    for item in iterable:
        return item
    if fallback is _Unset:
        raise ValueError('iterable is empty')
    return getresult(fallback)


def last(iterable: Iterable, fallback: TCallableOrAny = _Unset):
    """Returns last element of iterable.

    If iterable is empty, the result of fallback() will be returned instead.
    If fallback is not set, ValueError will be raised.

    Example:
        >>> last([1, 2, 3])
        3
        >>> last([], fallback=1)
        1
        >>> last([], fallback=lambda: 1)
        1
        >>> last([])
        Traceback (most recent call last):
        ...
        ValueError: iterable is empty
    """
    item = _Unset
    for item in iterable:
        pass

    if item is not _Unset:
        return item
    elif fallback is _Unset:
        raise ValueError('iterable is empty')
    return getresult(fallback)


def isnone(arg):
    """Returns True if arg is None.

    Example:
        >>> isnone(1)
        False
        >>> isnone(None)
        True
    """
    return arg is None


def notnone(arg):
    """Returns True if arg is not None.

    Example:
        >>> notnone(1)
        True
        >>> notnone(None)
        False
    """
    return arg is not None


def coalesce(*args, none=None, cond: Callable[[Any], bool] = None):
    """Returns first arg that passes cond(), if all args fail,
    the none will be returned.

    Default cond is: x is not none.

    If all args are none, none will be returned.
    Cond is a callable that takes an arg and returns True if it is not none.

    Args:
        none: Param that args will be compared to.
        cond: If specified, it will be used as condition for checking.

    Example:
        >>> coalesce(None) is None
        True
        >>> coalesce(1, None, 2)
        1
        >>> coalesce(None, 2)
        2
        >>> unset=object()
        >>> coalesce(unset, 2, none=unset)
        2
        >>> coalesce(unset, unset, none=unset) is unset
        True
        >>> coalesce('', 0, 1, cond=bool)
        1
        >>> coalesce('', 0, 0, cond=bool) is None
        True
        >>> coalesce(1, 2, cond=lambda x: x % 2 == 0)
        2
        >>> coalesce(1, 3, none=-1, cond=lambda x: x % 2 == 0)
        -1
    """
    if cond is None:
        def cond(x):
            return x is not none
    for arg in args:
        if cond(arg):
            return arg
    return none


def default(fallback: TCallableOrAny, *args,
            cond: Callable[[Any], bool] = notnone):
    """Returns the first arg that passes the cond(), if all args fail,
    the result of fallback() will be returned instead.

    Example:
        >>> default(lambda: 1, None)
        1
        >>> default(1, None, None)
        1
        >>> default(2, None, 1)
        1
        >>> default(lambda: False, '', 0, 0, cond=bool)
        False
    """
    for arg in args:
        if cond(arg):
            return arg
    return getresult(fallback)


def ifnone(arg: T, fallback: TCallableOrAny):
    """Returns arg if arg is not None, otherwise returns the result of fallback().

    Example:
        >>> ifnone(1, 2)
        1
        >>> ifnone(None, 2)
        2
    """
    return getresult(fallback) if arg is None else arg


def ifset(arg: T, callback: Callable[[T], Any], none=None):
    """If the arg is not the none, calls callback(arg) and returns the result.

    Args:
        arg: The argument to check.
        callback: The callback to call if arg is not none.
        none: The value to return if arg is none.

    Returns:
        result of callback(arg) if arg is not none, else none

    Example:
        >>> ifset(1, lambda x: x * 2)
        2
        >>> ifset(None, lambda x: x * 2) is None
        True
        >>> ifset(False, lambda x: x * 2, none=False) is False
        True
    """
    return none if arg is none else callback(arg)


def perform(arg: T, method: str, *args, **kwargs) -> T:
    """Calls arg.method(*args, **kwargs) and returns the arg.

    Example:
        >>> perform([], 'append', 1)
        [1]
    """
    getattr(arg, method)(*args, **kwargs)
    return arg


def inc(arg: TNumber, n: TNumber = 1):
    """Increments arg by n.

    Example:
        >>> inc(1)
        2
    """
    return arg + n


def dec(arg: TNumber, n: TNumber = 1):
    """Decrements arg by n.

    Example:
        >>> dec(1)
        0
    """
    return arg - n


def attrinc(obj, attr: str, n: TNumber = 1):
    """Increments obj.attr by n.
    When attr doesn't exist, it is created with 0 value.

    Example:
        >>> obj = type('Obj', (), {})()
        >>> _ = attrinc(obj, 'x')
        >>> obj.x
        1
    """
    setattr(obj, attr, getattr(obj, attr, 0) + n)
    return obj


def attrdec(obj, attr: str, n: TNumber = 1):
    """Decrements obj.attr by n.
    When attr doesn't exist, it is created with 0 value.

    Example:
        >>> obj = type('Obj', (), {})()
        >>> _ = attrdec(obj, 'x')
        >>> obj.x
        -1
    """
    setattr(obj, attr, getattr(obj, attr, 0) - n)
    return obj


def attrget(obj, attr: str, fallback: TCallableOrAny):
    """Returns obj.attr when it exists, or the result of fallback().

    Example:
        >>> o = object()
        >>> attrget(o, 'lol', lambda: 1)
        1
    """
    try:
        return getattr(obj, attr)
    except AttributeError:
        return getresult(fallback)


def attrset(obj, attr: str, fallback: TCallableOrAny = None):
    """Does obj.attr = fallback() if attr doesn't exist. Returns the value.

    Example:
        >>> obj = type('Obj', (), {})()
        >>> attrset(obj, 'x', lambda: 1)
        1
        >>> obj.x
        1
    """
    try:
        return getattr(obj, attr)
    except AttributeError:
        setattr(obj, attr, res := getresult(fallback))
        return res


def attrcheck(obj: T, attr: str, fallback: TCallableOrAny = None) -> T:
    """Check if obj.attr exists, when it doesn't, set it to fallback()
    and return obj.

    Example:
        >>> o = type('Obj', (), {})()
        >>> attrcheck(o, 'foo', lambda: 1).foo
        1
    """
    if not hasattr(obj, attr):
        setattr(obj, attr, getresult(fallback))
    return obj


def traverse(obj: Mapping,
             func: Callable[..., None],
             fargs: Union[list, tuple] = None,
             fkwargs: Mapping = None, *, onlyleafs=False):
    """Traverses the obj and calls the func on each item.

    Args:
        obj: Object to traverse.
        func: Function(item, path: tuple, *args, **kwargs) to call on each item.
              The path contains list of keys to get to the item from the obj.
        fargs: Positional arguments to pass to func.
        fkwargs: Keyword arguments to pass to func.
        onlyleafs: If True, only on leafs func will be called.

    Example:
        >>> d = {'foo': 1, 'bar': [{'baz': 2, 'qux': b'abc', 'quux': {1}}]}
        >>> def f(x, p):
        ...     print(f'{p}: ({type(x)}) {x}')
        >>> traverse(d, f)
        (): (<class 'dict'>) {'foo': 1, 'bar': [{'baz': 2, 'qux': b'abc', 'quux': {1}}]}
        ('foo',): (<class 'int'>) 1
        ('bar',): (<class 'list'>) [{'baz': 2, 'qux': b'abc', 'quux': {1}}]
        ('bar', 0): (<class 'dict'>) {'baz': 2, 'qux': b'abc', 'quux': {1}}
        ('bar', 0, 'baz'): (<class 'int'>) 2
        ('bar', 0, 'qux'): (<class 'bytes'>) b'abc'
        ('bar', 0, 'quux'): (<class 'set'>) {1}
        ('bar', 0, 'quux', 0): (<class 'int'>) 1
        >>> def f(x, p):
        ...     print(f'{p}: ({type(x)}) {x}')
        >>> traverse(d, f, onlyleafs=True)
        ('foo',): (<class 'int'>) 1
        ('bar', 0, 'baz'): (<class 'int'>) 2
        ('bar', 0, 'qux'): (<class 'bytes'>) b'abc'
        ('bar', 0, 'quux', 0): (<class 'int'>) 1
    """
    fargs, fkwargs = ifnone(fargs, tuple), ifnone(fkwargs, dict)
    visited = set()

    def _traverse(item, path):
        if id(item) in visited:
            return

        if isinstance(item, Mapping):
            visited.add(id(item))
            if not onlyleafs:
                func(item, path, *fargs, **fkwargs)
            for k, v in item.items():
                _traverse(v, path + (k,))
        elif not isinstance(item, (str, bytes)) and isinstance(item, Iterable):
            visited.add(id(item))
            if not onlyleafs:
                func(item, path, *fargs, **fkwargs)
            for i, v in enumerate(item):
                _traverse(v, path + (i,))
        else:
            func(item, path, *fargs, **fkwargs)

    _traverse(obj, ())
