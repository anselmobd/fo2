__all__ = ['ExecSql']

from pprint import pprint

from utils.functions.models.dictlist import (
    dictlist,
    dictlist_lower,
)


class ExecSql(object):
    """
    Initialize with cursor, args=[] (or *arguments) and parameters:
    - receive data when run DataSql.execute n times, passing only the sql
    Or pass sql also in inicialization:
    - receive imediatly data
    Parameters can be:
    - result_case:
      - '' or upper: process cursor with rows_to_dict_list
      - lower: process cursor with rows_to_dict_list_lower
      - cursor; not process the cursor
    """
    def __init__(self, cursor, *arguments, args=None, sql='', **kwargs):
        self._cursor = cursor
        if len(arguments) == 0:
            self.args = []
        else:
            self.args = arguments
        if args is not None:
            self.args.append(args)
        self.result_case = 'upper'
        if 'result_case' in {k.lower() for k in kwargs}:
            self.result_case = {
                k.lower(): v for k, v in kwargs.items()}['result_case']
        if sql:
            self.sql = sql

    def execute(self, sql=''):
        if sql:
            self.sql = sql
        self._cursor.execute(self.sql, self.args)
        if self.result_case == 'lower':
            return dictlist_lower(self._cursor)
        elif self.result_case == 'cursor':
            return self._cursor
        else:
            return dictlist(self._cursor)

    @property
    def sql(self): pass

    @sql.setter
    def sql(self, sql):
        self.data = self.execute(sql)
