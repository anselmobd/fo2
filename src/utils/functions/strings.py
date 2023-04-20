import textwrap
from pprint import pprint

from utils.functions import coalesce


def pluralize(conta, plural=None, singular=None):
    plural = coalesce(plural, "s")
    singular = coalesce(singular, "")
    try:
        um = len(conta) == 1
    except TypeError:
        um = conta == 1
    return singular if um else plural


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
    return text and all(map(str.isdigit, text))


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


def split_strip(text, sep):
    return [
        t.strip()
        for t in text.split(sep)
    ]


def split_numbers(text):
    groups = []
    number = ""
    for c in f"{text} ":
        if c.isdigit():
            number = f"{number}{c}"
        else:
            if number:
                groups.append(number)
                number = ""
    return groups


def dirt_split_digits_alphas(text):
    parts = []
    draft = {
        'd': "",
        'a': "",
    }
    last_type = None
    for char in f"{text}#":
        char_type = 'd' if char.isdigit() else 'a' if char.isalpha() else None
        if char_type != last_type:
            if last_type:
                parts.append(draft[last_type])
                draft[last_type] = ""
            last_type = char_type
        if char_type:
            draft[char_type] += char
    return parts


def clean_split_digits_alphas(text):
    parts = []
    text = only_alnum(text)
    if text:
        draft = {
            'd': "",
            'a': "",
        }
        last_type = 'd' if text[0].isdigit() else 'a'
        for char in text:
            char_type = 'd' if char.isdigit() else 'a'
            if char_type != last_type:
                parts.append(draft[last_type])
                draft[last_type] = ""
                last_type = char_type
            draft[char_type] += char
        parts.append(draft[last_type])
    return parts


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


def lms(string):
    return lm(string).strip("\n")


def min_max_string(min, max, process_input=noneifempty, msg_format="{}", mm='min_max'):
    mm_string = {
        'min_max': {
            'entre': "entre {min} e {max}",
            'min': "no mínimo {min}",
            'max': "no máximo {max}",
        },
        'de_ate': {
            'entre': "de {min} até {max}",
            'min': "de {min}",
            'max': "até {max}",
        },
    }
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
            filtro = mm_string[mm]['entre'].format(min=min, max=max)
        elif min:
            filtro = mm_string[mm]['min'].format(min=min)
        elif max:
            filtro = mm_string[mm]['max'].format(max=max)
        return msg_format.format(filtro)
