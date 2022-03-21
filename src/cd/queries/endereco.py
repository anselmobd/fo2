from pprint import pprint

from systextil.queries.base import SMountQuery

from utils.functions.queries import debug_cursor_execute


def query_endereco(tipo):
    where_tipo = []
    if tipo == 'E':
        where_tipo = [
            "e.COD_ENDERECO >= '1A0000'",
            "e.COD_ENDERECO <= '1H9999'",
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
