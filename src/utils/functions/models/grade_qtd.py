__all__ = ['GradeQtd']

from pprint import pprint

from utils.functions.models.data_sql import DataSql
from utils.functions.models.dictlist import dict_def_options


class GradeQtd(object):
    """docstring for GradeQtd."""

    class DataDim(DataSql):
        """docstring for DataDim."""
        def __init__(self, cursor, args, sql, case=None, **kwargs):
            self.id_field = \
                dict_def_options(kwargs, '', 'id', 'id_field')
            self.facade_field = \
                dict_def_options(kwargs, '', 'facade', 'facade_field',
                                             'id', 'id_field')
            self.name = kwargs.get('name', '')
            self.name_plural = kwargs.get('name_plural', self.name+'s')
            self.total = kwargs.get('total', '')
            self.forca_total = kwargs.get('forca_total', False)
            super(GradeQtd.DataDim, self).__init__(cursor, args, sql, case=case)

        def execute(self, sql):
            data_dim = super(GradeQtd.DataDim, self).execute(sql)
            self.niveis = len(data_dim)
            if self.total == '' or \
                    (self.niveis == 1 and not self.forca_total):
                self.idx_total = -1
            else:
                self.idx_total = len(data_dim)
                column = {self.id_field: self.total}
                if self.facade_field != self.id_field:
                    column[self.facade_field] = self.total
                data_dim.append(column)
            return data_dim

    def __init__(self, cursor, args=[], case=None):
        self._cursor = cursor
        self.args = args
        self.case = case
        self.total = 0
        self._table_data = None

    def row(self, **kwargs):
        if 'sql' in kwargs:
            self._row = self.DataDim(
                self._cursor, self.args, case=self.case, **kwargs)
            if len(self._row.data) > 1 and self._row.name_plural:
                self._row.name = self._row.name_plural
            return self._row.data
        return None

    def col(self, **kwargs):
        if 'sql' in kwargs:
            self._col = self.DataDim(
                self._cursor, self.args, case=self.case, **kwargs)
            if len(self._col.data) > 1 and self._col.name_plural:
                self._col.name = self._col.name_plural
            return self._col.data
        return None

    def value(self, **kwargs):
        if 'sql' in kwargs:
            self._value = self.DataDim(
                self._cursor, self.args, case=self.case, **kwargs)
            return self._value.data
        return None

    def do_table_data(self):
        self._table_data = {
            'header': [],
            'fields': [],
            'data': [],
            'row_tot': False,
            'col_tot': False,
            'style': {},
        }
        right_style = 'text-align: right;'
        bold_style = 'font-weight: bold;'

        if len(self._col.data) != 0 and len(self._row.data) != 0:
            self._table_data['header'] = \
                ['{} / {}'.format(self._row.name, self._col.name)]
            self._table_data['fields'] = [self._row.id_field]
            for col in self._col.data:
                self._table_data['header'].append(col[self._col.facade_field])
                self._table_data['fields'].append(col[self._col.id_field])

            row_tots = {}
            if self._col.idx_total != -1:
                self._table_data['row_tot'] = True
                for i in range(0, self._row.niveis):
                    row_tots[i] = 0

            col_tots = {}
            if self._row.idx_total != -1:
                self._table_data['col_tot'] = True
                for i in range(0, self._col.niveis):
                    col_tots[i+1] = 0

            if self._col.idx_total != -1:
                self._col.idx_total += 1

            for i_row, row in enumerate(self._row.data):
                for i_field, field in enumerate(self._table_data['fields']):
                    if i_field == 0:
                        self._table_data['data'].append({})
                        self._table_data['data'][i_row][field] = \
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

                            self._table_data['data'][i_row][field] = value
                            self.total += value
                            if i_row in row_tots:
                                row_tots[i_row] += value
                            if i_field in col_tots:
                                col_tots[i_field] += value

                        if tot_row and not tot_col:
                            self._table_data['data'][i_row][field] = \
                                col_tots[i_field]

                        if not tot_row and tot_col:
                            self._table_data['data'][i_row][field] = \
                                row_tots[i_row]

                        if tot_row and tot_col:
                            self._table_data['data'][i_row][field] = self.total

            len_fields = len(self._table_data['fields'])
            for i in range(2, len_fields+1):
                self._table_data['style'][i] = right_style

            if row_tots != {}:
                self._table_data['style'][len_fields] = (
                    self._table_data['style'][len_fields] + bold_style)

            if col_tots != {}:
                self._table_data['data'][-1]['|STYLE'] = bold_style

        return self._table_data

    @property
    def table_data(self):
        if self._table_data is None:
            return self.do_table_data()
        return self._table_data

    @table_data.setter
    def table_data(self, value):
        self._table_data = value
