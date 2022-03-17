from string import digits
import sys


TPL_HASH_ALPHA = "ABCDEFGHIJKLMNPQRSTUVWXYZ"


def tpl_hash_verify(strint):
    return strint == tpl_hashed(tpl_unhashed(strint))


def tpl_hashed(strint):
    return strint + tpl_hash_code(strint)


def tpl_unhashed(strint):
    return strint[:-1]


def tpl_hash_code(strint):
    int_num = int(strint)
    alt_num = int_num + 765432
    str_num = str(alt_num)
    digits = strint_mod11_10_digits(str_num, ndigits=2)
    int_digits = int(digits)
    return TPL_HASH_ALPHA[int_digits%len(TPL_HASH_ALPHA)]


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
        print(f"{num};{tpl_hash_code(str(num))}")
       
