from curses.ascii import isdigit
from pprint import pprint

from systextil.queries.base import SMountQuery

from utils.functions.queries import debug_cursor_execute

from cd.classes.palete import Plt


def query_palete():
    return SMountQuery(
        fields=[
          "co.COD_CONTAINER palete",
          "COALESCE(co.TUSSOR_IMPRESSA, 'N') impressa",
        ],
        table="ENDR_012 co",
        where=[
            "co.COD_CONTAINER LIKE 'P%'",
        ],
        order=[
          "co.COD_CONTAINER DESC",
        ],
    ).oquery.debug_execute()


def add_palete(cursor):
    paletes = query_palete()
    if len(paletes) == 0:
        palete = Plt().mount(1)
    else:
        palete = Plt(paletes[0]['palete']).next()

    sql = f"""
        INSERT INTO SYSTEXTIL.ENDR_012
        (COD_CONTAINER, COD_TIPO, ENDERECO, TARA_CONTAINER, QUANTIDADE_MAXIMO, ULTIMA_ATUALIZACAO_TARA, SITUACAO)
        VALUES('{palete}', 1, NULL, 1, 1, CURRENT_TIMESTAMP, '1')
    """

    try:
        debug_cursor_execute(cursor, sql)
        return True, ''
    except Exception as e:
        return False, repr(e)
