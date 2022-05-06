import textwrap
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


def __join(sep, lista):
    lista = all_str(lista)
    if len(lista) == 1:
        return lista[0]
    sep = all_str(sep)
    if isinstance(sep, (list, tuple)) and len(sep) == 2:
        first = sep[0].join(lista[:-1])
        return sep[1].join([first, lista[-1]])
    else:
        return sep.join(lista)


def join2(sep, lista):
    try:
        return(__join(sep, lista))
    except Exception:
        return ''


def join_non_empty(sep, lista):
    return join2(sep, [s for s in lista if str(s).strip()])


def is_only_digits(text):
    return all(map(str.isdigit, text))


def only_digits(text):
    return ''.join(filter(str.isdigit, text))


def split_non_empty(text, sep):
    return [
        t.strip()
        for t in text.split(sep)
        if t.strip()
    ]

def lm(string):
    """Left Margin
    Desidenta string de acordo com a identação da primeira linha.
    Exemplo de uso:
    sql = textwrap.dedent('''\
        select
          count(*)
        from tabela
    ''')
    print(sql)
    select
      count(*)
    from tabela
    """
    return textwrap.dedent(string)
