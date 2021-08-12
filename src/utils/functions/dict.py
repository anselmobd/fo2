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
