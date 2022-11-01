from collections import OrderedDict
from pprint import pprint


def equal_dicts(d1, d2):
    ''' Devolve True se dicionários são iguais.
    Só funciona se todos os valores forem serializáveis.
    '''
    return len(d1.items() ^ d2.items()) == 0


def update_dict(original, adding):
    result = original.copy()
    for key in adding.keys():
        if adding[key] is None:
            continue
        if isinstance(adding[key], dict):
            if key not in result or not isinstance(result[key], dict):
                result[key] = adding[key].copy()
            else:
                result[key] = update_dict(result[key], adding[key])
        else:
            result[key] = adding[key]
    return result


def dict_firsts(adict, firsts):
    eh_ordered = isinstance(adict, OrderedDict)
    if not eh_ordered:
        adict = OrderedDict(adict)
    keys = list(adict.keys())
    for key in keys:
        if key not in firsts:
            adict.move_to_end(key)
    if eh_ordered:
        return adict
    else:
        return dict(adict)


def dict_get_none(dic, key):
    try:
        value = dic[key]
    except KeyError:
        value = dic.get(None)
    return value
