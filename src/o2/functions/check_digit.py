import sys
from pprint import pprint


def strnum_mod1110_digits(strnum, ndigits=2):
    digits = ''
    for _ in range(ndigits):
        digit = strnum_mod1110_digit(strnum+digits)
        digits += digit
    return digits


def strnum_mod1110_digit(strnum):
    """Calcula dígito verificador de string de representação numérica.
    Recebe: String representando um valor inteiro, com ou sem zeros à 
            esquerda.
            Obs.: Zeros à esquerda são significativos
    Retorna: String representando um dígito verificador
    """
    sum = 0
    for idx, strdigit in enumerate(strnum[::-1]):
        # Multiplicadores:
        #   Da direita para a esquerda, 9 a 2, ciclicamente
        #   Exemplo para tamanho 10: 8, 9, 2, 3, 4, 5, 6, 7, 8, 9
        mult = (-idx-1)%8+2
        # Antes de multiplicar os dígitos são somados de 1
        digit_add1 = int(strdigit) + 1
        calc = mult * digit_add1
        # Acumula-se o módulo 11 da multiplicação
        calc_mod11 = calc % 11
        sum += calc_mod11
    # Dígito verificador é o módulo 10 do acumulado
    sum_mod10 = sum % 10
    return str(sum_mod10)



if __name__ == '__main__':
    arg1 = int(sys.argv[1])

    for num in range(arg1):
        print(f"{num};{strnum_mod1110_digits(str(num))}")
       