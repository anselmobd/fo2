from socket import if_indextoname, if_nameindex
import sys


def tpl_int_math_hash(num):
    alt_num = 702+num*702702
    raiz2 = (alt_num)**(1/2)
    raiz3 = (alt_num)**(1/3)
    raiz2_str = f"{raiz2:.4f}"
    raiz3_str = f"{raiz3:.4f}"
    hash99_str = ''.join([
        raiz2_str[-1],
        raiz3_str[-1]
    ])
    hash99 = int(hash99_str)
    print(f"{num};{hash99}")


def tpl_int_hash(num):
    alt_num = num + 765432
    str_num = str(alt_num)
    digits = strint_mod11_10_digits(str_num, ndigits=2)
    int_digits = int(digits)
    return int_digits


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
    # tpl_int_hash(arg1)

    for num in range(arg1):
        print(f"{num};{tpl_int_hash(num)}")
       
