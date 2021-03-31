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
    if isinstance(sep, (list, tuple)) and len(sep) == 2:
        first = str(sep[0]).join(map(str, lista[:-1]))
        return str(sep[1]).join([first, str(lista[-1])])
    else:
        return sep.join(map(str, lista))


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
