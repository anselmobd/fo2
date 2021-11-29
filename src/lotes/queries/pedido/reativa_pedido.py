from pprint import pprint

from django.db import DatabaseError, transaction


def exec_reativa_pedido(cursor, pedido):

    def update_pedido():
        sql = f"""
            UPDATE PEDI_100 ped -- pedido de venda
            SET 
              ped.STATUS_PEDIDO = 0 
            , ped.COD_CANCELAMENTO = 0
            , ped.DATA_CANC_VENDA = ''
            , ped.VALOR_SALDO_PEDI = ped.VALOR_LIQ_ITENS
            WHERE 1=1
              AND ped.PEDIDO_VENDA = {pedido}
              AND ped.STATUS_PEDIDO <> 0 
              AND ped.COD_CANCELAMENTO <> 0
              AND ped.DATA_CANC_VENDA IS NOT NULL
              AND ped.VALOR_SALDO_PEDI = 0
        """
        cursor.execute(sql)

    def update_itens():
        sql = f"""
            UPDATE PEDI_110 i -- item de pedido de venda
            SET 
              i.COD_CANCELAMENTO = 0
            , i.DT_CANCELAMENTO = NULL  
            WHERE 1=1
              AND i.PEDIDO_VENDA = {pedido}
              AND i.COD_CANCELAMENTO <> 0
              AND i.DT_CANCELAMENTO IS NOT NULL  
        """
        cursor.execute(sql)

    try:
        with transaction.atomic():
            update_pedido()
            update_itens()
    except DatabaseError:
        return False
    
    return True
