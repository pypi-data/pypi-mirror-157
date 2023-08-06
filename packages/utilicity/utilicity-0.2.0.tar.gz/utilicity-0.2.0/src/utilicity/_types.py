from typing import (
    Any,
    Callable,
    Hashable,
    Iterable,
    Literal,
    Mapping,
    Pattern,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    _Final,
    _tp_cache
)

T = TypeVar('T')
"""Type variable for use in type hints."""

TCallableOrAny = Union[Callable, Any]
"""Represents an argument that will be replaced by the result of calling itself, 
if it is callable, otherwise remains unchanged.

Same as:
arg = arg() if callable(arg) else arg
"""

TCallableOrMethodName = Union[str, Callable]

TMappable = Union[Mapping, Iterable[Tuple[Hashable, Any]]]

TMode = Literal['apply', 'call']

TSeparator = Union[str, Pattern]
TPath = Union[str, Sequence]

TNumber = Union[int, float, complex]
"""Number type."""


class _SpecialForm(_Final, _root=True):
    __slots__ = ('_name', '__doc__', '_getitem')

    def __init__(self, getitem):
        self._getitem = getitem
        self._name = getitem.__name__
        self.__doc__ = getitem.__doc__

    def __getattr__(self, item):
        if item in {'__name__', '__qualname__'}:
            return self._name

        raise AttributeError(item)

    def __mro_entries__(self, bases):
        raise TypeError(f"Cannot subclass {self!r}")

    def __repr__(self):
        return f'typing_extensions.{self._name}'

    def __reduce__(self):
        return self._name

    def __call__(self, *args, **kwds):
        raise TypeError(f"Cannot instantiate {self!r}")

    def __or__(self, other):
        return Union[self, other]

    def __ror__(self, other):
        return Union[other, self]

    def __instancecheck__(self, obj):
        raise TypeError(f"{self} cannot be used with isinstance()")

    def __subclasscheck__(self, cls):
        raise TypeError(f"{self} cannot be used with issubclass()")

    @_tp_cache
    def __getitem__(self, parameters):
        return self._getitem(self, parameters)


@_SpecialForm
def Self(self, params):
    """Used to spell the type of "self" in classes.

    Example:
        from typing import Self

        class ReturnsSelf:
            def parse(self, data: bytes) -> Self:
            ...
            return self
    """

    raise TypeError(f"{self} is not subscriptable")
