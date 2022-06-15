from pprint import pprint

from django.db.models.base import ModelState

__all__ = [
    'rows_to_key_dict',
    'dictlist_zip_columns',
    'custom_dictlist',
    'dictlist',
    'dictlist_lower',
    'queryset_to_dictlist_lower',
    'dictlist_to_lower',
    'dictlist_indexed',
    'dict_def_options',
    'dict_options',
    'record2dict',
]


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

    return {
        fkey(values, keys): fvalue(values, no_keys)
        for values in dictlist_zip_columns(cursor, columns)
    }


def dictlist_zip_columns(cursor, columns):
    return [
        dict(zip(columns, row))
        for row in cursor
    ]


def custom_dictlist(cursor, name_case=None):
    if name_case is None:
        columns = [i[0] for i in cursor.description]
    else:
        columns = [name_case(i[0]) for i in cursor.description]
    return dictlist_zip_columns(cursor, columns)


def dictlist(cursor):
    return custom_dictlist(cursor)


def dictlist_lower(cursor):
    return custom_dictlist(cursor, name_case=str.lower)


def queryset_to_dictlist_lower(qs):
    result = []
    for obj in qs:
        result.append({
            name.lower(): obj.__dict__[name]
            for name in obj.__dict__
            if name[0] != '_'
        })
    return result


def dictlist_to_lower(data):
    data_lower = []
    for row in data:
        row_lower = {}
        for key in row.keys():
            row_lower[key.lower()] = row[key]
        data_lower.append(row_lower)
    return data_lower


def dictlist_indexed(data, key):
    indexed = {}
    for row in data:
        indexed[row[key]] = row
    return indexed


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


def record2dict(rec):
    return {
        k:rec.__dict__[k]
        for k in rec.__dict__
        if not isinstance(rec.__dict__[k], ModelState)
    }
