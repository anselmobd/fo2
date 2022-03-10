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
        self.group = group
        self.order = order
        self.group_all_fields = group_all_fields
        self.order_all_fields = order_all_fields

    def sql(self):
        if self.group_all_fields:
            self.group = self.off_alias(self.fields)
        if self.order_all_fields:
            self.order = self.off_alias(self.fields)
        return self.query(
            self.fields,
            self.table,
            self.where,
            self.group,
            self.order,
        )

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

    def query(
            self,
            fields,
            table,
            where,
            group,
            order,
        ):
        qselect = f"""SELECT
            {", ".join(fields)}"""
        qfrom = f"""FROM {table}"""
        qwhere = f"""WHERE
            {" AND ".join(where)}""" if where else "--"
        qgroup = f"""GROUP BY
            {", ".join(group)}""" if group else "--"
        qorder = f"""ORDER BY
            {", ".join(order)}""" if order else "--"
        return f"""
            {qselect}
            {qfrom}
            {qwhere}
            {qgroup}
            {qorder}
        """


class SQuery():

    def __init__(self, sql) -> None:
        self.cursor = db_cursor_so()
        if isinstance(sql, MountQuery):
            self.sql = sql.sql()
        else:
            self.sql = sql

    def debug_execute(self):
        debug_cursor_execute(self.cursor, self.sql)
        return dictlist(self.cursor)
