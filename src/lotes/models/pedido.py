from utils.functions.models import rows_to_dict_list


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
    return rows_to_dict_list(cursor)
