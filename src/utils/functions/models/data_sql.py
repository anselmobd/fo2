__all__ = ['DataSql']

from pprint import pprint

from utils.functions.models.dictlist import dictlist, dictlist_lower
from utils.functions.queries import debug_cursor_execute


class DataSql(object):
    """docstring for DataDim."""
    def __init__(self, cursor, args=[], sql='', case=None):
        self._cursor = cursor
        self.args = args
        self.case = case
        if sql:
            self.sql = sql

    def execute(self, sql):
        debug_cursor_execute(self._cursor, sql, self.args)
        if self.case and self.case.startswith('l'):
            return dictlist_lower(self._cursor)
        else:
            return dictlist(self._cursor)

    @property
    def sql(self): pass

    @sql.setter
    def sql(self, sql):
        self.data = self.execute(sql)
