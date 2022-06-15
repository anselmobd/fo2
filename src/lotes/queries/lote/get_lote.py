from pprint import pprint

from utils.functions.models import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from lotes.functions.varias import periodo_oc


def query(cursor, lote):
    periodo, oc = periodo_oc(lote)
    sql = f"""
        select
          l.*
        from PCPC_040 l
        where l.PERIODO_PRODUCAO = {periodo}
          and l.ORDEM_CONFECCAO = {oc}
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
