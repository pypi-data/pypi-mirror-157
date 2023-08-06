import re
from functools import lru_cache
from typing import Mapping, Sequence, Union

from utilicity._types import TPath, TSeparator

__all__ = (
    'lookup',
    'lookup_default',
    'lookup_fallback',
)


# class _PathPart:
#     pass
#
#
# class PathKey(_PathPart, str):
#     pass
#
#
# class PathKeyInt(_PathPart, int):
#     pass
#
#
# class PathKeyFloat(_PathPart, float):
#     pass
#
#
# class PathIndex(_PathPart, int):
#     pass
#

def _tokenize_path(path: str, sep: str = '.', esc: str = '\\', fmt: str = ':'):
    """Tokenize a path string."""
    if sep == esc or sep == fmt or esc == fmt:
        raise ValueError('sep, esc, fmt must not be same')

    sep = re.escape(sep)
    esc = re.escape(esc)
    fmt = re.escape(fmt)
    matches = re.finditer(fr'''
        {esc}(?P<esc>({sep}|{esc}|{fmt}|\[))    | # esc sequences
        {fmt}(?P<fmt>[sdf])(?={sep}|\[|$)           | # format
        (?P<sep>{sep})                          | # separator
        \[(?P<idx>\d+)]                         | # index
        (?P<char>.)                               # everything else
    ''', path, re.VERBOSE)

    return [(m.lastgroup, m[m.lastgroup]) for m in matches]


@lru_cache()
def _split_path(path: str, sep: str = '.', esc: str = '\\', fmt: str = ':'):
    """Split a path string into a list of path parts.

    >>> _split_path('a.b.c')
    ['a', 'b', 'c']
    >>> _split_path('a/b/c', sep='/')
    ['a', 'b', 'c']
    >>> _split_path('a.1:d.2.0:f')
    ['a', 1, '2', 0.0]
    >>> _split_path('a:1%d:2:0%f', ':', fmt='%')
    ['a', 1, '2', 0.0]
    """
    if not path:
        return [path]
    elif len(sep) == 0:  # split path on chars
        return list(path)
    elif sep == esc:
        return path.split(sep)

    prev = None
    splits, split = [], []
    for token, val in _tokenize_path(path, sep, esc, fmt):
        if token in ('char', 'esc'):
            split.append(val)
        elif token == 'sep':
            if prev not in ('idx', 'fmt'):
                splits.append(''.join(split))
                split.clear()
        elif token == 'idx':
            if prev not in ('idx', 'fmt', None):
                splits.append(''.join(split))
                split.clear()
            splits.append(int(val))
        elif token == 'fmt':
            # if prev not in ('idx', None):
            if val == 's':
                splits.append(''.join(split))
            elif val == 'd':
                splits.append(int(''.join(split) or 0))
            elif val == 'f':
                splits.append(float(''.join(split) or 0))
            else:
                raise NotImplementedError(f'unknown format: {val}')
            split.clear()
        else:
            raise NotImplementedError(f'unknown token: {token}')
        prev = token
    else:
        if split or prev == 'sep':
            splits.append(''.join(split))

    return splits


def _parse_lookup_path(path: TPath, sep: TSeparator = '.', esc: str = '\\', fmt: str = ':'):
    if isinstance(path, str):
        if isinstance(sep, re.Pattern):
            path = sep.split(path)
        else:
            path = _split_path(path, sep, esc, fmt)
    return path


def parse_lookup_path(path: str, sep: str = '.', esc: str = '\\', fmt: str = ':'):
    return _split_path(path, sep, esc, fmt)


def lookup(d: Union[Mapping, Sequence], path: TPath, **path_kwargs):
    """Lookups a value in a dictionary.

    Example:
    >>> lookup({'a': {'b': {'c': 1}}}, 'a.b.c')
    1
    >>> lookup({'a': {'b': {'c': 1}}}, 'a.b.d')
    Traceback (most recent call last):
    ...
    KeyError: 'd'
    """

    cursor = d
    for part in _parse_lookup_path(path, **path_kwargs):
        try:
            cursor = cursor[part]
        except IndexError:
            raise KeyError(part) from None
    return cursor


def lookup_default(d: Union[Mapping, Sequence], path: TPath, default=None, **path_kwargs):
    cursor = d
    for part in _parse_lookup_path(path, **path_kwargs):
        try:
            cursor = cursor[part]
        except (KeyError, IndexError):
            return default
    return cursor


def lookup_fallback(d: Union[Mapping, Sequence], path: TPath, fallback: callable, **path_kwargs):
    cursor = d
    for part in _parse_lookup_path(path, **path_kwargs):
        try:
            cursor = cursor[part]
        except (KeyError, IndexError):
            return fallback(part)
    return cursor
