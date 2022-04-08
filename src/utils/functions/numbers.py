from functools import lru_cache
from pprint import pprint


@lru_cache(maxsize=128)
def num_digits(number):
    return max(
        0,
        str(number)[::-1].find('.')
    )


def digits_to_str(digs, b='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    return ''.join([b[i] for i in digs])


def str_to_digits(str, b='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
    return [b.index(char) for char in str]


def number_to_base(n, b):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return digits[::-1]


def base_to_number(digits, b):
    n = 0
    for i in digits:
        n = n*b + i
    return n
