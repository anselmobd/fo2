from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute

from cd.queries.mount import query


class Records():

    def __init__(
        self,
        cursor,
        select=None,
        filter=None,
        table=None,
    ):
        self.cursor = cursor
        self.select = select
        self.filter = filter
        self.table = table

        self.query = query.Query()

    def sql(self):
        self.query.add_alias(self.table)

        if self.filter:
            for key in self.filter:
                if self.filter[key] is not None:
                    self.query.add_filter(
                        key,
                        self.filter[key]
                    )

        if self.select:
            for field in self.select:
                self.query.add_select_field(field)

        return self.query.sql()

    def data(self):
        sql = self.sql()

        debug_cursor_execute(self.cursor, sql)
        data = dictlist(self.cursor)

        self.query.apply_makes(data)

        return data
