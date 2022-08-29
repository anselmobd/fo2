from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def referencias_com_op(cursor):
    sql = f'''
        SELECT
          op.REFERENCIA_PECA REF
        , max(op.DATA_PROGRAMACAO) DT_DIGITACAO 
        FROM PCPC_020 op
        WHERE op.COD_CANCELAMENTO = 0
        GROUP BY
          op.REFERENCIA_PECA
        ORDER BY 
          op.REFERENCIA_PECA
    '''
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
