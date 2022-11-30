from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import lms

__all__ = ['query']


def query(
    cursor,
    empresa=1,
    pedido=None,
):

    filtra_pedido = lms(f"""\
        AND op.PEDIDO_VENDA = '{pedido}'
    """) if pedido else ''

    sql = lms(f"""\
        SELECT 
          op.ORDEM_PRODUCAO OP
        -- , op.*
        FROM PCPC_020 op
        WHERE 1=1
          {filtra_pedido} -- filtra_pedido
          AND op.PEDIDO_VENDA = 33710
    """)

    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    return dados
