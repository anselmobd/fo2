from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import lms

__all__ = ['pedido_query']


def pedido_query(
    cursor,
    empresa=1,
    pedido=None,
):

    filtra_pedido = lms(f"""\
        AND ped.PEDIDO_VENDA = '{pedido}'
    """) if pedido else ''

    sql = lms(f"""\
        SELECT
          ped.PEDIDO_VENDA PEDIDO
        , ped.DATA_EMIS_VENDA DT_EMISSAO
        , ped.OBSERVACAO OBS
        FROM PEDI_100 ped -- pedido de venda
        WHERE 1=1
          AND ped.CODIGO_EMPRESA = {empresa}
          {filtra_pedido} -- filtra_pedido
        ORDER BY
          ped.PEDIDO_VENDA
    """)

    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    return dados
