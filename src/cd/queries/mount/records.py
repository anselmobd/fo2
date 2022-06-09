from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute

from cd.queries.mount import query
from cd.queries.mount import select


class Records():

    def __init__(
        self,
        cursor,
        fields=None,
        filter=None,
        table=None,
    ):
        self.cursor = cursor
        self.fields = fields
        self.filter = filter
        self.table = table

        self.query = query.Query()
        self.select = select.Select()

    def sql(self):
        self.query.add_alias(self.table)

        if self.fields:
            for field in self.fields:
                self.query.add_select_field(field)

        if self.filter:
            for key in self.filter:
                if self.filter[key] is not None:
                    self.query.add_filter(
                        key,
                        self.filter[key]
                    )

        return self.query.sql()

    def data(self):
        sql = self.sql()

        debug_cursor_execute(self.cursor, sql)
        data = dictlist(self.cursor)

        self.query.apply_makes(data)

        return data
