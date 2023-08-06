"""Helper functions for working with dicts.

Naming convention of the functions:
    <Name>[<Suffixes [df][zvn]>]

    Name:
        name of the function.
    Suffixes:
        d: Has default value to be used when key doesn't exist.
        f: Has fallback function value to be used when key doesn't exist.
        v: Returns value.
        z: Returns input object.
        n: Returns new object (original object stays intact).

"""
from typing import Any, Callable, Iterable, Literal, Mapping, MutableMapping, Tuple

from utilicity._types import TNumber
from utilicity.sentinels import _Unset


__all__ = (
    'getd',
    'getf',
    'setz',
    'setv',
    'setdz',
    'setdv',
    'setfz',
    'setfv',
    'has',
    'hasd',
    'hasf',
    'incv',
    'incz',
    'decv',
    'decz',
    'update',
    'merge',
    'flip',
    'replacekey',
    'removekeys',
    'take',
    'taked',
    'takef',
)

obj = MutableMapping  # to tell that return value is input object


def getd(obj: Mapping, key, default=None):
    """Gets obj[key] or default if key doesn't exist.

    Args:
        obj: Mapping object.
        key: Key to get.
        default: Default value to return if key doesn't exist.

    Example:
        >>> d = {'foo': 1}
        >>> getd(d, 'foo')
        1
        >>> getd(d, 'bar', 1)
        1
    """
    if default is _Unset:
        return obj[key]
    return obj.get(key, default)


def getf(obj: Mapping, key, fallback: Callable[[], Any]):
    """Gets obj[key] or fallback() if key doesn't exist.

    Example:
        >>> d = {'foo': 1}
        >>> getf(d, 'foo', lambda: 2)
        1
        >>> getf(d, 'bar', lambda: 2)
        2
    """
    try:
        return obj[key]
    except KeyError:
        return fallback()


def setz(obj: MutableMapping, key, value) -> obj:
    """Sets obj[key] to value, returns obj.

    Example:
        >>> d = {}
        >>> setz(d, 'foo', 1)
        {'foo': 1}
    """
    obj[key] = value
    return obj


def setv(obj: MutableMapping, key, value):
    """Sets obj[key] to value, returns value.

    Example:
        >>> d = {}
        >>> setv(d, 'foo', 1)
        1
        >>> d
        {'foo': 1}
    """
    obj[key] = value
    return value


def setdz(obj: MutableMapping, key, default=None) -> obj:
    """Sets obj[key] to default if key doesn't exist, returns obj.

    Example:
        >>> d = {}
        >>> setdz(d, 'foo', 1)
        {'foo': 1}
        >>> setdz(d, 'foo', 2)
        {'foo': 1}
    """
    if key not in obj:
        obj[key] = default
    return obj


def setdv(obj: MutableMapping, key, default=None):
    """Sets obj[key] to default if key doesn't exist, returns value.

    Example:
        >>> d = {}
        >>> setdv(d, 'foo', 1)
        1
        >>> setdv(d, 'foo', 2)
        1
        >>> d
        {'foo': 1}
    """
    try:
        return obj[key]
    except KeyError:
        obj[key] = default
        return default


def setfz(obj: MutableMapping, key, fallback: Callable[[], Any]) -> obj:
    """Sets obj[key] to fallback() if key doesn't exist, returns obj.

    Example:
        >>> d = {}
        >>> setfz(d, 'foo', lambda: 1)
        {'foo': 1}
        >>> setfz(d, 'foo', lambda: 2)
        {'foo': 1}
    """
    if key not in obj:
        obj[key] = fallback()
    return obj


def setfv(obj: MutableMapping, key, fallback: Callable[[], Any]):
    """Sets obj[key] to fallback() if key doesn't exist, returns value.

    Example:
        >>> d = {}
        >>> setfv(d, 'foo', lambda: 1)
        1
        >>> setfv(d, 'foo', lambda: 2)
        1
        >>> d
        {'foo': 1}
    """
    try:
        return obj[key]
    except KeyError:
        value = obj[key] = fallback()
        return value


def has(obj: Mapping, key) -> bool:
    """Checks if obj[key] exists.

    Example:
        >>> d = {'foo': 1}
        >>> has(d, 'foo')
        True
        >>> has(d, 'bar')
        False
    """
    return key in obj


def hasd(obj: MutableMapping, key, default=None) -> bool:
    """Checks if obj[key] exists, if not, it is created with default value.

    Example:
        >>> d = {}
        >>> hasd(d, 'foo', 0)
        False
        >>> d
        {'foo': 0}
        >>> hasd(d, 'foo', 0)
        True
    """
    if key in obj:
        return True
    obj[key] = default
    return False


def hasf(obj: MutableMapping, key, fallback: Callable[[], Any]) -> bool:
    """Checks if obj[key] exists, if not, it is created with fallback().

    Example:
        >>> d = {}
        >>> hasf(d, 'foo', lambda: 0)
        False
        >>> d
        {'foo': 0}
        >>> hasf(d, 'foo', lambda: 0)
        True
    """
    if key in obj:
        return True
    obj[key] = fallback()
    return False


def incv(obj: MutableMapping[Any, TNumber], key, n: TNumber = 1):
    """Increments obj[key] by n.

    When key doesn't exist, it is created with 0 value.

    Example:
        >>> d = {}
        >>> _ = incv(d, 'foo')
        >>> d
        {'foo': 1}
    """
    value = obj[key] = obj.get(key, 0) + n
    return value


def incz(obj: MutableMapping[Any, TNumber], key, n: TNumber = 1) -> obj:
    """Increments obj[key] by n.

    When key doesn't exist, it is created with 0 value.

    Example:
        >>> d = {}
        >>> _ = incz(d, 'foo')
        >>> d
        {'foo': 1}
    """
    obj[key] = obj.get(key, 0) + n
    return obj


def decv(obj: MutableMapping[Any, TNumber], key, n: TNumber = 1):
    """Decrements obj[key] by n.

    When key doesn't exist, it is created with 0 value.

    Example:
        >>> d = {}
        >>> _ = decv(d, 'foo')
        >>> d
        {'foo': -1}
    """
    value = obj[key] = obj.get(key, 0) - n
    return value


def decz(obj: MutableMapping[Any, TNumber], key, n: TNumber = 1) -> obj:
    """Decrements obj[key] by n.

    When key doesn't exist, it is created with 0 value.

    Example:
        >>> d = {}
        >>> _ = decz(d, 'foo')
        >>> d
        {'foo': -1}
    """
    obj[key] = obj.get(key, 0) - n
    return obj


def update(obj: MutableMapping, other: Mapping) -> obj:
    """Updates obj with other, existing keys are overwritten, returns obj.

    Example:
        >>> d = {}
        >>> update(d, {'foo': 1})
        {'foo': 1}
        >>> d
        {'foo': 1}
    """
    obj.update(other)
    return obj


def merge(obj: MutableMapping, other: Mapping) -> obj:
    """Updates obj with other, existing keys are preserved, returns obj.

    Example:
        >>> d = {'foo': 1}
        >>> merge(d, {'foo': 2, 'bar': 3})
        {'foo': 1, 'bar': 3}
    """
    for key, value in other.items():
        if key not in obj:
            obj[key] = value
    return obj


def flip(obj: MutableMapping,
         skip_unhashable: bool = False,
         key_policy: Literal['keep', 'replace', 'error'] = 'error') -> obj:
    """Flips the keys and values in place.

    Args:
        obj:
            Object to flip.
        skip_unhashable:
            If True, values that cannot be keys are skipped. Default is False.
        key_policy:
            What to do with non-unique values :
                'keep': Keep the first value.
                'replace': Keep the last value.
                'error': Raise ValueError.

    Raises:
        TypeError:
            When skip_unhashable=False and a value is not hashable.
        ValueError:
            When key_policy='error' and current values are not unique (flipping
            would mean overwritting keys).

    Example:
        >>> d = dict(a=1, b=2)
        >>> flip(d)
        {1: 'a', 2: 'b'}
        >>> d = dict(a=[], b=())
        >>> flip(d, skip_unhashable=False)  # default
        Traceback (most recent call last):
        ...
        TypeError: unhashable type: 'list'
        >>> d = dict(a=[], b=())
        >>> flip(d, skip_unhashable=True)
        {(): 'b'}
        >>> d = dict(a=1, b=1)
        >>> flip(d, key_policy='error')
        Traceback (most recent call last):
        ...
        ValueError: 1 is already in the dictionary
        >>> d = dict(a=1, b=1)
        >>> flip(d, key_policy='keep')
        {1: 'a'}
        >>> d = dict(a=1, b=1)
        >>> flip(d, key_policy='replace')
        {1: 'b'}
    """
    items = list(obj.items())
    obj.clear()

    if key_policy == 'error':
        for k, v in items:
            try:
                if v in obj:
                    raise ValueError(f'{v} is already in the dictionary')
                obj[v] = k
            except TypeError:
                if not skip_unhashable:
                    raise
    elif key_policy == 'replace':
        for k, v in items:
            try:
                obj[v] = k
            except TypeError:
                if not skip_unhashable:
                    raise
    elif key_policy == 'keep':
        for k, v in items:
            try:
                if v in obj:
                    continue
                obj[v] = k
            except TypeError:
                if not skip_unhashable:
                    raise
    else:
        raise ValueError(f'unknown key policy: {key_policy}')

    return obj


def replacekey(obj: MutableMapping,
               oldkey,
               newkey,
               keeporder: bool = False,
               oldkeyerror: bool = True,
               newkeyerror: bool = True
               ) -> obj:
    """Replaces the oldkey with the newkey in the obj, returns the obj.

    If the keeporder is True, the order of the keys is preserved but for
    cost of performance (whole obj must be reconstructed). This depends on
    the actual implementation of the obj (dicts are affected).

    Args:
        obj:
            Object to replace keys in.
        oldkey:
            Old key to replace.
        newkey:
            New key to replace oldkey with.
        keeporder:
            If True, the order of the keys is preserved. Default is False.
        oldkeyerror:
            If True, raise KeyError if oldkey is not found. Default is True.
            If False, silently ignore.
        newkeyerror:
            If True, raise ValueError if newkey is in obj. Default is True.

    Example:
        >>> d = {'foo': 1, 'bar': 2}
        >>> replacekey(d, 'foo', 'zed')  # <-- zed will be last
        {'bar': 2, 'zed': 1}
        >>> replacekey(d, 'bar', 'tet', keeporder=True)  # <-- tet stays first
        {'tet': 2, 'zed': 1}
    """
    if oldkeyerror and oldkey not in obj:
        raise KeyError(oldkey)
    if newkeyerror and newkey in obj:
        raise ValueError(f'Newkey already exists: {newkey}')

    if keeporder:
        items = list(obj.items())
        obj.clear()
        for k, v in items:
            if k == oldkey:
                obj[newkey] = v
            else:
                obj[k] = v
    else:
        try:
            obj[newkey] = obj.pop(oldkey)
        except KeyError:
            pass
    return obj


def removekeys(obj: MutableMapping,
               keys: Iterable,
               keyerror: bool = True
               ) -> obj:
    """Removes the keys from the obj, returns the obj. If keyerror is False,
    missing keys are ignored, otherwise KeyError is raised.

    Args:
        obj: Object to remove keys from.
        keys: Keys to remove.
        keyerror: If True, raise KeyError if a key is not found.
                  Default is True.

    Example:
        >>> d = {'foo': 1, 'bar': 2}
        >>> removekeys(d, ['foo'])
        {'bar': 2}
        >>> removekeys(d, ['baz'])
        Traceback (most recent call last):
        ...
        KeyError: 'baz'
        >>> removekeys(d, ['baz'], keyerror=False)
        {'bar': 2}
    """
    for key in keys:
        try:
            del obj[key]
        except KeyError:
            if keyerror:
                raise
    return obj


def take(obj: MutableMapping,
         keys: Iterable,
         keyerror: bool = True
         ) -> Tuple[Any, Any]:
    """Yields key/value pairs from the obj. If keyerror is False, missing
    keys are ignored, otherwise KeyError is raised.

    Args:
        obj: Object to take keys from.
        keys: Keys to take.
        keyerror: If True, raise KeyError if a key is not found, otherwise
                  the key is ignored. Default is True.

    Yields:
        Key/value pairs.

    Example:
        >>> d = {'foo': 1, 'bar': 2}
        >>> list(take(d, ['foo']))
        [('foo', 1)]
        >>> list(take(d, ['baz']))
        Traceback (most recent call last):
        ...
        KeyError: 'baz'
        >>> list(take(d, ['baz'], keyerror=False))
        []
    """
    for key in keys:
        try:
            yield key, obj[key]
        except KeyError:
            if keyerror:
                raise


def taked(obj: MutableMapping,
          keys: Iterable,
          default=None
          ) -> Tuple[Any, Any]:
    """Yields key/value pairs from the obj, replaces missing keys
    with the default.

    Args:
        obj: Object to take keys from.
        keys: Keys to take.
        default: Default value for missing keys.

    Yields:
        Key/value pairs.

    Example:
        >>> d = {'foo': 1}
        >>> list(taked(d, ['bar'], 2))
        [('bar', 2)]
    """
    for key in keys:
        yield key, obj.get(key, default)


def takef(obj: MutableMapping,
          keys: Iterable,
          fallback: Callable[[Any], Any]
          ) -> Tuple[Any, Any]:
    """Yields key/value pairs from the obj, replaces missing keys
    with the result of fallback(key).

    Args:
        obj: Object to take keys from.
        keys: Keys to take.
        fallback: Fallback with one argument (key) to use to get value
                  for missing keys.

    Yields:
        Key/value pairs.

    Example:
        >>> d = {'foo': 1}
        >>> list(takef(d, ['bar'], lambda k: 2))
        [('bar', 2)]
    """
    for key in keys:
        try:
            yield key, obj[key]
        except KeyError:
            yield key, fallback(key)
