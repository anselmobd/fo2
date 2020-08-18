from functools import lru_cache
from pprint import pprint


@lru_cache(maxsize=128)
def num_digits(number):
    return max(
        0,
        str(number)[::-1].find('.')
    )
