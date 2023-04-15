from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from lotes.functions.varias import modelo_de_ref


def referencias_com_op(cursor):
    ano_table_op = {
        2023: 'PCPC_020',
        2020: 'PCPC_020_ANO_2020',
        2019: 'PCPC_020_ANO_2019',
        2018: 'PCPC_020_ANO_2018',
        2017: 'PCPC_020_ANO_2017',
    }

    def table_op(ano):
        return f'''
            SELECT
              op.REFERENCIA_PECA REF
            , max(op.DATA_PROGRAMACAO) DT_DIGITACAO
            , {ano} ANO
            FROM {ano_table_op[ano]} op
            WHERE op.COD_CANCELAMENTO = 0
            GROUP BY
              op.REFERENCIA_PECA
        '''

    sql = '''
        --
        UNION 
        --
    '''.join([
       table_op(2023),
       table_op(2020),
       table_op(2019),
       table_op(2018),
       table_op(2017),
    ])
    sql += '''
        --
        ORDER BY 
          1
    '''
    debug_cursor_execute(cursor, sql)
    data = dictlist_lower(cursor)
    for row in data:
        row['modelo'] = modelo_de_ref(row['ref'])
    return data
