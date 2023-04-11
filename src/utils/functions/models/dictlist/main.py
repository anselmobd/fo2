import pandas as pd
from functools import lru_cache
from pprint import pprint

from django.db.models.base import ModelState


__all__ = [
    'key_dict',
    'dictlist_zip_columns',
    'custom_dictlist',
    'dictlist',
    'dictlist_lower',
    'dictlist_split',
    'queryset_to_dictlist',
    'dictlist_to_lower',
    'dictlist_indexed',
    'dict_def_options',
    'dict_options',
    'record2dict',
]


def key_dict(cursor, keys, simple_key=True, simple_value=True):

    def fkeys(row, keys):
        if simple_key:
            return tuple(row[key] for key in keys)
        else:
            return tuple((key, row[key]) for key in keys)

    def fvalue(row, keys):
        return row[keys[0]]

    def fdict(row, keys):
        return {key: row[key] for key in keys}

    if not isinstance(keys, (list, tuple)):
        keys = (keys, )

    if simple_key and len(keys) == 1:
        fkey = fvalue
    else:
        fkey = fkeys

    columns = [i[0] for i in cursor.description]
    no_keys = tuple(column for column in columns if column not in keys)

    if simple_value and len(no_keys) == 1:
        fvalue = fvalue
    else:
        fvalue = fdict

    return {
        fkey(row, keys): fvalue(row, no_keys)
        for row in dictlist_zip_columns(cursor, columns)
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


def dictlist_split(dlist, f_rule):
    list1 = []
    list2 = []
    for row in dlist:
        if f_rule(row):
            list1.append(row)
        else:
            list2.append(row)
    return list1, list2


def record_keys(record):
    return [
        key
        for key in record.__dict__
        if not isinstance(record.__dict__[key], ModelState)
    ]


def record_keys2dict(record, keys, fkey=lambda x:x):
    return {
        fkey(key): record.__dict__[key]
        for key in keys
    }


def record2dict(record, fkey=lambda x:x):
    return record_keys2dict(
        record,
        record_keys(record),
        fkey
    )


def queryset_to_dictlist(qs, filter=None):

    def filter_ok(obj):
        tests = [True]
        for key in filter:
            value = getattr(obj, key, None)
            tests.append(
                value == filter[key]
            )
        return all(tests)

    apply_filter = filter_ok
    if not filter:
        filter = {}
    elif callable(filter):
        apply_filter = filter

    result = []
    for i, obj in enumerate(qs):
        if i == 0:
            keys = record_keys(obj)
        if apply_filter(obj):
            result.append(record_keys2dict(obj, keys, key_lower))
    return result


@lru_cache(maxsize=128)
def key_lower(text):
    return text.lower()


def dictlist_to_lower(data):
    data_lower = []
    for row in data:
        row_lower = {}
        for key in row.keys():
            row_lower[key_lower(key)] = row[key]
        data_lower.append(row_lower)
    return data_lower


def df_dictlist_to_lower(data):
    df = pd.DataFrame(data)
    df.columns= df.columns.str.lower()
    return df.to_dict('records')


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
        try:
            return dictionary[arg]
        except KeyError:
            pass
    return default


def dict_options(dictionary, *args):
    """
    Call dict_def_options with default value None
    """
    return dict_def_options(dictionary, None, *args)
