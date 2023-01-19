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


def is_empty(value):
    """Retorna True de value for None ou:
    - se str: string vazia ou em branco
    - se number: 0
    """
    try:
        value = value.strip()
    except AttributeError:
        pass
    return not value


def fld_a_blank(row, field, viewname, *args):
    row[f'{field}|TARGET'] = '_blank'
    row[f'{field}|A'] = reverse(
        viewname,
        args=args,
    )


def fld_slf_a_blank(row, field, viewname, empty='-'):
    if not fld_empty(row, field, empty=empty):
        fld_a_blank(row, field, viewname, row[field])


def fld_date(row, field, empty='-'):
    if not fld_empty(row, field, empty=empty):
        row[field] = row[field].date()


def fld_empty(row, field, empty='-'):
    test = is_empty(row[field])
    if test and empty:
        row[field] = empty
    return test


def fld_str(row, field, empty='-'):
    if not fld_empty(row, field, empty=empty):
        row[field] = str(row[field])
