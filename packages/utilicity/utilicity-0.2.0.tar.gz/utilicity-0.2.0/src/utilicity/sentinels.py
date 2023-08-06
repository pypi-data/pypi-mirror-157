class __SentinelType(type):

    def __str__(self) -> str:
        return f'<Sentinel::{self.__name__}>'

    def __bool__(self):
        return False


class __Sentinel(metaclass=__SentinelType):

    def __new__(cls, *args, **kwargs):
        raise RuntimeError(f'{cls} - Sentinels are not instantiable.')

    @classmethod
    def same(cls, other) -> bool:
        """Returns True if other is of the same type as this sentinel.

        Example:
            >>> Default.same(Default)
            True
        """
        return cls is other

    @classmethod
    def notsame(cls, other) -> bool:
        """Returns True if other is not of the same type as this sentinel.

        Example:
            >>> from utilicity.helpers import coalesce
            >>> coalesce(Unset, Unset, 1, cond=Unset.notsame)
            1
        """
        return cls is not other


# Used by Utilicity itself.

class _Default(__Sentinel):
    """ Sentinel """


class _None(__Sentinel):
    """ Sentinel """


class _Sentinel(__Sentinel):
    """ Sentinel """


class _Stop(__Sentinel):
    """ Sentinel """


class _Unset(__Sentinel):
    """ Sentinel """


# For public use.

class Default(__Sentinel):
    """ Sentinel """


class Done(__Sentinel):
    """ Sentinel """


class Start(__Sentinel):
    """ Sentinel """


class End(__Sentinel):
    """ Sentinel """


class First(__Sentinel):
    """ Sentinel """


class Last(__Sentinel):
    """ Sentinel """


class Marker(__Sentinel):
    """ Sentinel """


class Missing(__Sentinel):
    """ Sentinel """


class Sentinel(__Sentinel):
    """ Sentinel """


class Stop(__Sentinel):
    """ Sentinel """


class Undefined(__Sentinel):
    """ Sentinel """


class Unset(__Sentinel):
    """ Sentinel """


class Unspecified(__Sentinel):
    """ Sentinel """
