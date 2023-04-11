from pprint import pprint


__all__ = ['key_dict']


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
        for row in [
            dict(zip(columns, cursor_row))
            for cursor_row in cursor
        ]
    }