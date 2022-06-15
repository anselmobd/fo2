from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def get_ref_colecao(cursor, ref):
    sql = '''
        SELECT
          r.COLECAO
        FROM BASI_030 r
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.REFERENCIA = %s
    '''
    debug_cursor_execute(cursor, sql, [ref])
    data = dictlist_lower(cursor)
    return data
