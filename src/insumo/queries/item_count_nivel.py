from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(cursor, ref, nivel=None):
    filtra_nivel = f"AND r.NIVEL_ESTRUTURA = {nivel}" if nivel else ''
    sql = f"""
        SELECT
          count(*) COUNT
        , min(r.NIVEL_ESTRUTURA) NIVEL
        FROM basi_030 r
        WHERE r.REFERENCIA = '{ref}'
          {filtra_nivel} -- filtra_nivel
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
