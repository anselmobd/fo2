from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from lotes.functions.varias import modelo_de_ref


def lotes_de_referencia(cursor):
    sql = f'''
        SELECT
          l.PROCONF_GRUPO REF
        , count(*) lotes
        FROM PCPC_040 l
        WHERE l.SITUACAO_ORDEM <> 9
          AND l.CODIGO_ESTAGIO = 63
          AND l.QTDE_PECAS_PROG <> 0
        GROUP BY
          l.PROCONF_GRUPO
        ORDER BY
          l.PROCONF_GRUPO
    '''
    debug_cursor_execute(cursor, sql)
    data = dictlist_lower(cursor)
    for row in data:
        row['modelo'] = modelo_de_ref(row['ref'])
    return data
