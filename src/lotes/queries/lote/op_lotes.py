from pprint import pprint

from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(cursor, op):
    sql = f'''
        WITH
        filtro AS (
        SELECT 
          {op} OP
        FROM dual
        ),
        ocs AS (
          SELECT DISTINCT 
            l.PERIODO_PRODUCAO PER
          , l.ORDEM_CONFECCAO OC
          , min(l.SEQUENCIA_ESTAGIO) SEQ1
          , min(
              CASE
              WHEN l.QTDE_DISPONIVEL_BAIXA > 0
                OR l.QTDE_CONSERTO > 0
              THEN l.CODIGO_ESTAGIO
              ELSE 999
              END
            ) EST
          , min(
              CASE
              WHEN l.NUMERO_ORDEM > 0
              THEN l.CODIGO_ESTAGIO
              ELSE 999
              END
            ) EST_OS
          , max(l.NUMERO_ORDEM) OS
          FROM filtro f
          JOIN PCPC_040 l
            ON l.ORDEM_PRODUCAO = f.OP
          GROUP BY 
            l.PERIODO_PRODUCAO
          , l.ORDEM_CONFECCAO
        ),
        lotes AS (
          SELECT 
            ocs.EST
          , ed.DESCRICAO EST_DESCR
          , ocs.OS
          , ocs.EST_OS
          , eod.DESCRICAO EST_OS_DESCR
          , l.PROCONF_GRUPO REF
          , l.PROCONF_ITEM COR
          , l.PROCONF_SUBGRUPO TAM
          , t.ORDEM_TAMANHO TAM_ORD
          , ocs.PER
          , ocs.OC
          , l.QTDE_PECAS_PROG QTD
          FROM ocs
          JOIN PCPC_040 l
            ON l.PERIODO_PRODUCAO = ocs.PER 
           AND l.ORDEM_CONFECCAO = ocs.OC
           AND l.SEQUENCIA_ESTAGIO = ocs.SEQ1
          LEFT JOIN BASI_220 t
            ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
          LEFT JOIN MQOP_005 ed
            ON ed.CODIGO_ESTAGIO = ocs.EST
          LEFT JOIN MQOP_005 eod
            ON eod.CODIGO_ESTAGIO = ocs.EST_OS
        )
        SELECT
          CASE
            WHEN l.EST = 999
            THEN 'FINALIZADO'
            ELSE l.EST || ' - ' || l.EST_DESCR 
          END EST
        , CASE WHEN l.OS = 0
            THEN '-'
            ELSE l.OS || ' (' || l.EST_OS_DESCR || ')'
          END OS
        , l.REF
        , l.COR
        , l.TAM
        , l.PER PERIODO
        , l.OC
        , l.QTD
        FROM lotes l
        ORDER BY 
          l.EST
        , l.OS
        , l.REF
        , l.COR
        , l.TAM_ORD
        , l.PER
        , l.OC
    '''
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
