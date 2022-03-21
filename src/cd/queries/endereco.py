from pprint import pprint

from systextil.queries.base import SMountQuery

from utils.functions.queries import debug_cursor_execute


def query_endereco():
    return SMountQuery(
        fields=[
          "e.COD_ENDERECO end",
        ],
        table="ENDR_013 e",
        order=[
          f"e.COD_ENDERECO",
        ],
    ).oquery.debug_execute()
