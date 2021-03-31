from pprint import pprint


def all_str(something):
    """
    Convert to string all values from a list or tuple; or
    Convert to string a value (not list or tuple)
    """
    if isinstance(something, (list, tuple)):
        return type(something)(map(str, something))
    else:
        return str(something)


def join(sep, lista):
    sep = all_str(sep)
    lista = all_str(lista)
    if len(lista) == 1:
        return lista[0]
    if isinstance(sep, (list, tuple)) and len(sep) == 2:
        first = sep[0].join(lista[:-1])
        return sep[1].join([first, lista[-1]])
    else:
        return sep.join(lista)


def join_non_empty(sep, lista):
    return join(sep, [s for s in lista if s.strip()])


def only_digits(text):
    num_text = []
    for char in text:
        if char.isdigit():
            num_text.append(char)
    return ''.join(num_text)


def split_nonempty(text, sep):
    return [
        t.strip()
        for t in text.split(sep)
        if t.strip()
    ]
