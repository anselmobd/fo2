from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from lotes.functions.varias import modelo_de_ref


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
    data = dictlist_lower(cursor)
    for row in data:
        row['modelo'] = modelo_de_ref(row['ref'])
    return data
