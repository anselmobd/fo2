from pprint import pprint

from django.db import DatabaseError, transaction


def exec_cancela_pedido(cursor, pedido):

    def update_pedido():
        sql = f"""
            UPDATE PEDI_100 ped -- pedido de venda
            SET
              ped.STATUS_PEDIDO = 5 -- cancelada
            , ped.COD_CANCELAMENTO = 19 -- PED ANTIGO Ñ FATURAD
            , ped.DATA_CANC_VENDA = CURRENT_DATE
            , ped.VALOR_SALDO_PEDI = 0
            WHERE 1=1
              AND ped.PEDIDO_VENDA = {pedido}
              AND ped.STATUS_PEDIDO <> 5
              AND ped.COD_CANCELAMENTO = 0
              AND ped.DATA_CANC_VENDA IS NULL
              AND ped.VALOR_SALDO_PEDI <> 0
        """
        cursor.execute(sql)

    def update_itens():
        sql = f"""
            UPDATE PEDI_110 i -- item de pedido de venda
            SET
              i.COD_CANCELAMENTO = 19 -- PED ANTIGO Ñ FATURAD
            , i.DT_CANCELAMENTO = CURRENT_DATE
            WHERE 1=1
              AND i.PEDIDO_VENDA = {pedido}
              AND i.COD_CANCELAMENTO = 0
              AND i.DT_CANCELAMENTO IS NULL
        """
        cursor.execute(sql)

    try:
        with transaction.atomic():
            update_pedido()
            update_itens()
    except DatabaseError:
        return False

    return True
