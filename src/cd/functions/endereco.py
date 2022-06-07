import re
from pprint import pprint


def endereco_split(endereco):
    """Split endereço em espaco, bloco e apartamento; e este último em andar e coluna"""
    parts = {
        'espaco' : None,
        'bloco' : None,
        'apartamento' : None,
        'andar' : None,
        'coluna' : None,
    }
    if not endereco:
        return parts
    try:
        end_parts = re.search('^([0-9])([A-Z]?[0-9]?[A-Z])([0-9]+)$', endereco)
    except Exception:
        end_parts = None
    if end_parts:
        try:
            parts['espaco'] = end_parts.group(1)
            parts['bloco'] = end_parts.group(2)
            parts['apartamento'] = end_parts.group(3)
        except AttributeError:
            end_parts = None
    if end_parts:
        if parts['apartamento'] and len(parts['apartamento']) >= 4:
            try:
                ap_parts = re.search('^([0-9]+)([0-9]{2})$', parts['apartamento'])
                parts['andar'] = ap_parts.group(1)
                parts['coluna'] = ap_parts.group(2)
            except Exception:
                pass
    else:
        parts['espaco'] = endereco[0]
        parts['bloco'] = endereco[1:]
    return parts


def calc_rota(endereco):
    ruas = {
        'A': 'AB',
        'B': 'AB',
        'C': 'CD',
        'D': 'CD',
        'E': 'EF',
        'F': 'EF',
        'G': 'GH',
        'H': 'GH',
    }
    parts = endereco_split(endereco)
    if parts['bloco'] in ruas:
        icoluna = int(parts['coluna'])
        irota = icoluna//2
        rua = ruas[parts['bloco']]
        rota = f"{parts['espaco']}{rua}{irota:02}"
    else:
        rota = f"{parts['espaco']}{parts['bloco']}"
    return rota
