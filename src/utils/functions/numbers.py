from pprint import pprint


def num_digits(number):
    return max(
        0,
        str(number)[::-1].find('.')
    )
