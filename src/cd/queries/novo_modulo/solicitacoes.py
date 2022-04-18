from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute


def get_solicitacoes(cursor):
    sql = f"""
        SELECT DISTINCT
          sl.SOLICITACAO 
        , sum(CASE WHEN sl.SITUACAO = 1 THEN 1 ELSE 0 END) l1
        , sum(CASE WHEN sl.SITUACAO = 1 THEN sl.QTDE ELSE 0 END) q1
        , sum(CASE WHEN sl.SITUACAO = 2 THEN 1 ELSE 0 END) l2
        , sum(CASE WHEN sl.SITUACAO = 2 THEN sl.QTDE ELSE 0 END) q2
        , sum(CASE WHEN sl.SITUACAO = 3 THEN 1 ELSE 0 END) l3
        , sum(CASE WHEN sl.SITUACAO = 3 THEN sl.QTDE ELSE 0 END) q3
        , sum(CASE WHEN sl.SITUACAO = 4 THEN 1 ELSE 0 END) l4
        , sum(CASE WHEN sl.SITUACAO = 4 THEN sl.QTDE ELSE 0 END) q4
        , sum(CASE WHEN sl.SITUACAO = 5 THEN 1 ELSE 0 END) l5
        , sum(CASE WHEN sl.SITUACAO = 5 THEN sl.QTDE ELSE 0 END) q5
        , sum(CASE WHEN l.CODIGO_ESTAGIO IS NULL THEN 1 ELSE 0 END) lf
        , sum(CASE WHEN l.CODIGO_ESTAGIO IS NULL THEN sl.QTDE ELSE 0 END) qf
        , sum(CASE WHEN l.CODIGO_ESTAGIO IS NOT NULL THEN 1 ELSE 0 END) lp
        , sum(CASE WHEN l.CODIGO_ESTAGIO IS NOT NULL THEN sl.QTDE ELSE 0 END) qp
        , sum(1) lt
        , sum(sl.QTDE) qt
        FROM pcpc_044 sl -- solicitação / lote 
        LEFT JOIN PCPC_040 l
          ON l.QTDE_EM_PRODUCAO_PACOTE > 0
         AND l.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND l.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
        WHERE sl.SOLICITACAO IS NOT NULL 
        GROUP BY 
          sl.SOLICITACAO
        ORDER BY 
          sl.SOLICITACAO 
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def get_solicitacao(cursor, id):
    sql = f"""
        SELECT DISTINCT
          sl.*
        , lest.CODIGO_ESTAGIO
        , l.PROCONF_NIVEL99 NIVEL
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        FROM pcpc_044 sl -- solicitação / lote 
        LEFT JOIN PCPC_040 lest
          ON lest.QTDE_EM_PRODUCAO_PACOTE > 0
         AND lest.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND lest.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
        LEFT JOIN PCPC_040 l
          ON l.SEQUENCIA_ESTAGIO = 1
         AND l.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND l.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
        WHERE sl.SOLICITACAO  = {id}
        ORDER BY
          sl.SITUACAO
        , lest.CODIGO_ESTAGIO
        , sl.ORDEM_PRODUCAO
        , sl.ORDEM_CONFECCAO
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
