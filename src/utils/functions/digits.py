from functools import lru_cache
from stdnum.iso7064 import mod_11_10


@lru_cache(maxsize=128)
def fo2_digit_calc(inteiro):
    if isinstance(inteiro, str):
        try:
            inteiro = int(inteiro)
        except Exception:
            inteiro = 0
    if inteiro < 0:
        inteiro = 0
    salt1 = str(3*inteiro)
    digit1 = mod_11_10.calc_check_digit(salt1)
    salt2 = str(5*(inteiro*10+int(digit1)))
    digit2 = mod_11_10.calc_check_digit(salt2)
    return f"{digit1}{digit2}"


@lru_cache(maxsize=128)
def fo2_digit_with(inteiro):
    if isinstance(inteiro, int):
        inteiro = str(inteiro)
    return f'{inteiro}{fo2_digit_calc(inteiro)}'


@lru_cache(maxsize=128)
def fo2_digit_valid(texto):
    return fo2_digit_calc(texto[:-2]) == texto[-2:]
