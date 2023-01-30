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


def fld_a_blank(row, field, viewname, *args, **kwargs):
    fld_reverse(row, field, viewname, *args, **kwargs, a_link='A', target='_blank')


def fld_a(row, field, viewname, *args, **kwargs):
    fld_reverse(row, field, viewname, *args, **kwargs, a_link='A')


def fld_link_blank(row, field, viewname, *args, **kwargs):
    fld_reverse(row, field, viewname, *args, **kwargs, a_link='LINK', target='_blank')


def fld_link(row, field, viewname, *args, **kwargs):
    fld_reverse(row, field, viewname, *args, **kwargs, a_link='LINK')


def insert_fld_reverse(
    row, field, viewname, *args, a_link=None, target=None
):
    if target:
        row[f'{field}|TARGET'] = target
    if a_link:
        a_link = a_link.upper()
        if not args:
            args = [row[field]]
        row[f'{field}|{a_link}'] = reverse(
            viewname,
            args=args,
        )


def fld_reverse(row, field, viewname, *args,
    a_link=None, target=None,
    always_link=False, default=None,
    is_empty_also=None, is_empty_only=None,
):
    field_is_empty = is_empty(
        row[field], also=is_empty_also, only=is_empty_only)
    if always_link or not field_is_empty:
        insert_fld_reverse(
            row, field, viewname, *args, a_link=a_link, target=target)
    if field_is_empty and default:
        row[field] = default


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
