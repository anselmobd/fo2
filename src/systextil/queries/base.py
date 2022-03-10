from pprint import pprint

from fo2.connections import db_cursor_so

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute


class MountQuery():

    def __init__(
            self,
            fields=None,
            table=None,
            where=None,
            group=None,
            order=None,
            group_all_fields=False,
            order_all_fields=False,
        ) -> None:
        self.fields = fields
        self.table = table
        self.where = where
        self.group_arg = group if group else []
        self.order_arg = order if order else []
        self.group_all_fields = group_all_fields
        self.order_all_fields = order_all_fields

        self._group = None
        self._order = None

    @property
    def group(self):
        if not self._group:
            group_form_fields = (
                self.off_alias(self.fields)
                if self.group_all_fields
                else []
            )
            self._group = group_form_fields + self.group_arg
        return self._group

    @property
    def order(self):
        if not self._order:
            order_form_fields = (
                self.off_alias(self.fields)
                if self.order_all_fields
                else []
            )
            self._order = order_form_fields + self.order_arg
        return self._order

    @property
    def sql(self):
        qselect = f"""SELECT
            {", ".join(self.fields)}"""
        qfrom = f"""FROM {self.table}"""
        qwhere = f"""WHERE
            {" AND ".join(self.where)}""" if self.where else "--"
        qgroup = f"""GROUP BY
            {", ".join(self.group)}""" if self.group else "--"
        qorder = f"""ORDER BY
            {", ".join(self.order)}""" if self.order else "--"
        return f"""
            {qselect}
            {qfrom}
            {qwhere}
            {qgroup}
            {qorder}
        """

    @property
    def squery(self):
        return SQuery(self.sql)

    def off_alias(self, fields):
        new_fields = []
        for field in map(str.strip, fields):
            last_space = field.rfind(' ')
            if last_space + 1:  # se last_space >= 0
                alias_candidate = field[last_space+1:]
                if alias_candidate.find('.') == -1:
                    new_fields.append(field[:last_space].strip())
                    continue
            new_fields.append(field)
        return new_fields


class SQuery():

    def __init__(self, sql) -> None:
        self.cursor = db_cursor_so()
        if isinstance(sql, MountQuery):
            self.sql = sql.sql
        else:
            self.sql = sql

    def debug_execute(self):
        debug_cursor_execute(self.cursor, self.sql)
        return dictlist(self.cursor)
