from pprint import pprint


def rows_to_key_dict(cursor, keys):

    def fkeys(row, keys):
        return tuple((key, row[key]) for key in keys)

    def fvalue(row, keys):
        return row[keys[0]]

    def fdict(row, keys):
        return {key: row[key] for key in keys}

    if isinstance(keys, tuple):
        fkey = fkeys
    else:
        keys = (keys, )
        fkey = fvalue

    columns = [i[0] for i in cursor.description]
    no_keys = tuple(column for column in columns if column not in keys)

    if len(no_keys) == 1:
        fvalue = fvalue
    else:
        fvalue = fdict

    return {fkey(values, keys): fvalue(values, no_keys)
            for values in [dict(zip(columns, row))
                           for row in cursor]}


def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def rows_to_dict_list_lower(cursor):
    columns = [i[0].lower() for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def queryset_to_dict_list_lower(qs):
    result = []
    for obj in qs:
        result.append({
            name.lower(): obj.__dict__[name] for name in obj.__dict__
            if name[0] != '_'
        })
    return result


def dict_list_to_lower(data):
    data_lower = []
    for row in data:
        row_lower = {}
        for key in row.keys():
            row_lower[key.lower()] = row[key]
        data_lower.append(row_lower)
    return data_lower


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
            self.forca_total = kwargs.get('forca_total', False)
            super(GradeQtd.DataDim, self).__init__(cursor, args, sql)

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

    def __init__(self, cursor, args=[]):
        self._cursor = cursor
        self.args = args
        self.total = 0
        self._table_data = None

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
