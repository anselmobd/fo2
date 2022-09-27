from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor, op):
    sql = f"""
        WITH filtro AS (
          SELECT
            {op} OP
          FROM dual
        )
        SELECT
          sum(l.QTDE_A_PRODUZIR_PACOTE) QTD
        FROM filtro f
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = f.op
        WHERE l.SEQUENCIA_ESTAGIO = 
            (
              SELECT
                max(ms.SEQUENCIA_ESTAGIO)
              FROM filtro f
              JOIN PCPC_040 ms
                ON ms.ORDEM_PRODUCAO = f.op
            )
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
