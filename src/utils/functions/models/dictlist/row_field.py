from pprint import pprint

from django.urls import reverse


__all__ = [
    'fld_a_blank',
    'fld_date',
    'fld_empty',
    'fld_self_a_blank',
    'fld_str',
]


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


def fld_empty(row, field, empty='-'):
    if (not row[field]) or (isinstance(row[field], str) and not row[field].strip()):
        row[field] = empty


def fld_str(row, field, empty='-'):
    row[field] = str(row[field]) if row[field] else empty
