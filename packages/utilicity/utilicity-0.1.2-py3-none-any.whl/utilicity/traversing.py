import re
from functools import lru_cache

from typing import Sequence, Union


__all__ = 'lookup', 'lookup_default', 'lookup_fallback'

TSeparator = Union[str, re.Pattern]
TPath = Union[str, Sequence]


@lru_cache()
def _parse_lookup_path(path: TPath, sep: TSeparator = '.', esc: str = '\\'):
    def _tokenize_path(path: str, sep: str = '.', esc: str = '\\'):
        sep = re.escape(sep)
        esc = re.escape(esc)
        matches = re.finditer(fr'''
            {esc}(?P<esc>({sep}|{esc}|\[))      | # esc sequences
            (?P<sep>{sep})                      | # separator
            \[(?P<idx>\d+)]                     | # index
            (?P<char>.)                           # everything else
        ''', path, re.VERBOSE)

        return [(m.lastgroup, m[m.lastgroup]) for m in matches]

    def _split_path(path: str, sep: str = '.', esc: str = '\\'):
        if not path:
            return [path]
        elif len(sep) == 0:  # split path on chars
            return list(path)
        elif sep == esc:
            return path.split(sep)

        splits = []
        split = []
        prev = None
        for token, val in _tokenize_path(path, sep, esc):
            if token in ('char', 'esc'):
                split.append(val)
            elif token == 'sep':
                if prev != 'idx':
                    splits.append(''.join(split))
                    split.clear()
            elif token == 'idx':
                if prev not in ('idx', None):
                    splits.append(''.join(split))
                    split.clear()
                splits.append(int(val))
            else:
                raise NotImplementedError(f'unknown token: {token}')
            prev = token
        else:
            if split or prev == 'sep':
                splits.append(''.join(split))

        return splits

    if isinstance(path, str):
        if isinstance(sep, re.Pattern):
            path = sep.split(path)
        else:
            path = _split_path(path, sep, esc)
    return path


def lookup(d, path: TPath, **path_kwargs):
    cursor = d
    for part in _parse_lookup_path(path, **path_kwargs):
        try:
            cursor = cursor[part]
        except IndexError:
            raise KeyError(part) from None
    return cursor


def lookup_default(d, path: TPath, default=None, **path_kwargs):
    cursor = d
    for part in _parse_lookup_path(path, **path_kwargs):
        try:
            cursor = cursor[part]
        except (KeyError, IndexError):
            return default
    return cursor


def lookup_fallback(d, path: TPath, fallback: callable, **path_kwargs):
    cursor = d
    for part in _parse_lookup_path(path, **path_kwargs):
        try:
            cursor = cursor[part]
        except (KeyError, IndexError):
            return fallback(part)
    return cursor
