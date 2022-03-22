from pprint import pprint

from utils.functions.models import rows_to_dict_list


def altera_pedido(cursor, pedido, empresa, observacao):
    sql = f"""
        UPDATE PEDI_100 p 
        SET 
          p.OBSERVACAO = '{observacao}'
        WHERE 1=1
          AND p.CODIGO_EMPRESA = {empresa}
          AND p.PEDIDO_VENDA = {pedido}
    """
    cursor.execute(sql)
