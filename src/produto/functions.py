

def papg_modelo(papg):
    modelo = ''.join(filter(str.isdigit, papg))
    return modelo.lstrip('0')
