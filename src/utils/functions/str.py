from pprint import pprint


def join(sep, lista):
    str_lista = list(map(str, lista))
    if isinstance(sep, str):
        return sep.join(str_lista)
    else:
        if len(sep) == 2:
            result = sep[0].join(str_lista[:-1])
            result += sep[1] + str_lista[-1]
            return result
