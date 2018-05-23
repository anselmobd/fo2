import sys
import fdb
from pprint import pprint

from django.db import models

from fo2.settings import DB_F1


def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def rows_to_dict_list_lower(cursor):
    columns = [i[0].lower() for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def dict_list_to_lower(data):
    data_lower = []
    for row in data:
        row_lower = {}
        for key in row.keys():
            row_lower[key.lower()] = row[key]
        data_lower.append(row_lower)
    return data_lower


def cursorF1():
    con = fdb.connect(
        dsn='{}/{}:{}'.format(DB_F1['HOST'], DB_F1['PORT'], DB_F1['NAME']),
        user=DB_F1['USER'],
        password=DB_F1['PASSWORD'],
        charset=DB_F1['CHARSET']
        )
    return con.cursor()


def dict_def_options(dictionary, default, *args):
    """
    Return dictionary[arg] for first arg in args that exists in dictionary.
    Otherwise, return default value.
    """
    for arg in args:
        if arg in dictionary:
            return dictionary[arg]
    return default


def dict_options(dictionary, *args):
    """
    Call dict_def_options with default value None
    """
    return dict_def_options(dictionary, None, *args)


class DataSql(object):
    """docstring for DataDim."""
    def __init__(self, cursor, args=[], sql=''):
        self._cursor = cursor
        self.args = args
        if sql:
            self.sql = sql

    def execute(self, sql):
        self._cursor.execute(sql, self.args)
        return rows_to_dict_list(self._cursor)

    @property
    def sql(self): pass

    @sql.setter
    def sql(self, sql):
        self.data = self.execute(sql)


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
        self.args = []
        if len(arguments) != 0:
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
            return rows_to_dict_list_lower(self._cursor)
        elif self.result_case == 'cursor':
            return self._cursor
        else:
            return rows_to_dict_list(self._cursor)

    @property
    def sql(self): pass

    @sql.setter
    def sql(self, sql):
        self.data = self.execute(sql)


class GradeQtd(object):
    """docstring for GradeQtd."""

    class DataDim(DataSql):
        """docstring for DataDim."""
        def __init__(self, cursor, args, sql, **kwargs):
            self.id_field = \
                dict_def_options(kwargs, '', 'id', 'id_field')
            self.facade_field = \
                dict_def_options(kwargs, '', 'facade', 'facade_field',
                                             'id', 'id_field')
            self.name = kwargs.get('name', '')
            self.name_plural = kwargs.get('name_plural', self.name+'s')
            self.total = kwargs.get('total', '')
            super(GradeQtd.DataDim, self).__init__(cursor, args, sql)

        def execute(self, sql):
            data_dim = super(GradeQtd.DataDim, self).execute(sql)
            if self.total == '' or len(data_dim) == 1:
                self.idx_total = -1
            else:
                self.idx_total = len(data_dim)
                column = {self.id_field: self.total}
                if self.facade_field != self.id_field:
                    column[self.facade_field] = self.total
                data_dim.append(column)
            return data_dim

    def __init__(self, cursor, args=[]):
        self._cursor = cursor
        self.args = args
        self.total = 0

    def row(self, **kwargs):
        if 'sql' in kwargs:
            self._row = self.DataDim(
                self._cursor, self.args, **kwargs)
            if len(self._row.data) > 1 and self._row.name_plural:
                self._row.name = self._row.name_plural
            return self._row.data
        return None

    def col(self, **kwargs):
        if 'sql' in kwargs:
            self._col = self.DataDim(
                self._cursor, self.args, **kwargs)
            if len(self._col.data) > 1 and self._col.name_plural:
                self._col.name = self._col.name_plural
            return self._col.data
        return None

    def value(self, **kwargs):
        if 'sql' in kwargs:
            self._value = self.DataDim(
                self._cursor, self.args, **kwargs)
            self.do_table_data()
            return self._value.data
        return None

    def do_table_data(self):
        self.table_data = {
            'header': [],
            'fields': [],
            'data': [],
        }
        if len(self._col.data) != 0 and len(self._row.data) != 0:
            self.table_data['header'] = \
                ['{} / {}'.format(self._row.name, self._col.name)]
            self.table_data['fields'] = [self._row.id_field]
            for col in self._col.data:
                self.table_data['header'].append(col[self._col.facade_field])
                self.table_data['fields'].append(col[self._col.id_field])

            row_tots = {}
            for i in range(0, self._row.idx_total):
                row_tots[i] = 0
            if self._col.idx_total != -1:
                self._col.idx_total += 1
            col_tots = {}
            for i in range(1, self._col.idx_total):
                col_tots[i] = 0

            for i_row, row in enumerate(self._row.data):
                for i_field, field in enumerate(self.table_data['fields']):
                    if i_field == 0:
                        self.table_data['data'].append({})
                        self.table_data['data'][i_row][field] = \
                            row[self._row.facade_field]
                    else:
                        tot_row = i_row == self._row.idx_total
                        tot_col = i_field == self._col.idx_total

                        if not tot_row and not tot_col:
                            value_list = [
                                v[self._value.id_field]
                                for v in self._value.data
                                if v[self._row.id_field] ==
                                row[self._row.id_field]
                                and v[self._col.id_field] == field]
                            if len(value_list) == 1:
                                value = value_list[0]
                            else:
                                value = 0

                            self.table_data['data'][i_row][field] = value
                            self.total += value
                            if i_row in row_tots:
                                row_tots[i_row] += value
                            if i_field in col_tots:
                                col_tots[i_field] += value

                        if tot_row and not tot_col:
                            self.table_data['data'][i_row][field] = \
                                col_tots[i_field]

                        if not tot_row and tot_col:
                            self.table_data['data'][i_row][field] = \
                                row_tots[i_row]

                        if tot_row and tot_col:
                            self.table_data['data'][i_row][field] = self.total

        return self.table_data
