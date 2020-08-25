from pprint import pprint


def calc_check_digit(number):
    """Calculate the EAN check digit for 13-digit numbers. The number passed
    should not have the check bit included.
    ---
    From:
      https://github.com/arthurdejong/python-stdnum/blob/master/stdnum/ean.py
    """
    return str((10 - sum((3, 1)[i % 2] * int(n)
                for i, n in enumerate(reversed(number)))) % 10)


def gtin13_valid(numbers):
    if len(numbers) != 13:
        return False
    return numbers[12] == calc_check_digit(numbers[:12])
