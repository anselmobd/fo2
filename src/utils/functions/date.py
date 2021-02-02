from pprint import pprint


__dow_info = {
    0: {'name': 'segunda-feira', 'plural': 'segundas-feiras',
        'alias': 'segunda', 'abb': 'seg'},
    1: {'name': 'terça-feira', 'plural': 'terças-feiras',
        'alias': 'terça', 'abb': 'ter'},
    2: {'name': 'quarta-feira', 'plural': 'quartas-feiras',
        'alias': 'quarta', 'abb': 'qua'},
    3: {'name': 'quinta-feira', 'plural': 'quintas-feiras',
        'alias': 'quinta', 'abb': 'qui'},
    4: {'name': 'sexta-feira', 'plural': 'sextas-feiras',
        'alias': 'sexta', 'abb': 'sex'},
    5: {'name': 'sábado', 'plural': 'sábados',
        'alias': 'sábado', 'abb': 'sab'},
    6: {'name': 'domingo', 'plural': 'domingos',
        'alias': 'domingo', 'abb': 'dom'},
}


def dow_info(dt, info, capitalize=False):
    dow = dt.weekday()
    result = __dow_info[dow][info]
    if capitalize:
        result = result.capitalize()
    return result
