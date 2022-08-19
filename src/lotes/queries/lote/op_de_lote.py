from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(cursor, lote):
    periodo = lote[:4]
    oc = lote[4:]
    sql = f"""
        SELECT
          l.ORDEM_PRODUCAO OP
        FROM PCPC_040 l
        WHERE l.PERIODO_PRODUCAO = {periodo}
          AND l.ORDEM_CONFECCAO = {oc}
          AND l.SEQUENCIA_ESTAGIO = 1
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
