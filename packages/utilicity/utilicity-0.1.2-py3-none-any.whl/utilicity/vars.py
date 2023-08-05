class _Null:
    """An object that does nothing but return itself."""

    __slots__ = ()

    def __init__(self, *args, **kwargs): pass

    def __call__(self, *args, **kwargs): return self

    def __repr__(self): return 'Null()'

    def __bool__(self): return False

    def __getattr__(self, name): return self

    def __setattr__(self, name, value): return self

    def __delattr__(self, name): return self


Null = _Null()


class Var:
    __slots__ = 'value',

    def __init__(self, value=None):
        self.value = value

    def __call__(self, *args):
        if args:
            self.value = args[0]
        return self.value

    def set(self, value):
        self.value = value
        return self

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return f'Var(value={self.value!r})'


class LazyVar:
    __slots__ = '_value', '_factory'

    def __init__(self, factory: callable):
        self._factory = factory

    def __call__(self):
        try:
            return self._value
        except AttributeError:
            res = self._value = self._factory()
            return res

    @property
    def factory(self):
        return self._factory

    @property
    def is_filled(self):
        return hasattr(self, '_value')

    @property
    def value(self):
        return self()

    def clear(self):
        try:
            del self._value
        except AttributeError:
            pass
        return self

    def __str__(self) -> str:
        return str(self())

    def __repr__(self) -> str:
        return f'LazyVar(value={self()!r})'
