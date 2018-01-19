import fdb

from django.db import models

from fo2.settings import DB_F1


def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def rows_to_dict_list_lower(cursor):
    columns = [i[0].lower() for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]

def cursorF1():
    con = fdb.connect(
        dsn='{}/{}:{}'.format(DB_F1['HOST'], DB_F1['PORT'], DB_F1['NAME']),
        user=DB_F1['USER'],
        password=DB_F1['PASSWORD'],
        charset=DB_F1['CHARSET']
        )
    return con.cursor()


def dict_def_options(dict_, def_, *args):
    """
    Return dict_[arg] for first arg in args that exists in dict_.
    Otherwise, return default value.
    """
    for arg in args:
        if arg in dict_:
            return dict_[arg]
    return def_


def dict_options(dict_, *args):
    """
    Call dict_def_options with default value None
    """
    return dict_def_options(dict_, None, *args)


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


class GradeQtd(object):
    """docstring for GradeQtd."""

    class DataDim(DataSql):
        """docstring for DataDim."""
        def __init__(self, cursor, args, sql, **kwargs):
            self.id_field = \
                dict_def_options(kwargs, '', 'id', 'id_field')
            self.facade_field = \
                dict_def_options(kwargs, '', 'facade', 'facade_field'
                                             'id', 'id_field')
            self.name = kwargs.get('name', '')
            self.name_plural = kwargs.get('name_plural', self.name+'s')
            super(GradeQtd.DataDim, self).__init__(cursor, args, sql)

    def __init__(self, cursor, args=[]):
        self._cursor = cursor
        self.args = args

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
                self.table_data['header'].append(col[self._col.id_field])
                self.table_data['fields'].append(col[self._col.id_field])

            for i_row, row in enumerate(self._row.data):
                for i_field, field in enumerate(self.table_data['fields']):
                    if i_field == 0:
                        self.table_data['data'].append({})
                        self.table_data['data'][i_row][field] = \
                            row[self._row.facade_field]
                    else:
                        self.table_data['data'][i_row][field] = 0
                        for value in self._value.data:
                            if value[self._row.id_field] \
                                == row[self._row.id_field] and \
                                    value[self._col.id_field] == field:
                                self.table_data['data'][i_row][field] = \
                                    value[self._value.id_field]
                                break

        return self.table_data
