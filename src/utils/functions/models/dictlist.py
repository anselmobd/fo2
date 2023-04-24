import pandas as pd
from collections import defaultdict
from functools import lru_cache
from pprint import pprint

from django.db.models.base import ModelState


__all__ = [
    'dictlist_zip_columns',
    'custom_dictlist',
    'dictlist',
    'dictlist_lower',
    'dictlist_split',
    'queryset2dictlist',
    'dictlist2lower',
    'dictlist_indexed',
    'dict_def_options',
    'dict_options',
    'record2dict',
]


def dictlist_zip_columns(cursor, columns):
    return [
        dict(zip(columns, row))
        for row in cursor
    ]


def custom_dictlist(cursor, name_case=lambda x: x):
    columns = [name_case(i[0]) for i in cursor.description]
    return dictlist_zip_columns(cursor, columns)


def dictlist(cursor):
    return custom_dictlist(cursor)


def dictlist_lower(cursor):
    return custom_dictlist(cursor, name_case=str.lower)


def dictlist_split(dlist, rule):
    parts = defaultdict(list)
    for row in dlist:
        parts[rule(row)].append(row)
    return parts[True], parts[False]


def record_keys(record):
    return [
        key
        for key in record.__dict__
        if not isinstance(record.__dict__[key], ModelState)
    ]


def record_keys2dict(record, keys, fkey=lambda x: x):
    return {
        fkey(key): record.__dict__[key]
        for key in keys
    }


def record2dict(record, fkey=lambda x: x):
    return record_keys2dict(
        record,
        record_keys(record),
        fkey
    )


def queryset2dictlist(qs, filter=None):

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


def dictlist2lower(data):
    data_lower = []
    for row in data:
        row_lower = {}
        for key in row.keys():
            row_lower[key_lower(key)] = row[key]
        data_lower.append(row_lower)
    return data_lower


def df_dictlist2lower(data):
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


def dictlist_agg(data, key, agg_key=None, sep=', ', distinct=False):
    if not agg_key:
        agg_key = f"agg_{key}"
    rows = {}
    for row in data:
        data_key = tuple([
            row[k] for k in row if k != key
        ])

        try:
            rows[data_key]
        except KeyError:
            rows[data_key] = row
        row_base = rows[data_key]

        try:
            row_base[agg_key].append(row[key])
        except KeyError:
            row_base[agg_key] = [row[key]]

    result = rows.values()
    for row in result:
        if distinct:
            row[agg_key] = list(dict.fromkeys(row[agg_key]))
        row[agg_key] = sep.join(row[agg_key])

    return result
