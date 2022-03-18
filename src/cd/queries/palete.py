from curses.ascii import isdigit
from pprint import pprint

from systextil.queries.base import SMountQuery

from utils.functions.queries import debug_cursor_execute


def query_palete():
    return SMountQuery(
        fields=[
          "co.COD_CONTAINER palete",
        ],
        table="ENDR_012 co",
        where=[
            "co.COD_CONTAINER LIKE 'PLT%'",
        ],
        order=[
          "co.COD_CONTAINER DESC",
        ],
    ).oquery.debug_execute()


def add_palete(cursor):
    paletes = query_palete()
    if len(paletes) == 0:
        next_palete = 1
    else:
        palete = paletes[0]['palete']
        numeros = palete[3:7]
        if numeros.isdigit():
            next_palete = int(numeros) + 1
        else:
            return False, "Último palete inválido"

    numeros = f"{next_palete:04d}"

    sql = f"""
        INSERT INTO SYSTEXTIL.ENDR_012
        (COD_CONTAINER, COD_TIPO, ENDERECO, TARA_CONTAINER, QUANTIDADE_MAXIMO, ULTIMA_ATUALIZACAO_TARA, SITUACAO)
        VALUES('PLT{next_palete:04d}A', 1, NULL, 1, 1, CURRENT_TIMESTAMP, '1')
    """

    try:
        debug_cursor_execute(cursor, sql)
        return True, ''
    except Exception as e:
        return False, repr(e)
