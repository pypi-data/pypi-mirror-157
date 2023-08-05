class fallbackdict(dict):
    """Like defaultdict but fallback() receives missing key as the argument."""

    def __init__(self, fallback: callable, *args, **kwargs):
        self.fallback = fallback
        super().__init__(*args, **kwargs)

    def __missing__(self, key):
        res = self[key] = self.fallback(key)
        return res


class recurdict(dict):
    """Dict where missing items can be accessed indefinitely.

    Example
    -------
    >>> recurdict()[1][2][3]  # no KeyError raised
    {}
    """

    def __missing__(self, key):
        res = self[key] = recurdict()
        return res
