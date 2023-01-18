from pprint import pprint

from django.urls import reverse


__all__ = [
    'row_field_a_blank',
    'row_field_date',
    'row_field_empty',
    'row_field_str',
]


def row_field_a_blank(row, field, viewname, *args):
    row[f'{field}|TARGET'] = '_blank'
    row[f'{field}|A'] = reverse(
        viewname,
        args=args,
    )


def row_field_date(row, field, empty='-'):
    row[field] = row[field].date() if row[field] else empty


def row_field_empty(row, field, empty='-'):
    if (not row[field]) or (isinstance(row[field], str) and not row[field].strip()):
        row[field] = empty


def row_field_str(row, field, empty='-'):
    row[field] = str(row[field]) if row[field] else empty
