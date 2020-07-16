from pprint import pprint


def search_in_dict_fields(search, row, *fields, **params):
    ignore_case = params.get('ignore_case', True)
    for part in search.split():
        for field in fields:
            pattern = part.lower() if ignore_case else part
            value = row[field].lower() if ignore_case else row[field]
            if pattern in value:
                return True
    return False


def filtered_data_fields(search, data, *fields, **params):
    result = []
    for row in data:
        if search_in_dict_fields(search, row, *fields, **params):
            result.append(row)
    return result
