from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute


def get_solicitacoes(cursor):
    sql = f"""
        SELECT DISTINCT
          sl.SOLICITACAO 
        , sum(CASE WHEN sl.SITUACAO = 1 THEN 1 ELSE 0 END) lotes_1
        , sum(CASE WHEN sl.SITUACAO = 1 THEN sl.QTDE ELSE 0 END) qtde_1
        , sum(CASE WHEN sl.SITUACAO = 2 THEN 1 ELSE 0 END) lotes_2
        , sum(CASE WHEN sl.SITUACAO = 2 THEN sl.QTDE ELSE 0 END) qtde_2
        , sum(CASE WHEN sl.SITUACAO = 3 THEN 1 ELSE 0 END) lotes_3
        , sum(CASE WHEN sl.SITUACAO = 3 THEN sl.QTDE ELSE 0 END) qtde_3
        , sum(CASE WHEN sl.SITUACAO = 4 THEN 1 ELSE 0 END) lotes_4
        , sum(CASE WHEN sl.SITUACAO = 4 THEN sl.QTDE ELSE 0 END) qtde_4
        , sum(CASE WHEN sl.SITUACAO = 5 THEN 1 ELSE 0 END) lotes_5
        , sum(CASE WHEN sl.SITUACAO = 5 THEN sl.QTDE ELSE 0 END) qtde_5
        , sum(1) lotes_tot
        , sum(sl.QTDE) qtde_tot
        FROM pcpc_044 sl -- solicitação / lote 
        WHERE sl.SOLICITACAO IS NOT NULL 
          AND sl.OP_DESTINO  > 0
        GROUP BY 
          sl.SOLICITACAO
        ORDER BY 
          sl.SOLICITACAO 
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
