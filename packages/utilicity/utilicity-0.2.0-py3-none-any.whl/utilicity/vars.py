from __future__ import annotations

from typing import Callable, Generic

from utilicity import attrset
from utilicity._types import T, Self
from utilicity.sentinels import _Unset

__all__ = (
    'Null',
    'Var',
    'Bool',
    'Counter',
    'LazyVar',
)


class _Null:
    """Singleton object that does nothing but return itself.

    Example:
        >>> Null.foo[1].bar().baz
        <Null>
        >>> bool(Null)
        False
    """
    __slots__ = ()

    def __new__(cls, *args, **kwargs):
        try:
            inst = cls._instance
        except AttributeError:
            inst = cls._instance = super().__new__(cls, *args, **kwargs)
        return inst

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs) -> Self:
        return self

    def __repr__(self) -> str:
        return '<Null>'

    def __str__(self) -> str:
        return '<Null>'

    def __bool__(self) -> bool:
        return False

    def __getattr__(self, name) -> Self:
        return self

    def __setattr__(self, name, value) -> Self:
        return self

    def __delattr__(self, name) -> Self:
        return self

    def __getitem__(self, name) -> Self:
        return self

    def __setitem__(self, name, value) -> Self:
        return self

    def __delitem__(self, name) -> Self:
        return self


Null = _Null()


class Var(Generic[T]):
    """Muttable variable holder.

    Example:
        >>> var = Var(7)
        >>> var()
        7
        >>> var.set(5)
        Var(5)
        >>> var()
        5
    """
    __slots__ = 'value',

    def __init__(self, value: T = None):
        """Initializes variable with the given value.

        Args:
            value: The value to initialize this variable with.
        """
        self.value = self._coerce(value)

    def __call__(self, value: T = _Unset) -> T:
        """Returns the value of this variable, if no argument is given,
        or sets it to the given value.

        Args:
            value: If specified, the value to set this variable to.

        Example:
            >>> var = Var(7)
            >>> var()
            7
            >>> var(5)
            5
            >>> var()
            5
        """
        if value is not _Unset:
            self.value = self._coerce(value)
        return self.value

    def _coerce(self, value) -> T:
        """Coerces the value. Used in child classes for specific types."""
        return value

    def set(self, value: T) -> Self:
        """Sets the value of this variable to the given value and returns self.

        Example:
            >>> var = Var(7)
            >>> var.set(5)
            Var(5)
            >>> var()
            5
        """
        self.value = self._coerce(value)
        return self

    def setget(self, value: T) -> T:
        """Sets the value of this variable to the given value and returns it.

        Example:
            >>> var = Var(7)
            >>> var.setget(5)
            5
            >>> var()
            5
        """
        value = self.value = self._coerce(value)
        return value

    def get(self) -> T:
        """Returns the value of this variable."""
        return self.value

    def __bool__(self) -> bool:
        return bool(self.value)

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f'Var({self.value!r})'


class Bool(Var[bool]):
    """Mutable boolean object.

    Example:
        >>> b = Bool(False)
        >>> b.setgettrue()
        True
        >>> b.istrue()
        True
        >>> ~b
        False
        >>> b.invertget()
        False
    """

    def _coerce(self, value):
        return bool(value)

    def settrue(self) -> Self:
        """Sets the value of the flag to True and return self."""
        return self.set(True)

    def setgettrue(self) -> bool:
        """Sets the value of the flag to True and return the value."""
        return self(True)

    def setfalse(self) -> Self:
        """Sets the value of the flag to False and returns self."""
        return self.set(False)

    def setgetfalse(self) -> bool:
        """Sets the value of the flag to False and return the value."""
        return self(False)

    def invert(self) -> Self:
        """Flips the value of the flag and returns self.

        Example:
            >>> b = Bool(True)
            >>> b.invert() is b
            True
        """
        return self.set(~self)

    def invertget(self) -> bool:
        """Flips the value of the flag and returns the new value.

        Example:
            >>> b = Bool(True)
            >>> b.invertget()
            False
        """
        return self(~self)

    def istrue(self) -> bool:
        """Returns True if the flag is True."""
        return self.value

    def isfalse(self) -> bool:
        """Returns True if the flag is False."""
        return not self.value

    def __invert__(self) -> bool:
        """Inverts the value of the flag without changing the flag itself.

        Example:
        >>> ~Bool(True) is False
        True

        """
        return not self.value

    def __repr__(self) -> str:
        return f'Bool({self.value!r})'


class Counter(Var[int]):
    """Mutable integer object.

    Example:
    >>> i = Counter()
    >>> i.setget(1)
    1
    >>> i.incget(2)
    3
    >>> i.decget()
    2
    >>> for _ in range(3):
    ...     next(i)
    3
    4
    5
    """

    def __init__(self, value=0):
        super().__init__(value)

    def _coerce(self, value) -> int:
        return int(value)

    def inc(self, n: int = 1) -> Self:
        """Increments value of counter by n and returns self."""
        return self.set(self.value + n)

    def incget(self, n: int = 1) -> int:
        """Increments value of counter by n and returns the new value."""
        return self(self.value + n)

    def dec(self, n: int = 1) -> Self:
        """Decrements value of counter by n and returns self."""
        return self.set(self.value - n)

    def decget(self, n: int = 1) -> int:
        """Decrements value of counter by n and returns the new value."""
        return self(self.value - n)

    __next__ = incget

    def __int__(self) -> int:
        return self.value

    def __repr__(self) -> str:
        """Returns a string representation of the counter.

        Example:
            >>> repr(Counter(0))
            'Counter(0)'
        """
        return f'Counter({self.value!r})'


class LazyVar(Generic[T]):
    """Lazy loaded variable holder.

    The value is retrieved by calling the factory function when it's needed.

    Example:
        >>> var = LazyVar(lambda: print('computing') or 7)
        >>> var()
        computing
        7
        >>> var()
        7
        >>> _ = var.clear()
        >>> var()
        computing
        7
    """
    __slots__ = '_value', 'factory'

    def __init__(self, factory: Callable[[], T]):
        """Factory function that will be called to retrieve the value.

        Args:
            factory: The function that will be called to retrieve the value.
        """
        self.factory = factory

    def __call__(self) -> T:
        """Returns the value of this variable. If the value has not yet been
        retrieved, it is computed by calling the factory.

        Example:
            >>> var = LazyVar(lambda: print('computing') or 7)
            >>> var()
            computing
            7
            >>> var()
            7
        """
        return attrset(self, '_value', self.factory)

    @property
    def has_value(self) -> bool:
        """True if the value is set (after calling the factory).

        Example:
            >>> lazy_var = LazyVar(lambda: 7)
            >>> lazy_var.has_value
            False
            >>> lazy_var()
            7
            >>> lazy_var.has_value
            True
        """
        return hasattr(self, '_value')

    @property
    def value(self) -> T:
        """Returns the value of this variable. If the value has not yet been
        retrieved, it is computed by calling the factory.
        """
        return self()

    def get(self) -> T:
        """Returns the value of this variable. If the value has not yet been
        retrieved, it is computed by calling the factory.
        """
        return self()

    def clear(self) -> Self:
        """Clears the value of this variable.

        Example:
            >>> lazy_var = LazyVar(Counter().incget)
            >>> lazy_var()
            1
            >>> lazy_var()
            1
            >>> _ = lazy_var.clear()
            >>> lazy_var()
            2
        """
        try:
            del self._value
        except AttributeError:
            pass
        return self

    def __str__(self) -> str:
        return str(self())

    def __repr__(self) -> str:
        """Returns the representation of the value.

        LazyVar(*...) if the value has not yet been retrieved,
        LazyVar(...) if the value has been retrieved.

        Example:
            >>> var = LazyVar(lambda: 7)
            >>> repr(var)  # doctest: +ELLIPSIS
            'LazyVar(*<function <lambda> at ...)'
            >>> _ = var()
            >>> repr(var)
            'LazyVar(7)'
        """
        if self.has_value:
            return f'LazyVar({self._value!r})'
        return f'LazyVar(*{self.factory!r})'
