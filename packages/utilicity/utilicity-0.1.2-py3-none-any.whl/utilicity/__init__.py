__VERSION__ = '0.1.2'


def throw(exc: BaseException):
    """Raising exceptions via function.

    Example
    -------
    >>> False or throw(ValueError())
    Traceback (most recent call last):
    ...
    ValueError
    """
    raise exc


def getresult(arg):
    """Returns a result of calling arg (*if callable*) or arg itself.

    Example
    -------
    >>> getresult(lambda: True)
    True
    >>> getresult(True)
    True
    """
    return arg() if callable(arg) else arg


def attrget(obj, attr, fallback: callable):
    """Returns obj.attr when it exists, otherwise returns result of fallback().

    Example
    -------
    >>> o = object()
    >>> attrget(o, 'x', lambda: 1)
    1
    """
    try:
        return getattr(obj, attr)
    except AttributeError:
        return fallback()


def attrset(obj, attr, fallback=None):
    """Does obj.attr = fallback() if attr doesn't exist.
    Returns the content of attr.

    Example
    -------
    >>> class Obj: pass
    >>> obj = Obj()
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


def itemget(obj, key, fallback):
    """Returns obj[key], if exists, or fallback().

    Example
    -------
    >>> itemget({}, 'foo', lambda: True)
    True
    """
    try:
        return obj[key]
    except (KeyError, IndexError):
        return fallback()


def itemset(obj, key, fallback=None):
    """Does obj[key] = fallback() if key doesn't exist. Returns the value.

    Example
    -------
    >>> d = {}
    >>> itemset(d, 'foo', lambda: True)
    True
    >>> d
    {'foo': True}
    """
    try:
        return obj[key]
    except KeyError:
        obj[key] = (res := getresult(fallback))
        return res
