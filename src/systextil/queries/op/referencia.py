from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def referencias_com_op(cursor):
    sql = f'''
        SELECT distinct
          op.REFERENCIA_PECA ref
        FROM PCPC_020 op
        WHERE op.COD_CANCELAMENTO = 0
        ORDER BY 
          op.REFERENCIA_PECA
    '''
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
