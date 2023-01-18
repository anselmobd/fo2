from pprint import pprint

from django.urls import reverse


__all__ = [
    'fld_a_blank',
    'fld_date',
    'fld_empty_str',
    'fld_self_a_blank',
    'fld_str',
]


def _none_empty_blank(value):
    """Retorna True de value for None ou string vazia ou em branco"""
    return not value or not value.strip()


def _none_numeric0(value):
    """Retorna True de value for None ou numérico 0"""
    return not value or not value


def fld_a_blank(row, field, viewname, *args):
    row[f'{field}|TARGET'] = '_blank'
    row[f'{field}|A'] = reverse(
        viewname,
        args=args,
    )


def fld_self_a_blank(row, field, viewname):
    if row[field] is not None and str(row[field]):
        fld_a_blank(row, field, viewname, row[field])


def fld_date(row, field, empty='-'):
    row[field] = row[field].date() if row[field] else empty


def fld_empty_num(row, field, empty='-'):
    is_empty = _none_numeric0(row[field])
    if is_empty:
        row[field] = empty
    return is_empty


def fld_empty_str(row, field, empty='-'):
    is_empty = _none_empty_blank(row[field])
    if is_empty:
        row[field] = empty
    return is_empty


def fld_str(row, field, empty='-'):
    row[field] = str(row[field]) if row[field] is not None else empty
