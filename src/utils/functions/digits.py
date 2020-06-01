from stdnum.iso7064 import mod_11_10


def fo2_digit_calc(inteiro):
    if isinstance(inteiro, str):
        inteiro = int(inteiro)
    salt1 = str(3*inteiro)
    digit1 = mod_11_10.calc_check_digit(salt1)
    salt2 = str(5*(inteiro*10+int(digit1)))
    digit2 = mod_11_10.calc_check_digit(salt2)
    return f"{digit1}{digit2}"


def fo2_digit_with(inteiro):
    if isinstance(inteiro, int):
        texto = str(inteiro)
    return f'{texto}{fo2_digit_calc(inteiro)}'
