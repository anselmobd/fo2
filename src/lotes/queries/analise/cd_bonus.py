from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['cd_bonus_query']


def cd_bonus_query(
    cursor,
    data=None,
):
    filtra_data = f"""--
        AND ml.DATA_PRODUCAO >= DATE '{data}'
        AND ml.DATA_PRODUCAO < DATE '{data}' + 1
    """ if data else ''
    sql = f"""
        SELECT
          u.USUARIO
        , l.PROCONF_GRUPO REF
        , sum(ml.QTDE_PRODUZIDA) qtd
        --, ml.*
        FROM PCPC_045 ml
        JOIN PCPC_040 l
          ON l.PERIODO_PRODUCAO = ml.PCPC040_PERCONF 
         AND l.ORDEM_CONFECCAO = ml.PCPC040_ORDCONF 
         AND l.CODIGO_ESTAGIO = ml.PCPC040_ESTCONF 
        JOIN HDOC_030 u 
          ON u.CODIGO_USUARIO = ml.CODIGO_USUARIO
        WHERE 1=1
          {filtra_data} -- filtra_data
          AND ml.PCPC040_ESTCONF = 63
        GROUP BY 
          u.USUARIO
        , l.PROCONF_GRUPO
        ORDER BY 
          u.USUARIO
        , l.PROCONF_GRUPO
    """
    debug_cursor_execute(cursor, sql)
    data = dictlist_lower(cursor)

    return data
