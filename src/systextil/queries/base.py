from pprint import pprint

from fo2.connections import db_cursor_so

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute


class SQuery():

    def __init__(
            self,
            sql=None,
            fields=None,
            table=None,
            where=None,
            group=None,
            order=None,
            group_all_fields=False,
            order_all_fields=False,
        ) -> None:
        self.cursor = db_cursor_so()
        if sql:
            self.sql = sql
        else:
            if group_all_fields:
                group = self.off_alias(fields)
            if order_all_fields:
                order = self.off_alias(fields)
            self.sql = self.query(
                fields,
                table,
                where,
                group,
                order,
            )

    def off_alias(self, fields):
        new_fields = []
        for field in map(str.strip, fields):
            last_space = field.rfind(' ')
            if last_space + 1:  # se last_space >= 0
                alias_candidate = field[last_space+1:]
                print(alias_candidate)
                if alias_candidate.find('.') == -1:
                    new_fields.append(field[:last_space])
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
            {"AND ".join(where)}""" if where else "--"
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

    def debug_execute(self):
        debug_cursor_execute(self.cursor, self.sql)
        return dictlist(self.cursor)
