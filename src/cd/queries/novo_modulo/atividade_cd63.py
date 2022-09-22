from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(cursor, data_de, data_ate):

    sql = f"""
        SELECT
          trunc(h.DATA_HORA) DATA
        , h.USUARIO
        , h.ATIVIDADE
        , count(*) QTD
        FROM ENDR_016_HIST h -- histórico de endereçamento
        WHERE 1=1
          AND h.DATA_HORA >= DATE '{data_de}'
          AND h.DATA_HORA <= DATE '{data_ate}'
        GROUP BY
          trunc(h.DATA_HORA)
        , h.USUARIO
        , h.ATIVIDADE
        ORDER BY
          trunc(h.DATA_HORA)
        , h.USUARIO
        , h.ATIVIDADE
    """
    debug_cursor_execute(cursor, sql)

    data = dictlist_lower(cursor)
    for row in data:
        row['data'] = row['data'].date()

    return data
