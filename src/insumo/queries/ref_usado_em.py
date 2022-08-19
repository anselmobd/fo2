from pprint import pprint

from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(cursor, nivel, ref):
    sql = f"""
        SELECT DISTINCT
          CASE WHEN e.NIVEL_ITEM = 1 THEN
            CASE WHEN r.REFERENCIA <= '99999' THEN 'PA'
            WHEN r.REFERENCIA like 'A%' or r.REFERENCIA like 'B%' THEN 'PG'
            WHEN r.REFERENCIA like 'Z%' THEN 'MP'
            ELSE 'MD'
            END
          WHEN e.NIVEL_ITEM = 5 THEN 'RE'
          ELSE 'MP'
          END TIPO
        , e.SUB_COMP TAM_COMP
        , e.ITEM_COMP COR_COMP
        , e.NIVEL_ITEM NIVEL
        , e.GRUPO_ITEM REF
        , e.SUB_ITEM TAM
        , e.ITEM_ITEM COR
        , e.GRUPO_ITEM REF
        , r.DESCR_REFERENCIA DESCR
        , e.ALTERNATIVA_ITEM ALTERNATIVA
        , e.CONSUMO
        , e.ESTAGIO || '-' || es.DESCRICAO ESTAGIO
        FROM BASI_050 e
        LEFT JOIN basi_030 r
          ON r.NIVEL_ESTRUTURA = e.NIVEL_ITEM
         AND r.REFERENCIA = e.GRUPO_ITEM
        LEFT JOIN MQOP_005 es
          ON es.CODIGO_ESTAGIO = e.ESTAGIO
        WHERE 1=1
          AND (
            ( e.NIVEL_ITEM = 1
            AND r.RESPONSAVEL IS NOT NULL
            )
          OR e.NIVEL_ITEM <> 1
          )
          AND e.NIVEL_COMP = {nivel}
          AND e.GRUPO_COMP = '{ref}'
        ORDER BY
          e.SUB_COMP
        , e.ITEM_COMP
        , NLSSORT(e.GRUPO_ITEM,'NLS_SORT=BINARY_AI')
        , e.ALTERNATIVA_ITEM
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
