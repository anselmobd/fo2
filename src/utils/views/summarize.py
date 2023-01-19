import copy
from pprint import pprint


def brif(data, keys=[], sum=[]):
    empty = {
        sum_key: 0
        for sum_key in sum
    }
    empty['brif_count'] = 0
    items = {}
    for row in data:
        kvalues = tuple(
            row[key]
            for key in keys
        )
        if kvalues not in items:
            items[kvalues] = copy.deepcopy(empty)
        for sum_key in sum:
            items[kvalues][sum_key] += row[sum_key]
        items[kvalues]['brif_count'] += 1

    result = []
    for kvalues in items:
        row = dict(zip(keys, kvalues))
        for sum_key in sum:
             row[sum_key] = items[kvalues][sum_key]
        row['brif_count'] = items[kvalues]['brif_count']
        result.append(row)

    return result
