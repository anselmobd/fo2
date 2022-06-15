from utils.functions.models import dictlist


def ped_dep_qtd(cursor, pedido):
    # quantidade por depósito
    sql = """
        SELECT
          i.CODIGO_DEPOSITO DEPOSITO
        , sum(i.QTDE_PEDIDA) QTD
        FROM PEDI_110 i
        WHERE i.PEDIDO_VENDA = %s
        GROUP BY
          i.CODIGO_DEPOSITO
        ORDER BY
          i.CODIGO_DEPOSITO
    """
    cursor.execute(sql, [pedido])
    return dictlist(cursor)
