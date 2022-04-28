from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor, pedido):
    sql = f"""
        SELECT distinct
          i.CD_IT_PE_GRUPO REF
        FROM PEDI_110 i -- item de pedido de venda
        WHERE i.PEDIDO_VENDA = {pedido}
        ORDER BY
          i.CD_IT_PE_GRUPO
    """
    debug_cursor_execute(cursor, sql)
    return rows_to_dict_list_lower(cursor)
