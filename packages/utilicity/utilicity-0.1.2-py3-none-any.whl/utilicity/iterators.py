from .vars import Null


class CachingIterator:
    """ TODO: doc """

    def __init__(self, iterable, lazy=True):
        self._iterable = iterable
        self._lazy = lazy
        self._pointer = -1
        self._cache = []
        self._iterator = None
        self._finished = None
        self.__iter__()

    def __next_cached(self):
        current = next(self._iterator)
        self._pointer += 1
        return current

    def __next_init(self):
        next_pointer = self._pointer + 1
        cache = self._cache
        if next_pointer < len(cache):
            current = cache[next_pointer]
        else:
            try:
                current = next(self._iterator)
            except StopIteration:
                self._finished = next_pointer - 1
                raise
            cache.append(current)
        self._pointer = next_pointer

        return current

    __next = __next_init

    def __next__(self):
        return self.__next()

    def __iter__(self):
        self._pointer = -1

        finished = self._finished is not None
        eager = not self._lazy
        if finished or eager:
            if eager and not finished:
                self._cache = list(self._iterable)
                self._finished = len(self._cache) - 1
            self._iterator = iter(self._cache)
            self.__next = self.__next_cached
        else:
            self._cache = []
            self._iterator = iter(self._iterable)
            self.__next = self.__next_init

        return self

    def __len__(self):
        return len(self._iterable) \
            if self._finished is None \
            else self._finished + 1

    @property
    def current(self):
        return self._cache[self._pointer]

    def behind(self, nth: int = 1, default=None):
        if nth < 0:
            raise ValueError('Arg nth must be non negative.')

        index = self._pointer - nth
        if index < 0:
            return default
        try:
            return self._cache[index]
        except IndexError:
            return default

    def ahead(self, nth: int = 1, default=None):
        if nth < 0:
            raise ValueError('Arg nth must be non negative.')

        ahead_index = self._pointer + nth
        cache = self._cache

        missing = 1 + ahead_index - len(cache)
        if missing > 0:
            if self._finished is not None:
                return default

            iterator = self._iterator
            try:
                for i in range(missing):
                    cache.append(next(iterator))
            except StopIteration:
                self._finished = len(cache) - 1
                return default

        try:
            return cache[ahead_index]
        except IndexError:
            return default

    @property
    def is_first(self):
        pointer = self._pointer
        if pointer == -1:
            return None
        return pointer == 0

    @property
    def is_last(self):
        if self._pointer == -1:
            return None
        return self.ahead(default=Null) is Null

    @property
    def is_odd(self):
        pointer = self._pointer
        if pointer == -1:
            return None
        return pointer % 2 == 0

    @property
    def is_even(self):
        pointer = self._pointer
        if pointer == -1:
            return None
        return pointer % 2 == 1

    @property
    def counter(self):
        if self._pointer == -1:
            return None
        return self._pointer + 1
