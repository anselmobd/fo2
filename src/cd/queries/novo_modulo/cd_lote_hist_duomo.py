from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(cursor, lote):
    sql = f"""
        SELECT
          ehd.COD_CONTAINER
        , ehd.ORDEM_PRODUCAO
        , ehd.ORDEM_CONFECCAO
        , ehd.DATA_INCLUSAO
        , ehd.NIVEL
        , ehd.GRUPO
        , ehd.SUB
        , ehd.ITEM
        , ehd.QUANTIDADE
        , ehd.DATA_VERSAO
        , ehd.USUARIO_SYSTEXTIL
        FROM ENDR_014_HIST_DUOMO ehd
        WHERE 1=1
          AND ehd.ORDEM_CONFECCAO = '{lote}'
        ORDER BY 
          ehd.DATA_VERSAO DESC 
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
