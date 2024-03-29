from pprint import pprint
from typing import Iterable

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def get_agrupador(cursor, pedido):
    sql = f"""
        SELECT DISTINCT
          iped.AGRUPADOR_PRODUCAO + 999000000 AGRUPADOR
        FROM  PEDI_110 iped -- item de pedido de venda
        WHERE iped.PEDIDO_VENDA = {pedido}
          AND iped.AGRUPADOR_PRODUCAO <> 0
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
