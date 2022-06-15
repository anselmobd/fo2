from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor):
    sql = '''
        SELECT
          p.PERIODO_PRODUCAO PERIODO
        , p.DATA_INI_PERIODO INI
        , p.DATA_FIM_PERIODO FIM
        FROM PCPC_010 p
        WHERE p.AREA_PERIODO = 1 -- confecção
        ORDER BY
          p.PERIODO_PRODUCAO
    '''
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)
    for row in dados:
        row['ini'] = row['ini'].date()
        row['fim'] = row['fim'].date()
    return dados
