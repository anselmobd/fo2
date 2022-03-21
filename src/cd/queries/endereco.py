from pprint import pprint

from systextil.queries.base import SMountQuery

from utils.functions.queries import debug_cursor_execute


def query_endereco(tipo):
    where_tipo = []
    if tipo == 'ES':
        where_tipo = [
            f"REGEXP_LIKE(e.COD_ENDERECO, '^1[ABCDEFGH][0123456789]{{4}}$')",
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
    return SMountQuery(
        fields=[
          "e.COD_ENDERECO end",
        ],
        table="ENDR_013 e",
        where=where_tipo,
        order=[
          f"e.COD_ENDERECO",
        ],
    ).oquery.debug_execute()
