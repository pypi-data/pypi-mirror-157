from functools import partial

from typing import Callable

from utilicity import perform
from utilicity.items.helpers import setfz
from utilicity._types import Self, TCallableOrAny, TCallableOrMethodName, TMode
from utilicity.helpers import getresult, ifset
from utilicity.vars import Var

__all__ = (
    'Break',
    'Context',
    'Continue',
    'Fluent',
    'P',
)


class P:
    """Predicate object.

    When called, it will execute the callback function that was passed
    to the constructor. It also provides logical operators (and, or, not)
    that can be used to combine multiple callbacks into a single callback.

    Example:
        >>> (P(lambda: False) | P(lambda: True))()
        True
        >>> (P(lambda: False) & P(lambda: True))()
        False
    """

    def __init__(self, callback: Callable[[], bool]):
        self._callback = callback

    def __call__(self):
        return bool(self._callback())

    def __invert__(self):
        return P(lambda: not self())

    def __and__(self, other: 'P'):
        return P(lambda: self() and other())

    def __or__(self, other: 'P'):
        return P(lambda: self() or other())


class _ReturnValue(Exception):
    def __init__(self, val):
        self.val = val


class _Break(Exception):
    def __init__(self, n=1):
        self.n = n


def Break(n: int = 1):
    """Call within fluent expression to break a loop.

    Args:
        n: Number of loops to break.

    Example:
        >>> (Fluent()
        ...     .Repeat(lambda: 3)
        ...         .While(lambda: True)
        ...             .DoWhile(lambda: True)
        ...                 .Do(lambda: print('X', end='') or Break(3))
        ...             .End()
        ...         .End()
        ...     .End()
        ... )()
        X
    """
    raise _Break(n)


class _Continue(Exception):
    def __init__(self, n=1):
        if n < 1:
            raise ValueError('n must be >= 1')
        self.n = n


def Continue(n: int = 1):
    """Call within fluent expression to continue the Nth loop.

    Args:
        n: Number of the loop that should continue.

    Example:
        >>> (Fluent()
        ...     .Repeat(lambda: 4)
        ...         .Do(lambda: print('X', end='') or Continue(1))
        ...         .Do(lambda: print('O', end=''))  # Never executed
        ...     .End()
        ... )()
        XXXX
        >>> (Fluent()
        ...     .Repeat(lambda: 3)
        ...         .Repeat(lambda: 3)
        ...             .Do(lambda: print('X', end='') or Continue(2))
        ...         .End()
        ...         .Do(lambda: print('O', end=''))  # Never executed
        ...     .End()
        ... )()
        XXX
        >>> a = [1]
        >>> (Fluent()
        ...     .While(lambda: len(a))
        ...         .Do(lambda: print('X', end='') or a.clear() or Continue(1))
        ...         .Do(lambda: print('O', end=''))  # Never executed
        ...     .End()
        ... )()
        X
        >>> a = [1]
        >>> (Fluent()
        ...     .DoWhile(lambda: len(a))
        ...         .If(lambda: not a)
        ...             .Do(lambda: Break(1))
        ...         .End()
        ...         .Do(lambda: print('X', end='') or a.clear() or Continue(1))
        ...         .Do(lambda: print('O', end=''))  # Never executed
        ...     .End()
        ... )()
        X
        >>> (Fluent()
        ...     .While(True)
        ...         .Do(lambda: print('X', end='') or Continue(3))
        ...     .End()
        ... )()
        Traceback (most recent call last):
        ...
        RuntimeError: Continue() - given n is greater than the number of available loops
    """
    raise _Continue(n)


class Context:
    """Provides access to the context in fluent expression.

    Example:
        >>> (Fluent(context={'foo': 'bar'})
        ...     .Do(Context(lambda ctx: print(ctx['foo'])))
        ... )()
        bar
    """

    def __init__(self, callback: Callable):
        self.callback = callback
        self.context = None

    def __call__(self, *args, **kwargs):
        return self.callback(self.context, *args, **kwargs)

    def attach(self, context):
        self.context = context


class Fluent:
    """Class providing fluent interface.

    Allows to dynamically chain methods of target object (or just to turn
    statements into expressions) and to control flow with conditionals/loops/etc.

    Almost all fluent instructions can be evaluated lazily (when the expression
    is executed) by providing callbacks as arguments.

    Example:
        >>> # Example turning if statements into the expression.
        >>> (Fluent(target=None)
        ...     .If(False)
        ...         .Do(lambda: print('never printed'))
        ...     .Elif(lambda: True)
        ...         .Do(lambda: print('hello'))
        ...     .End()
        ... )() is None # <-- If target is unset, fluent expression returns None.
        hello
        True

        >>> (Fluent(target=None)
        ...     .If(lambda: True)
        ...         .Return(lambda: 'foo')  # Can be just .Return('foo').
        ...     .End()
        ... )() # <-- if .Return() is used, it's value is returned.
        'foo'

        >>> # Mode 'call' keeps the target object unchanged.
        >>> (Fluent(target=[], mode='call')
        ...     .If(lambda: True)
        ...         .extend([1, 2])  # Calls target.extend([1, 2]).
        ...     .End()
        ...     .reverse()  # Calls target.reverse() that reverses the list inplace.
        ... )()
        [2, 1]

        >>> # Mode 'apply' causes that result of calling target's methods
        >>> # will replace the target. If mode 'call' was used, the target
        >>> # would stay unchanged and the result of the fluent expression
        >>> # would be 'hello'.
        >>> (Fluent(target='hello', mode='apply')
        ...     .If(lambda: True)
        ...         .upper()  # Does target = target.upper() when mode='apply'.
        ...         .replace('LO', 'P')
        ...     .End()
        ... )()
        'HELP'
    """

    def __init__(self,
                 target=None,
                 mode: TMode = 'apply',
                 context: dict = None):
        """Initializes fluent expression.

        Args:
            target:
                If specified, target will be returned when the Fluent is executed.
            mode:
                Sets default mode when calling target's methods.
                Mode 'apply' will replace target with the result of method calls.
                Mode 'call' will just execute the target's methods.
            context:
                If specified, the context will be used.
        """
        self.__fluent_parent__ = None
        self.__fluent_children__ = []
        self.__fluent_target__ = ifset(target, Var)
        self.__fluent_mode__ = mode
        self.__fluent_context__ = context

    def __call__(self):
        """Evaluates the fluent expression.

        Returns:
            If target was set, returns target.
            If target is not set, returns None, unless Return() was used.
        """
        root = self
        while root.__fluent_parent__:
            root = root.__fluent_parent__

        try:
            root.__fluent_exec__()
        except _ReturnValue as e:
            return e.val
        except (_Continue, _Break) as e:
            raise RuntimeError(f'{e.__class__.__name__[1:]}() - '
                               f'given n is greater than the number '
                               f'of available loops')
        return getresult(self.__fluent_target__)

    def __fluent_add_child__(self, child):
        """Adds child fluent expression to the list of children."""
        self.__fluent_children__.append(child)
        child.__fluent_on_added__(self)
        return child

    def __fluent_on_added__(self, parent):
        """Called when the fluent expression is added to the parent."""
        self.__fluent_parent__ = parent
        self.__fluent_target__ = parent.__fluent_target__
        if self.__fluent_mode__ is None:
            self.__fluent_mode__ = parent.__fluent_mode__
        if self.__fluent_context__ is None:
            self.__fluent_context__ = parent.__fluent_context__

    def __fluent_exec__(self):
        """Executes current expression and its children."""
        for child in self.__fluent_children__:
            child.__fluent_exec__()

    def Do(self, action: Callable) -> Self:
        """Performs arbitrary action.

        The eventual result is not returned.

        Args:
            action: Action to perform.
        """
        self.__fluent_add_child__(_Do(action))
        return self

    def Return(self, value: TCallableOrAny) -> Self:
        """Returns the value and stops further execution.

        Args:
            value: If value is callable, it will be called
                   and the result is returned.
        """
        self.__fluent_add_child__(_Return(value))
        return self

    def Call(self, func: TCallableOrMethodName, *args, **kwargs) -> Self:
        """Executes func on target.

        If func is a string, it will be treated as a method name:
            target.func(*args, **kwargs)

        If func is callable, it will be executed directly
        with target as the first argument:
            func(target, *args, **kwargs)

        Args:
            func:
                Function or method name.
            *args:
                Positional arguments passed to func.
            **kwargs:
                Keyword arguments passed to func.
        """
        self.__fluent_add_child__(_Call(func, args, kwargs))
        return self

    def Apply(self, func: TCallableOrMethodName, *args, **kwargs) -> Self:
        """Executes func on target and replaces target with the result.

        If func is a string, it will be treated as a method name:
            target = target.func(*args, **kwargs)

        If func is callable, it will be executed directly
        with target as the first argument:
            target = func(target, *args, **kwargs)

        """
        self.__fluent_add_child__(_Apply(func, args, kwargs))
        return self

    def Block(self, mode: TMode = None) -> '_Block':
        """Creates a block of instructions.

        Args:
            mode: Sets mode ('apply'|'call') for this block when
                  calling target's methods. If None, mode is inherited.
        """
        return self.__fluent_add_child__(_Block(mode=mode))

    def If(self, predicate: TCallableOrAny) -> '_If':
        """Creates a block of instructions that will be executed
        if predicate is truthful.

        Args:
            predicate: Predicate to test.
        """
        return self.__fluent_add_child__(_If(predicate))

    def Try(self) -> '_Try':
        """Create a block of instructions where any exceptions thrown
        will be eventually handled in the following Except blocks.
        """
        return self.__fluent_add_child__(_Try())

    def While(self, predicate) -> '_While':
        """Creates a block of instructions that will be executed repeatedly
        while predicate is truthful.

        Loop can be broken by calling Break().

        Args:
            predicate: Predicate to test.
        """
        return self.__fluent_add_child__(_While(predicate))

    def DoWhile(self, predicate) -> '_DoWhile':
        """Creates a block of instructions that will be executed repeatedly
        while predicate is truthful. The block will be executed at least once.

        Loop can be broken by calling Break().

        Args:
            predicate: Predicate to test.
        """
        return self.__fluent_add_child__(_DoWhile(predicate))

    def Repeat(self, n) -> '_Repeat':
        """Creates a block of instructions that will be executed n times.

        Loop can be broken by calling Break().

        Args:
            n: Number of times to execute the block.
        """
        return self.__fluent_add_child__(_Repeat(n))

    def __getattr__(self, func):
        """Shortcut for .Apply/Call(func, *args, **kwargs).

        Which method is used depends on the mode in parent block.

        Args:
            func(str): Targets method name.

        Raises:
            AttributeError: If target is not set.

        Example:
            >>> (Fluent(target='hello', mode='apply')
            ...     .upper()  # <- does target = target.upper()
            ... )()
            'HELLO'
        """
        if self.__fluent_target__ is None:
            raise RuntimeError(f'target must be set first: {func}')
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
    def __init__(self, func: TCallableOrMethodName, args, kwargs):
        super().__init__()
        self.__fluent_args__ = func, args, kwargs

    def __fluent_exec__(self):
        target = self.__fluent_target__.value
        func, args, kwargs = self.__fluent_args__

        if isinstance(func, Context):
            func.attach(self.__fluent_context__)
            callback = func.callback
            if isinstance(callback, str):
                func.callback = getattr(target, callback)(*args, **kwargs)
            else:
                func.callback = callback(target, *args, **kwargs)
            return func(target, *args, **kwargs)

        else:
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
        callback = self.__fluent_callback__
        if isinstance(callback, Context):
            callback.attach(self.__fluent_context__)
        return callback()


class _Return(Fluent):
    def __init__(self, value: TCallableOrAny):
        super().__init__()
        self.__fluent_value__ = value

    def __fluent_exec__(self):
        value = self.__fluent_value__
        if isinstance(value, Context):
            value.attach(self.__fluent_context__)
        raise _ReturnValue(getresult(value))


class _Predicate(Fluent):
    def __init__(self, predicate: TCallableOrAny):
        super().__init__()
        self.__fluent_predicate__ = predicate


class _Block(Fluent):
    def __init__(self, mode: TMode = None):
        super().__init__(None, mode)

    def End(self) -> 'Fluent':
        """Ends the block."""
        return self.__fluent_parent__


class _If(_Predicate, _Block):
    def __init__(self, predicate: TCallableOrAny):
        super().__init__(predicate)
        self.__fluent_branches__ = [(predicate, self.__fluent_children__)]
        self.__fluent_last_clause__ = 'If'

    def __fluent_exec__(self):
        for args, children in self.__fluent_branches__:
            if isinstance(args, Context):
                args.attach(self.__fluent_context__)
            if getresult(args):
                self.__fluent_children__ = children
                super().__fluent_exec__()
                break

    def Elif(self, predicate: TCallableOrAny):
        """Creates a block of instructions that will be executed
        when predicate is truthful and prior If/Elif blocks failed.

        Args:
            predicate: Predicate to test.
        """
        if self.__fluent_last_clause__ == 'Else':
            raise RuntimeError('Cannot use Elif() after Else().')

        self.__fluent_children__ = []
        self.__fluent_branches__.append((predicate, self.__fluent_children__))
        self.__fluent_last_clause__ = 'Elif'
        return self

    def Else(self):
        """Creates a block of instructions that will be executed
        when all prior If/Elif blocks failed.
        """
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

    def Except(self, *exceptions: BaseException):
        """Creates a block of instructions that will be executed if any
        of given exceptions is thrown by prior Try block.

        Args:
            *exceptions: Exceptions to catch.
        """
        if self.__fluent_last_clause__ in ('Else', 'Finally'):
            raise RuntimeError(f'Except() can\'t be used '
                               f'after {self.__fluent_last_clause__}().')

        self.__fluent_children__ = []
        self.__fluent_excepts__.append((exceptions, self.__fluent_children__))
        self.__fluent_last_clause__ = 'Except'
        return self

    def Else(self):
        """Creates a block of instructions that will be executed
        if prior Try block throws no exceptions.
        """
        if self.__fluent_last_clause__ == 'Else':
            raise RuntimeError('Else() can be used once per Try() block only.')
        elif self.__fluent_last_clause__ == 'Finally':
            raise RuntimeError('Else() can\'t be used after Finally().')
        self.__fluent_children__ = self.__fluent_else__
        self.__fluent_last_clause__ = 'Else'
        return self

    def Finally(self):
        """Creates a block of instructions that will always be executed
        if prior Try block was executed.
        """
        if self.__fluent_last_clause__ == 'Finally':
            raise RuntimeError('Finally() can be used '
                               'once per Try() block only.')
        self.__fluent_children__ = self.__fluent_finally__
        self.__fluent_last_clause__ = 'Finally'
        return self


class _While(_Predicate, _Block):
    def __fluent_exec__(self):
        predicate = self.__fluent_predicate__
        if isinstance(predicate, Context):
            predicate.attach(self.__fluent_context__)

        try:
            while getresult(predicate):
                try:
                    super().__fluent_exec__()
                except _Continue as e:
                    if n := e.n - 1:
                        raise _Continue(n)
        except _Break as e:
            if n := e.n - 1:
                raise _Break(n)


class _DoWhile(_Predicate, _Block):
    def __fluent_exec__(self):
        predicate = self.__fluent_predicate__
        if isinstance(predicate, Context):
            predicate.attach(self.__fluent_context__)
        try:
            while True:
                try:
                    super().__fluent_exec__()
                    if not getresult(predicate):
                        break
                except _Continue as e:
                    if n := e.n - 1:
                        raise _Continue(n)
        except _Break as e:
            if n := e.n - 1:
                raise _Break(n)


class _Repeat(_Block):
    def __init__(self, n: int):
        super().__init__()
        self.__fluent_n__ = n

    def __fluent_exec__(self):
        context = self.__fluent_context__
        if context is not None:
            perform(setfz(context, '__repeat__', list), 'append', Var(0))

        n = self.__fluent_n__
        if isinstance(n, Context):
            n.attach(context)
        try:
            result = getresult(n)
            for i in range(result):
                try:
                    super().__fluent_exec__()
                except _Continue as e:
                    if n := e.n - 1:
                        raise _Continue(n)
        except _Break as e:
            if n := e.n - 1:
                raise _Break(n)
