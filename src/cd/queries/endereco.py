import operator
import re
from pprint import pprint

from systextil.queries.base import SMountQuery

from utils.functions.queries import debug_cursor_execute


def query_endereco(tipo):
    where_tipo = []
    if tipo == 'ES':
        where_tipo = [
            f"REGEXP_LIKE(e.COD_ENDERECO, '^1[ABCDEFGH][0123456789]{{4}}$')",
        ]
    elif tipo == 'NE':
        where_tipo = [
            "e.COD_ENDERECO LIKE '1%'",
            f"NOT REGEXP_LIKE(e.COD_ENDERECO, '^1[ABCDEFGH][0123456789]{{4}}$')",
        ]
    elif tipo == 'IN':
        where_tipo = [
            "e.COD_ENDERECO LIKE '1%'",
        ]
    elif tipo == 'EX':
        where_tipo = [
            "e.COD_ENDERECO NOT LIKE '1%'",
        ]
    elif tipo != 'TO':
        where_tipo = [
            f"REGEXP_LIKE(e.COD_ENDERECO, '^1{tipo}[0123456789]{{4}}$')",
        ]
    data = SMountQuery(
        fields=[
          "e.COD_ENDERECO end",
        ],
        table="ENDR_013 e",
        where=where_tipo,
        order=[
          f"e.COD_ENDERECO",
        ],
    ).oquery.debug_execute()

    for row in data:
        try:
            rua = re.search('^[0-9]([A-Z]+)[0-9]+', row['end']).group(1)
        except AttributeError:
            rua = '#'
        if rua in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            row['order'] = 1
            row['area'] = 'Estantes'
        elif rua.startswith('Q'):
            row['order'] = 2
            row['area'] = 'Quarto andar'
        elif (
                rua.startswith('S') or
                rua.startswith('Y')
              ):
            row['order'] = 3
            row['area'] = 'Externo'
        else:
            row['order'] = 4
            row['area'] = 'Indefinido'

    data.sort(key=operator.itemgetter('order', 'end'))

    return data

def endereco_split(endereco):
    """Split endereço em espaco, bloco, andar e ap"""
    try:
        busca = re.search('^([0-9])([A-Z]+)([0-9]{2})([0-9]{2})$', endereco)
    except AttributeError:
        return None, None, None
    return busca.group(1), busca.group(2), busca.group(3), busca.group(4)

def calc_rota(endereco):
    RUAS = {
        'A': 'AB',
        'B': 'AB',
        'C': 'CD',
        'D': 'CD',
        'E': 'EF',
        'F': 'EF',
        'G': 'GH',
        'H': 'GH',
    }
    espaco, bloco, andar, ap = endereco_split(endereco)
    if bloco <= 'H':
        iap = int(ap)
        irota = iap//2
        rua = RUAS[bloco]
        rota = f'{espaco}{rua}{irota:02}'
    else:
        rota = f'{espaco}{bloco}'
    return rota

