from pprint import pprint

from utils.functions.models.main import *


__all__ = ['DataSql']


class DataSql(object):
    """docstring for DataDim."""
    def __init__(self, cursor, args=[], sql='', case=None):
        self._cursor = cursor
        self.args = args
        self.case = case
        if sql:
            self.sql = sql

    def execute(self, sql):
        self._cursor.execute(sql, self.args)
        if self.case and self.case.startswith('l'):
            return rows_to_dict_list_lower(self._cursor)
        else:
            return rows_to_dict_list(self._cursor)

    @property
    def sql(self): pass

    @sql.setter
    def sql(self, sql):
        self.data = self.execute(sql)
