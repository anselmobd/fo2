from itertools import takewhile
from pprint import pprint


__all__ = [
    'count_at_start',
    'count_at_end',
]


def count_at_start(str, test):
    if callable(test):
        func = test
    else:
        func = lambda value: value == test
    return sum(1 for _ in takewhile(func, str))


def count_at_end(str, test):
    return count_at_start(reversed(str), test)
