from pprint import pprint

from fo2.connections import db_cursor_so

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute


class SQuery():

    def __init__(self, sql) -> None:
        self.cursor = db_cursor_so()
        self.sql = sql

    def debug_execute(self):
        debug_cursor_execute(self.cursor, self.sql)
        return dictlist(self.cursor)
