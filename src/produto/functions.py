

def papg_modelo(papg):
    modelo = ''.join(filter(str.isdigit, papg))
    return modelo.lstrip('0')


def item_str(nivel, ref, tam, cor):
    return f'{nivel}.{ref}.{tam}.{cor}'
