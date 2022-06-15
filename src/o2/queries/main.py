from pprint import pprint

from django.db import connection

from utils.functions.models.dictlist import dictlist_lower
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
        self._OQuery = None

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
    def query(self):
        fields = "\n, ".join(self.fields)
        qselect = "\n  ".join(["SELECT", fields])

        qfrom = f"FROM {self.table}"

        where = "\n  AND ".join(self.where) if self.where else ""
        qwhere = " ".join(["WHERE", where]) if where else "-- where"

        group = "\n, ".join(self.group) if self.group else ""
        qgroup = "\n  ".join(["GROUP BY", group]) if group else "-- group"

        order = "\n, ".join(self.order) if self.order else ""
        qorder = "\n  ".join(["ORDER BY", order]) if order else "-- order"

        sql = "\n".join([
            qselect,
            qfrom,
            qwhere,
            qgroup,
            qorder,
        ])
        return sql

    @property
    def OQuery(self):
        if not self._OQuery:
            self._OQuery = OQuery
        return self._OQuery

    @property
    def oquery(self):
        return self.OQuery(self.query)

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


class OQuery():

    def __init__(self, sql) -> None:
        self._cursor = None
        if isinstance(sql, MountQuery):
            self.sql = sql.query
        else:
            self.sql = sql

    @property
    def cursor(self):
        if not self._cursor:
            self._cursor = connection.cursor()
        return self._cursor

    def debug_execute(self):
        debug_cursor_execute(self.cursor, self.sql)
        return dictlist_lower(self.cursor)
