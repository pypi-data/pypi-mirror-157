from functools import partial

from typing import Callable, Literal, Union

from . import getresult
from .vars import Var

__all__ = 'Fluent', 'Q', 'Break'

TPredicate = Union[Callable[[], bool], bool]
TMode = Literal['apply', 'call']


class Q:
    """The class Q defines a callable object.
    When called, it will execute the callback function
    that was passed to its constructor.
    It also provides logical operators (and, or, not)
    that can be used to combine multiple callbacks
    into a single callback.
    """

    def __init__(self, callback: Callable):
        self._callback = callback

    def __call__(self):
        return self._callback()

    def __invert__(self):
        return Q(lambda: not self())

    def __and__(self, other: 'Q'):
        return Q(lambda: self() and other())

    def __or__(self, other: 'Q'):
        return Q(lambda: self() or other())


class _Break(Exception):
    def __init__(self, n=1):
        self.n = n


def Break(n: int = 1):
    """Call to break within fluent loops."""
    raise _Break(n)


class _ReturnValue(Exception):
    def __init__(self, val):
        self.val = val


class Fluent:
    """Allows to dynamically chain methods of a target object
    and controlling flow with conditions/loops/etc.

    Example
    -------
    >>> query = (Fluent(target=Blog.objects.all(), mode='apply')
            .If(lambda: not getenv('DEBUG'))
                .filter(published=True)
            .End()
        )()
    """

    def __init__(self,
                 target=None,
                 mode: TMode = 'apply'):
        self.__fluent_parent__ = None
        self.__fluent_children__ = []
        self.__fluent_target__ = None if target is None else Var(target)
        self.__fluent_mode__ = mode

    def __call__(self):
        root = self
        while root.__fluent_parent__:
            root = root.__fluent_parent__

        try:
            root.__fluent_exec__()
        except _ReturnValue as e:
            return e.val
        return getresult(self.__fluent_target__)

    def __fluent_add_child__(self, child: 'Fluent'):
        self.__fluent_children__.append(child)
        child.__fluent_on_added__(self)
        return child

    def __fluent_on_added__(self, parent: 'Fluent'):
        self.__fluent_parent__ = parent
        self.__fluent_target__ = parent.__fluent_target__
        if self.__fluent_mode__ is None:
            self.__fluent_mode__ = parent.__fluent_mode__

    def __fluent_exec__(self):
        for child in self.__fluent_children__:
            child.__fluent_exec__()

    def Do(self, action: Callable):
        """Executes arbitrary action."""
        self.__fluent_add_child__(_Do(action))
        return self

    def Return(self, action: Callable):
        """Executes the given action and returns the result.
        Also stops further execution (same as return inside function)."""
        self.__fluent_add_child__(_Return(action))
        return self

    def Call(self, func: Union[str, Callable], *args, **kwargs):
        """Executes func on target.

        If func is a string, it will be treated as a method name:
            target.func(*args, **kwargs)

        If func is callable, it will be executed directly
        with target as the first argument:
            func(target, *args, **kwargs)

        """
        self.__fluent_add_child__(_Call(func, args, kwargs))
        return self

    def Apply(self, func: Union[str, Callable], *args, **kwargs):
        """Executes func on target and replaces target with the result.

        If func is a string, it will be treated as a method name:
            target = target.func(*args, **kwargs)

        If func is callable, it will be executed directly
        with target as the first argument:
            target = func(target, *args, **kwargs)

        """
        self.__fluent_add_child__(_Apply(func, args, kwargs))
        return self

    def Block(self, mode: TMode = None):
        """Creates a block with different context."""
        return self.__fluent_add_child__(_Block(mode=mode))

    def If(self, predicate) -> '_If':
        """Conditionally executes the code within If block."""
        return self.__fluent_add_child__(_If(predicate))

    def Try(self) -> '_Try':
        """Tries to execute the code within Try block."""
        return self.__fluent_add_child__(_Try())

    def While(self, predicate) -> '_While':
        """Repeats the code within While block while predicate is truthful."""
        return self.__fluent_add_child__(_While(predicate))

    def DoWhile(self, predicate) -> '_DoWhile':
        """Repeats the code within While block while predicate is truthful.
        The code is executed at least once."""
        return self.__fluent_add_child__(_DoWhile(predicate))

    def Repeat(self, n) -> '_Repeat':
        """Repeats the code within Repeat block n times."""
        return self.__fluent_add_child__(_Repeat(n))

    def __getattr__(self, func):
        """Shortcut for .Apply/Call(func, *args, **kwargs). Which method
        is used depends on the mode.

        Example
        -------
        >>> (Fluent('hello', mode='apply')
                .upper()
            )()
        >>> 'HELLO'
        """
        if self.__fluent_target__ is None:
            raise AttributeError(func)
        elif self.__fluent_mode__ == 'apply':
            return partial(self.Apply, func)
        elif self.__fluent_mode__ == 'call':
            return partial(self.Call, func)

    def __str__(self):
        return f'{self.__class__.__name__}()'

    # Only for debugging purposes:
    # PyCharm crashes with custom __getattr__() and absent __len__()
    def __len__(self):
        return len(self.__fluent_children__) or 1


class _Call(Fluent):
    def __init__(self, func, args, kwargs):
        super().__init__()
        self.__fluent_args__ = func, args, kwargs

    def __fluent_exec__(self):
        func, args, kwargs = self.__fluent_args__
        target = self.__fluent_target__.value
        if isinstance(func, str):
            return getattr(target, func)(*args, **kwargs)
        else:
            return func(target, *args, **kwargs)


class _Apply(_Call):
    def __fluent_exec__(self):
        return self.__fluent_target__(super().__fluent_exec__())


class _Do(Fluent):
    def __init__(self, callback: Callable):
        super().__init__()
        self.__fluent_callback__ = callback

    def __fluent_exec__(self):
        return self.__fluent_callback__()


class _Return(Fluent):
    def __init__(self, value):
        super().__init__()
        self.__fluent_value__ = value

    def __fluent_exec__(self):
        raise _ReturnValue(getresult(self.__fluent_value__))


class _Predicate(Fluent):
    def __init__(self, predicate: TPredicate):
        super().__init__()
        self.__fluent_predicate__ = predicate


class _Block(Fluent):
    def __init__(self, mode: TMode = None):
        super().__init__(None, mode)

    def End(self) -> 'Fluent':
        """Ends the block."""
        return self.__fluent_parent__


class _If(_Predicate, _Block):
    def __init__(self, predicate: TPredicate):
        super().__init__(predicate)
        self.__fluent_branches__ = [(predicate, self.__fluent_children__)]
        self.__fluent_last_clause__ = 'If'

    def __fluent_exec__(self):
        for args, children in self.__fluent_branches__:
            if getresult(args):
                self.__fluent_children__ = children
                super().__fluent_exec__()
                break

    def Elif(self, predicate: TPredicate):
        if self.__fluent_last_clause__ == 'Else':
            raise RuntimeError('Cannot use Elif() after Else().')

        self.__fluent_children__ = []
        self.__fluent_branches__.append((predicate, self.__fluent_children__))
        self.__fluent_last_clause__ = 'Elif'
        return self

    def Else(self):
        if self.__fluent_last_clause__ == 'Else':
            raise RuntimeError('Else() can be used once per If() block only.')
        self.__fluent_children__ = []
        self.__fluent_branches__.append((True, self.__fluent_children__))
        self.__fluent_last_clause__ = 'Else'
        return self


class _Try(_Block):
    def __init__(self):
        super().__init__()
        self.__fluent_try__ = self.__fluent_children__
        self.__fluent_excepts__ = []
        self.__fluent_else__ = []
        self.__fluent_finally__ = []
        self.__fluent_last_clause__ = 'Try'

    def __fluent_exec__(self):
        self.__fluent_children__ = self.__fluent_try__
        try:
            super().__fluent_exec__()
        except _ReturnValue:
            raise
        except BaseException as e:
            for exceptions, children in self.__fluent_excepts__:
                if isinstance(e, exceptions):
                    self.__fluent_children__ = children
                    super().__fluent_exec__()
                    break
            else:
                raise
        else:
            self.__fluent_children__ = self.__fluent_else__
            super().__fluent_exec__()
        finally:
            self.__fluent_children__ = self.__fluent_finally__
            super().__fluent_exec__()

    def Except(self, *exceptions: Exception):
        if self.__fluent_last_clause__ in ('Else', 'Finally'):
            raise RuntimeError(f'Except() can\'t be used '
                               f'after {self.__fluent_last_clause__}().')

        self.__fluent_children__ = []
        self.__fluent_excepts__.append((exceptions, self.__fluent_children__))
        self.__fluent_last_clause__ = 'Except'
        return self

    def Else(self):
        if self.__fluent_last_clause__ == 'Else':
            raise RuntimeError('Else() can be used once per Try() block only.')
        elif self.__fluent_last_clause__ == 'Finally':
            raise RuntimeError('Else() can\'t be used after Finally().')
        self.__fluent_children__ = self.__fluent_else__
        self.__fluent_last_clause__ = 'Else'
        return self

    def Finally(self):
        if self.__fluent_last_clause__ == 'Finally':
            raise RuntimeError('Finally() can be used '
                               'once per Try() block only.')
        self.__fluent_children__ = self.__fluent_finally__
        self.__fluent_last_clause__ = 'Finally'
        return self


class _While(_Predicate, _Block):
    def __fluent_exec__(self):
        predicate = self.__fluent_predicate__
        try:
            while getresult(predicate):
                super().__fluent_exec__()
        except _Break as e:
            if n := e.n - 1:
                raise _Break(n)


class _DoWhile(_Predicate, _Block):
    def __fluent_exec__(self):
        predicate = self.__fluent_predicate__
        try:
            while True:
                super().__fluent_exec__()
                if not getresult(predicate):
                    break
        except _Break as e:
            if n := e.n - 1:
                raise _Break(n)


class _Repeat(_Block):
    def __init__(self, n: int):
        super().__init__()
        self.__fluent_n__ = n

    def __fluent_exec__(self):
        try:
            for i in range(getresult(self.__fluent_n__)):
                super().__fluent_exec__()
        except _Break as e:
            if n := e.n - 1:
                raise _Break(n)
