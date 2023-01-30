import numbers
from pprint import pprint

from django.urls import reverse


__all__ = [
    'fld_a_blank',
    'fld_a',
    'fld_link_blank',
    'fld_link',
    'fld_default',
    'fld_date',
    'fld_date_dash',
    'fld_str',
    'fld_str_dash',
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

    def in_sequence(value, enum):
        if isinstance(enum, str):
            enum = [enum]
        # catch TypeError, se não quiser erro quando also
        # não é tuple ou list ou outro enumerate
        for item in enum:
            if value == item:
                return True
        return False

    if only:
        return in_sequence(value, only)

    try:
        value = value.strip()
    except AttributeError:
        pass
    result = not value

    if not result and also:
        return in_sequence(value, also)

    return result


def fld_a_blank(row, field, viewname, *args, **kwargs):
    fld_reverse(
        row, field, viewname, *args, **kwargs,
        a_link='A', target='_blank')


def fld_a(row, field, viewname, *args, **kwargs):
    fld_reverse(
        row, field, viewname, *args, **kwargs,
        a_link='A')


def fld_link_blank(row, field, viewname, *args, **kwargs):
    fld_reverse(
        row, field, viewname, *args, **kwargs,
        a_link='LINK', target='_blank')


def fld_link(row, field, viewname, *args, **kwargs):
    fld_reverse(
        row, field, viewname, *args, **kwargs,
        a_link='LINK')


def fld_insert_reverse(
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
    post_process=None,
):
    field_is_empty = is_empty(
        row[field], also=is_empty_also, only=is_empty_only)
    if always_link or not field_is_empty:
        fld_insert_reverse(
            row, field, viewname, *args, a_link=a_link, target=target)
    if field_is_empty and default:
        row[field] = default
    elif post_process:
        post_process(row, field)


def fld_default(row, field, default=None):
    default = default if default else '-'
    test = is_empty(row[field])
    if test and default:
        row[field] = default
    return test


def fld_to_date(row, field):
    row[field] = row[field].date()


def fld_date(row, field, default=None):
    if default is None:
        fld_to_date(row, field)
    elif not fld_default(row, field, default=default):
        fld_to_date(row, field)


def fld_date_dash(row, field):
    fld_date(row, field, default='-')


def fld_to_str(row, field):
    row[field] = str(row[field])


def fld_str(row, field, default=None):
    if default is None:
        fld_to_str(row, field)
    elif not fld_default(row, field, default=default):
        fld_to_str(row, field)


def fld_str_dash(row, field):
    fld_str(row, field, default='-')


class PrepRows():

    def __init__(self, data, basic_steps) -> None:
        self.data = data
        self.basic_steps = [
            self.prep_args(step)
            for step in basic_steps
        ]

    def prep_args(self, step):
        params = {
            'procedure': step[0],
            'fields': (
                [step[1]]
                if isinstance(step[1], str)
                else step[1]
            ),
            'args': [],
            'kwargs': {},
        }
        for value in step[2:]:
            if isinstance(value, dict):
                params['kwargs'].update(value)
            else:
                params['args'].append(value)
        return params

    def process(self):
        for row in self.data:
            for basic_step in self.basic_steps:
                for field in basic_step['fields']:
                    basic_step['procedure'](
                        row,
                        field,
                        *basic_step['args'],
                        **basic_step['kwargs'],
                    )
