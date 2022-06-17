from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor):
    sql = f"""
        WITH lotes_605763 AS
        ( SELECT DISTINCT
            l.ORDEM_PRODUCAO OP
          , l.PERIODO_PRODUCAO PER
          , l.ORDEM_CONFECCAO OC
          , l.CODIGO_ESTAGIO EST
          , l.QTDE_PROGRAMADA QTD_LOTE
          FROM PCPC_040 l 
          WHERE 1=1
            AND l.QTDE_DISPONIVEL_BAIXA > 0
            AND (
              l.CODIGO_ESTAGIO = 60
              OR l.CODIGO_ESTAGIO = 57
              OR l.CODIGO_ESTAGIO = 63
            )
            AND l.PROCONF_GRUPO in ('0156M') -- filter_ref
            AND l.PROCONF_SUBGRUPO = 'M' -- filter_cor
            AND l.PROCONF_ITEM = '0000AJ' -- filter_cor
        )
        , lotes_605763end AS 
        ( SELECT DISTINCT 
            l.OP
          , l.PER
          , l.OC
          , l.QTD_LOTE
          FROM lotes_605763 l
          LEFT JOIN ENDR_014 lp
            ON lp.ORDEM_PRODUCAO = l.OP
          AND lp.ORDEM_CONFECCAO = l.PER * 100000 + l.OC
          WHERE 1=1
            AND (
              l.EST <> 63
              OR lp.ORDEM_PRODUCAO IS NOT NULL
            )
        )
        SELECT 
          l.*
        FROM lotes_605763end l
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
