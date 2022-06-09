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


def only_alnum(text):
    return ''.join(filter(str.isalnum, text))


def noneif(value, test):
    """Return None if equal, else return value"""
    if value != test:
        return value


def noneifempty(value):
    return noneif(value, '')


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


def min_max_string(min, max, process_input=noneifempty, msg_format="{}"):
    if process_input:
        min_max = min, max
        if not isinstance(process_input, tuple):
            process_input = (process_input, )
        for process in process_input:
            min_max = map(process, min_max)
        min, max = min_max
    if min or max:
        if min == max:
            filtro = f"igual a {min}"
        elif min and max:
            filtro = f"entre {min} e {max}"
        elif min:
            filtro = f"no mínimo {min}"
        elif max:
            filtro = f"no máximo {max}"
        return msg_format.format(filtro)
