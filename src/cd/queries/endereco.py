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
    elif tipo == 'QA':
        where_tipo = [
            f"REGEXP_LIKE(e.COD_ENDERECO, '^1Q[0123456789]{{4}}$')",
        ]
    elif tipo == 'LA':
        where_tipo = [
            f"REGEXP_LIKE(e.COD_ENDERECO, '^1L[0123456789]{{4}}$')",
        ]
    elif tipo == 'NG':
        where_tipo = [
            "e.COD_ENDERECO LIKE '1%'",
            f"NOT REGEXP_LIKE(e.COD_ENDERECO, '^1[ABCDEFGHLQ][0123456789]{{4}}$')",
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
          "e.ROTA",
        ],
        table="ENDR_013 e",
        where=where_tipo,
        order=[
          f"e.COD_ENDERECO",
        ],
    ).oquery.debug_execute()

    for row in data:
        parts = endereco_split(row['end'])
        row['bloco'] = parts['bloco']
        row['andar'] = parts['andar']
        row['coluna'] = parts['coluna']
        if parts['bloco'] in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']:
            row['prioridade'] = 1
            row['order_ap'] = 10000 + int(parts['coluna']) * 100 + int(parts['andar'])
            row['espaco'] = 'Estantes'
        elif parts['bloco'].startswith('Q'):
            row['prioridade'] = 2
            row['order_ap'] = int(parts['apartamento'])
            row['espaco'] = 'Quarto andar'
        elif (
                parts['bloco'].startswith('S') or
                parts['bloco'].startswith('Y')
              ):
            row['prioridade'] = 3
            row['order_ap'] = 0
            row['espaco'] = 'Externo'
        else:
            row['prioridade'] = 4
            row['order_ap'] = 0
            row['espaco'] = 'Indefinido'

    data.sort(key=operator.itemgetter('prioridade', 'bloco', 'order_ap'))

    return data


def endereco_split(endereco):
    """Split endereço em espaco, bloco e apartamento; e este último em andar e coluna"""
    parts = {
        'espaco' : None,
        'bloco' : None,
        'apartamento' : None,
        'andar' : None,
        'coluna' : None,
    }
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


def add_endereco(cursor, endereco):
    """Cria endereco no banco de dados
    Recebe: cursor e endereco a ser criado
    Retorna: Se sucesso, None, senão, mensagem de erro
    """
    rota = calc_rota(endereco)
    sql = f"""
        INSERT INTO SYSTEXTIL.ENDR_013
        (RUA, BOX, ALTURA, COD_ENDERECO, EMPRESA, PROCESSO, SITUACAO, TIPO_ENDERECO, ROTA)
        VALUES(NULL, NULL, NULL, '{endereco}', 1, 1, '1', '1', '{rota}')
    """
    try:
        debug_cursor_execute(cursor, sql)
    except Exception as e:
        return repr(e)
