import string
from unicodedata import normalize
from base64 import b64decode, b64encode
from itertools import chain, cycle, islice, product, tee
from math import ceil, log
from re import VERBOSE, compile, escape, finditer, split

from typing import Callable, Iterable, Mapping, Sequence, Union

__all__ = (
    'anycoder',
    'boolify',
    'charlist_factory',
    'replace',
)


def boolify(s: str):
    """Converts some textual representations to bool.

    String is converted to lowercase and trimmed first.

    True values:
        '1', 'on', 'yes', 'true', 'y', 't', '+'
    False values:
        '0', 'off', 'no', 'false', 'n', 'f', '-'
    If no bool representation is found, None is returned.

    Example:
    >>> assert boolify('true') is True
    >>> assert boolify('0') is False
    >>> assert boolify('foo') is None

    :param s: string to be converted
    :return: bool|None

    """
    s = str(s).strip().lower()
    if s in ('1', 'on', 'yes', 'true', 'y', 't', '+'):
        return True
    elif s in ('0', 'off', 'no', 'false', 'n', 'f', '-'):
        return False
    return None


def asciify(s: str):
    """Basic transliteration of some unicode chars to ascii.

    If it does not work for you as expected, try more sofisticated
    librariers (e.g. Unidecode) that can handle cyrillic, chinesse, etc.

    Example:
        >>> asciify('ěščřžýáíéúůťňäöüĚŠČŘŽÝÁÍÉÚŮŤŇÄÖÜ')
        'escrzyaieuutnaouESCRZYAIEUUTNAOU'
    """
    return normalize('NFKD', s).encode('ascii', errors='ignore').decode()


def _replace_sub(old):
    return compile('|'.join(escape(o) for o in old)).sub


def replace(s: str,
            old: Union[str, Iterable[str], Mapping[str, str]],
            new: Union[str, Iterable[str], Callable[[str], str]] = '') -> str:
    """More powerful version of str.replace() that allows multiple replacements
    at once (atomically).

    Args:
        s: input string
        old: part(s) to be replaced
        new: part(s) that will replace old one(s).
             if old is str and new iterable, replaced values will rotate

    Examples:
        >>> s = 'solid spend solid spend'

        # same as str.replace
        >>> replace(s, 'spend', 'foo')
        'solid foo solid foo'

        # replaces 'solid' by rotating 'foo' and 'bar'
        >>> replace(s, 'solid', ['foo', 'bar'])
        'foo spend bar spend'

        # replaces 'solid' by function call
        >>> replace(s, 'solid', lambda r: r[::-1])
        'dilos spend dilos spend'

        >>> s = 'solid spend'

        # replaces multiple strings with 'sol'
        >>> replace(s, ['so', 'sollid'], 'sol')
        'sollid spend'

        # replaces old with new 1:1
        >>> replace(s, ['solid', 'spend'], ['foo', 'bar'])
        'foo bar'

        # replaces old (keys) with new (values)
        >>> replace(s, {'solid': 'spend', 'spend': 'foo'})
        'spend foo'
    """
    if isinstance(old, str):
        if isinstance(new, str):
            return s.replace(old, new)
        elif isinstance(new, Callable):
            p = _replace_sub([old])
            return p(lambda m: new(m[0]), s)
        elif isinstance(new, Iterable):
            splits = s.split(old)
            return ''.join(islice(
                chain(*zip(splits, cycle(new))),
                len(splits) * 2 - 1)
            )
        return s.replace(old, str(new))

    elif isinstance(old, Mapping):
        p = _replace_sub(old.keys())
        return p(lambda m: escape(str(old[m[0]])), s)

    elif isinstance(old, Iterable):
        if not isinstance(old, Sequence):
            old = tuple(old)
        p = _replace_sub(old)
        if isinstance(new, str):
            return p(escape(new), s)
        elif isinstance(new, Callable):
            return p(lambda m: new(m[0]), s)
        elif isinstance(new, Iterable):
            d = dict(zip(old, new))
            return p(lambda m: escape(d[m[0]]), s)
        return p(escape(str(new)), s)

    return replace(str(old), new)


def base62_encode(s: bytes):
    """Encodes bytes se they are represented with only letters and digits.

    It uses base64 encoding but replaces symbols '+' and '/' with
    sequences '7c' and '7b'. 7 itself is replaced with '7a'.
    Also removes padding '=' characters.

    Example:
        >>> base62_encode(b'hello')
        b'aGVsbG8'
        >>> base62_encode('éíáýžřčšw'.encode('utf-8'))
        b'w6nDrcOhw7a3FvsWZxI3FoXc'
    """
    s = b64encode(s)
    s = s.replace(b'7', b'7a')  # 7 seems to be least used
    s = s.replace(b'/', b'7b')
    s = s.replace(b'+', b'7c')
    return s.rstrip(b'=')


def base62_decode(s: bytes):
    """Decodes bytes previously encoded with base62_encode.

    It uses base64 encoding but replaces symbols '+' and '/' with
    sequences '7c' and '7b'. 7 itself is replaced with '7a'.
    Also removes padding '=' characters.

    Example:
        >>> base62_decode(b'aGVsbG8')
        b'hello'
        >>> base62_decode(b'w6nDrcOhw7a3FvsWZxI3FoXc').decode('utf-8')
        'éíáýžřčšw'
    """
    s = s.replace(b'7c', b'+')
    s = s.replace(b'7b', b'/')
    s = s.replace(b'7a', b'7')
    if rpad := len(s) % 4:
        s = s + b'=' * (4 - rpad)
    return b64decode(s)


def decimal_convertor(target_digits: bytes):
    digits_length = len(target_digits)
    index = {v: i for i, v in enumerate(target_digits)}

    def from_dec(dec: int, zfill=None):
        buff = bytearray()
        buff_append = buff.append
        while dec > 0:
            dec, m = divmod(dec, digits_length)
            buff_append(target_digits[m])
        buff.reverse()
        if zfill:
            buff = buff.rjust(zfill, target_digits[:1])
        return bytes(buff)

    def to_dec(s: bytes):
        dec = 0
        for i, c in enumerate(reversed(s)):
            dec += index[c] * (digits_length ** i)
        return dec

    return from_dec, to_dec


def anycoder(dst_alphabet: bytes, src_alphabet: bytes = None):
    if src_alphabet is None:
        src_alphabet = bytes(i for i in range(256))
    src_len = len(src_alphabet)
    letters_needed = ceil(log(src_len, len(dst_alphabet)))

    enc_table = {}
    for i, word in enumerate(product(*tee(dst_alphabet, letters_needed))):
        if i < src_len:
            enc_table[src_alphabet[i]] = bytes(word)
    dec_table = {v: k for k, v in enc_table.items()}

    def encode(s: bytes):
        return b''.join(enc_table[b] for b in s)

    def decode(s: bytes):
        if len(s) % letters_needed:
            raise ValueError('Invalid data format')
        s = memoryview(s)

        i = 0
        buffer = bytearray()
        append = buffer.append
        while True:
            idx = i * letters_needed
            word = s[idx:idx + letters_needed]
            if not word:
                break
            append(dec_table[word])
            i += 1
        return bytes(buffer)

    return encode, decode


def charlist_factory(definition: str) -> str:
    r"""Generates list of characters according to the definition.
    Definition can contain single chars, ranges (e.g. 'a-z', '0-9', 'Z-A'),
    or predefined constats:
        \- for the dash itself (not as range delimiter)
        \a - same as a-z
        \z - same as z-a
        \A - same as A-Z
        \Z - same as Z-A
        \d - same as 0-9
        \D - same as 9-0
        \x - same as 0-9a-f
        \X - same as f-a0-9
        \o - same as 0-7
        \O - same as 7-0
        \s - same as !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ or !-/:-@[-`{-~
        \S - same as reversed \s
        \p - same as string.printable
        \P - same as reversed \p

        TODO:
        .. whitespaces ..
        \w - same as a-zA-Z0-9
        \W - same as reversed \w

    Example:
        >>> charlist_factory('a-z')
        'abcdefghijklmnopqrstuvwxyz'
        >>> charlist_factory('a-zA-Z')
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        >>> charlist_factory('0-9xyz')
        '0123456789xyz'
        >>> charlist_factory(r'\A')
        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        >>> charlist_factory(r'\P')
        '\x0c\x0b\r\n\t ~}|{`_^]\\[@?>=<;:/.-,+*)(\'&%$#"!ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba9876543210'
    """

    def tokenize():
        matches = finditer(r'''
            \\(?P<esc>.)            | # esc
            (?P<range>.-.)          | # range
            (?P<char>.)               # everything else
        ''', definition, VERBOSE)

        for m in matches:
            yield m.lastgroup, m[m.lastgroup]

    res = []
    for token, val in tokenize():
        if token == 'range':
            a, b = split(r'(?<=.)-(?=.)', val)
            a, b = ord(a), ord(b)
            step = 1 if a <= b else -1
            res.extend(chr(c) for c in range(a, b + step, step))
        elif token == 'esc':
            if val == 'a':
                res.extend(string.ascii_lowercase)
            elif val == 'z':
                res.extend(reversed(string.ascii_lowercase))
            elif val == 'A':
                res.extend(string.ascii_uppercase)
            elif val == 'Z':
                res.extend(reversed(string.ascii_uppercase))
            elif val == 'd':
                res.extend(string.digits)
            elif val == 'D':
                res.extend(reversed(string.digits))
            elif val == 'x':
                res.extend(string.hexdigits[:-6])
            elif val == 'X':
                res.extend(reversed(string.hexdigits[:-6]))
            elif val == 'o':
                res.extend(string.octdigits)
            elif val == 'O':
                res.extend(reversed(string.octdigits))
            elif val == 's':
                res.extend(string.punctuation)
            elif val == 'S':
                res.extend(reversed(string.punctuation))
            elif val == 'p':
                res.extend(string.printable)
            elif val == 'P':
                res.extend(reversed(string.printable))
            else:
                res.append(val)
        else:
            res.append(val)

    return ''.join(res)
