from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower


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
    return dictlist_lower(cursor)
