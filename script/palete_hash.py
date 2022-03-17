from decimal import InvalidContext
from string import digits
import sys
from xml.dom import InvalidCharacterErr


_PLT_HASH_ALPHA = "ABCDEFGHIJKLMNPQRSTUVWXYZ"
_PLT_LEN_HASH_ALPHA = len(_PLT_HASH_ALPHA)
_PLT_SALT = 765432
_PLT_PREFIX = "PLT"
_PLT_NUM_LEN = 4

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
    str_num = code[len_prefix:len_code-len_hash]
    return prefix, str_num, hash


def plt_verify(str_num):
    return str_num == plt_hashed(str_num)


def plt_hashed(code):
    return plt_unhashed(code) + plt_hash(code)


def plt_unhashed(code):
    prefix, str_num, _ = plt_split(code)
    return ''.join([prefix, str_num])


def plt_next(code):
    prefix, str_num, _ = plt_split(code)
    next_num = int(str_num) + 1 
    return plt_mount(next_num, prefix, len(str_num))


def plt_mount(num, prefix=_PLT_PREFIX, num_len=_PLT_NUM_LEN):
    str_num = str(num)
    len_str_num = len(str_num)
    if len_str_num > num_len:
        prefix = prefix[:num_len-len_str_num]
    str_num = str_num.zfill(num_len)
    return plt_hashed(''.join([prefix, str_num]))


def plt_hash(code):
    _, str_num, _ = plt_split(code)
    num = int(str_num)
    num_salt = num + _PLT_SALT
    str_num_salt = str(num_salt)
    hash_digits = str_num_mod1110_digits(str_num_salt, ndigits=2)
    hash_int = int(hash_digits)
    hash = _PLT_HASH_ALPHA[hash_int%_PLT_LEN_HASH_ALPHA]
    return hash


def str_num_mod1110_digits(str_num, ndigits=1):
    digits = ''
    for _ in range(ndigits):
        digit = str_num_mod1110_digit(str_num+digits)
        digits += digit
    return digits


def str_num_mod1110_digit(str_num):
    sum = 0
    for idx, str_digit in enumerate(str_num[::-1]):
        mult = idx%8+2
        digit = int(str_digit)
        calc = mult * digit 
        calc_mod11 = calc % 11
        sum += calc_mod11
    sum_mod10 = sum % 10
    return str(sum_mod10)


if __name__ == '__main__':
    arg1 = int(sys.argv[1])

    for num in range(arg1):
        print(f"{num};{plt_hash(str(num))}")
       
