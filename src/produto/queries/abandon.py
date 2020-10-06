from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def get_ref_colecao(cursor, ref):
    sql = '''
        SELECT
          r.COLECAO
        FROM BASI_030 r
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.REFERENCIA = %s
    '''
    cursor.execute(sql, [ref])
    data = rows_to_dict_list_lower(cursor)
    return data
