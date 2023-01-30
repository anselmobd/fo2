import numbers
from pprint import pprint

from django.urls import reverse


__all__ = [
    'fld_a_blank',
    'fld_slf_a_blank',
    'fld_date',
    'fld_empty',
    'fld_str',
]


def is_empty(value, also=None, only=None):
    """
    Testa se valor é vazio

    Por padrão retorna True se:
    - value for None;
    - for string vazia ou em branco;
    - for number com valor 0.

    Parametros:
    - also: enumerate com outros valores a serem considerados
      como vazios, além do padrão citado acima.
    - only: enumerate os únicos valores a serem considerados
      como vazios, sobrepondo o padrão citado acima.
    """

    def in_enumerate(value, enum):
        if isinstance(enum, str):
            enum = [enum]
        # catch TypeError, se não quiser erro quando also
        # não é tuple ou list ou outro enumerate
        for item in enum:
            if value == item:
                return True
        return False

    if only:
        return in_enumerate(value, only)

    try:
        value = value.strip()
    except AttributeError:
        pass
    result = not value

    if not result and also:
        return in_enumerate(value, also)

    return result


def fld_a_blank(row, field, viewname, *args):
    row[f'{field}|TARGET'] = '_blank'
    row[f'{field}|A'] = reverse(
        viewname,
        args=args,
    )


def fld_slf_a_blank(row, field, viewname, default='-'):
    if not fld_empty(row, field, default=default):
        fld_a_blank(row, field, viewname, row[field])


def fld_slf_args_a_blank(row, field, viewname, *args, default='-'):
    if not fld_empty(row, field, default=default):
        fld_a_blank(row, field, viewname, *args)


def fld_date(row, field, default='-'):
    if not fld_empty(row, field, default=default):
        row[field] = row[field].date()


def fld_empty(row, field, default='-'):
    test = is_empty(row[field])
    if test and default:
        row[field] = default
    return test


def fld_str(row, field, default='-'):
    if not fld_empty(row, field, default=default):
        row[field] = str(row[field])
