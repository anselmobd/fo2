from pprint import pprint

from django.urls import reverse

from utils.functions.variable import is_empty


__all__ = ['PrepRows']


class PrepRows():

    def __init__(self, data, basic_steps=None) -> None:
        self.__data = data
        self.__basic_steps = [
            self.prep_args(step)
            for step in basic_steps
        ] if basic_steps else []

        self.__post_process = {
            'str': self._str,
        }


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

    def _args_with_fields_to_args(self, row, *args_with_fields):
        args = []
        has_field = False
        for arg in args_with_fields:
            if isinstance(arg, set):
                has_field = True
                args.append(row[arg.pop()])
            elif isinstance(arg, list):
                has_field = True
                for field in arg:
                    args.append(row[field])
            else:
                args.append(arg)
        if has_field:
            return args
        return args_with_fields

    def _insert_reverse(
        self, row, field, viewname, *args, a_link=None, target=None
    ):
        if target:
            row[f'{field}|TARGET'] = target
        if a_link:
            a_link = a_link.upper()
            if args:
                args = self._args_with_fields_to_args(row, *args)
            else:
                args = [row[field]]
            row[f'{field}|{a_link}'] = reverse(
                viewname,
                args=args,
            )

    def _reverse(
        self, row, field, viewname, *args,
        a_link=None, target=None,
        always_link=False, default=None,
        is_empty_also=None, is_empty_only=None,
        post_process=None,
    ):
        field_is_empty = is_empty(
            row[field], also=is_empty_also, only=is_empty_only)
        if always_link or not field_is_empty:
            self._insert_reverse(
                row, field, viewname, *args, a_link=a_link, target=target)
        if field_is_empty and default:
            row[field] = default
        else:
            if post_process:
                if isinstance(post_process, str):
                    self.__post_process[post_process](row, field)
                else:
                    post_process(row, field)

    def _a_blank(self, row, field, viewname, *args, **kwargs):
        self._reverse(
            row, field, viewname, *args, **kwargs,
            a_link='A', target='_blank')

    def _a(self, row, field, viewname, *args, **kwargs):
        self._reverse(
            row, field, viewname, *args, **kwargs,
            a_link='A')

    def _link_blank(self, row, field, viewname, *args, **kwargs):
        self._reverse(
            row, field, viewname, *args, **kwargs,
            a_link='LINK', target='_blank')

    def _link(self, row, field, viewname, *args, **kwargs):
        self._reverse(
            row, field, viewname, *args, **kwargs,
            a_link='LINK')

    def _default(self, row, field, default='-', field_is_empty=None):
        empty = is_empty(row[field]) if field_is_empty is None else field_is_empty
        if empty and default:
            row[field] = default
            return True

    def _to_date(self, row, field, field_is_empty=None):
        empty = is_empty(row[field]) if field_is_empty is None else field_is_empty
        if not empty:
            row[field] = row[field].date()

    def _date(self, row, field, default=None):
        empty = is_empty(row[field])
        if default is None:
            self._to_date(row, field, field_is_empty=empty)
        elif not self._default(row, field, default=default, field_is_empty=empty):
            self._to_date(row, field, field_is_empty=empty)

    def _date_dash(self, row, field):
        self._date(row, field, default='-')

    def _to_str(self, row, field, field_is_empty=None):
        empty = is_empty(row[field]) if field_is_empty is None else field_is_empty
        if not empty:
            row[field] = str(row[field])

    def _sn(self, row, field, nao_sim=['Não', 'Sim']):
        row[field] = nao_sim[bool(row[field])]

    def _str(self, row, field, default=None):
        empty = is_empty(row[field])
        if default is None:
            self._to_str(row, field, field_is_empty=empty)
        elif not self._default(row, field, default=default, field_is_empty=empty):
            self._to_str(row, field, field_is_empty=empty)

    def _str_dash(self, row, field):
        self._str(row, field, default='-')

    def custom_command(self, command, *args, **kwargs):
        self.__basic_steps.append(
            self.prep_args([command]+list(args)+[kwargs])
        )
        return self

    def a_blank(self, *args, **kwargs):
        self.custom_command(self._a_blank, *args, **kwargs)
        return self

    def date(self, *args, **kwargs):
        self.custom_command(self._date, *args, **kwargs)
        return self

    def date_dash(self, *args, **kwargs):
        self.custom_command(self._date_dash, *args, **kwargs)
        return self

    def default(self, *args, **kwargs):
        self.custom_command(self._default, *args, **kwargs)
        return self

    def str(self, *args, **kwargs):
        self.custom_command(self._str, *args, **kwargs)
        return self

    def sn(self, *args, **kwargs):
        self.custom_command(self._sn, *args, **kwargs)
        return self

    def process(self):
        for row in self.__data:
            for basic_step in self.__basic_steps:
                for field in basic_step['fields']:
                    basic_step['procedure'](
                        row,
                        field,
                        *basic_step['args'],
                        **basic_step['kwargs'],
                    )
