from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(cursor, lote):
    sql = f"""
        SELECT
          h.USUARIO
        , h.DATA_HORA
        , h.ATIVIDADE
        , h.COD_CONTAINER
        , h.ENDERECO
        , h.ORDEM_PRODUCAO
        , h.ORDEM_CONFECCAO
        FROM ENDR_016_HIST h
        WHERE h.ORDEM_CONFECCAO = {lote}
        ORDER BY 
          h.DATA_HORA DESC 
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
