from decimal import InvalidContext
from string import digits
import sys
from xml.dom import InvalidCharacterErr


_TPL_HASH_ALPHA = "ABCDEFGHIJKLMNPQRSTUVWXYZ"
_LEN_TPL_HASH_ALPHA = 25


def plt_split(code):
    prefix_list = []
    for char in code:
        if char.isalpha():
            prefix_list.append(char)
        else:
            break
    prefix = ''.join(prefix_list)
    hash = code[-1] if code[-1].isalpha() else ''
    len_code = len(code)
    len_prefix = len(prefix)
    len_hash = len(hash)
    if len_code <= len_prefix + len_hash:
        raise ValueError("Valid formats: A*9* or A*9*A")
    number = code[len_prefix:len_code-len_hash]
    return prefix, number, hash


def plt_verify(strint):
    return strint == plt_hashed(strint)


def plt_hashed(code):
    return plt_unhashed(code) + plt_hash(code)


def plt_unhashed(code):
    prefix, strint, _ = plt_split(code)
    return ''.join([prefix, strint])


def plt_next(code):
    prefix, strint, _ = plt_split(code)
    next_int = int(strint) + 1 
    return plt_mount(next_int, prefix, len(strint))


def plt_mount(int_num, prefix="PLT", int_len=4):
    strint = str(int_num).zfill(int_len)
    return plt_hashed(''.join([prefix, strint]))


def plt_hash(code):
    _, strint, _ = plt_split(code)
    int_num = int(strint)
    alt_num = int_num + 765432
    str_num = str(alt_num)
    digits = strint_mod11_10_digits(str_num, ndigits=2)
    int_digits = int(digits)
    return _TPL_HASH_ALPHA[int_digits%_LEN_TPL_HASH_ALPHA]


def strint_mod11_10_digits(strint, ndigits=1):
    digits = ''
    for _ in range(ndigits):
        digit = strint_mod11_10_digit(strint+digits)
        digits += digit
    return digits


def strint_mod11_10_digit(strint):
    sum = 0
    for idx, digit in enumerate(strint[::-1]):
        mult = idx%8+2
        digit_int = int(digit)
        calc = mult * digit_int 
        calc_11 = calc % 11
        sum += calc_11
    sum_10 = sum % 10
    return str(sum_10)


if __name__ == '__main__':
    arg1 = int(sys.argv[1])

    for num in range(arg1):
        print(f"{num};{plt_hash(str(num))}")
       
