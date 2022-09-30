from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from cd.queries.mount import query
from cd.queries.mount import select


class Records():

    def __init__(
        self,
        cursor,
        fields=None,
        filters=None,
        table=None,
    ):
        self.cursor = cursor
        self.fields = fields
        self.filters = filters
        self.table = table

        self.query = query.Query()
        self.select = select.Select()

    def sql(self):
        if self.table:
            self.query.add_alias(self.table)

        self.select.add_from('lp')
        self.select.add_field('field alias')
        if self.fields:
            for field in self.fields:
                self.query.add_select_field(field)
                self.select.add_field(field)

        if self.filters:
            for key in self.filters:
                if self.filters[key] is not None:
                    self.query.add_filter(
                        key,
                        self.filters[key]
                    )

        return self.query.sql()

    def data(self):
        sql = self.sql()

        debug_cursor_execute(self.cursor, sql)
        data = dictlist_lower(self.cursor)

        self.query.apply_makes(data)

        return data
