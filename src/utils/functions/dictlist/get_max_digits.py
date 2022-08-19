from pprint import pprint

__all__ = ['get_max_digits']


def get_max_digits(data, *fields, allways_tuple=False):
    max_digits = {
        field: 0
        for field in fields
    }
    for row in data:
        for field in fields:
            num_digits = str(row[field])[::-1].strip('0').find('.')
            max_digits[field] = max(max_digits[field], num_digits)
    if len(fields) == 1 and not allways_tuple:
        return max_digits[fields[0]]
    return tuple(
        max_digits[field]
        for field in fields
    )
