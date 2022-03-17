from pprint import pprint


def strnum_mod1110_digits(strnum, ndigits=1):
    digits = ''
    for _ in range(ndigits):
        digit = strnum_mod1110_digit(strnum+digits)
        digits += digit
    return digits


def strnum_mod1110_digit(strnum):
    sum = 0
    for idx, strdigit in enumerate(strnum[::-1]):
        mult = idx%8+2
        digit = int(strdigit)
        calc = mult * digit 
        calc_mod11 = calc % 11
        sum += calc_mod11
    sum_mod10 = sum % 10
    return str(sum_mod10)
