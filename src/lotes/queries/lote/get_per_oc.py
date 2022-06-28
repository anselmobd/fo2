from pprint import pprint

from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(cursor, op):
    sql = f"""
        SELECT DISTINCT 
          l.PERIODO_PRODUCAO PERIODO
        , l.ORDEM_CONFECCAO OC
        FROM PCPC_040 l
        WHERE l.ORDEM_PRODUCAO = {op}
        ORDER BY 
          l.PERIODO_PRODUCAO
        , l.ORDEM_CONFECCAO
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
