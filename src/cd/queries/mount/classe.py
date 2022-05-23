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

        self.statement = Statement(
            select=select,
            filter=filter,
            table=table,
        )

    def data(self):
        sql = self.statement.sql()

        debug_cursor_execute(self.cursor, sql)
        data = dictlist(self.cursor)

        return data


class Statement():
    """Monta Statement
    """

    def __init__(
        self, 
        select=None, 
        filter=None, 
        table=None, 
    ):
        self.select = select
        self.filter = filter
        self.table = table

        self.query = query.Query()

    def sql(self):
        self.query.table = self.table

        for key in self.filter:
            self.query.add_filter(
                key,
                self.filter[key]
            )

        for field in self.select:
            self.query.add_select_field(field)

        return self.query.sql()
