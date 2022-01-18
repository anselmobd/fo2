from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def query_colecao(cursor):
    sql = f'''
        SELECT
          col.COLECAO
        , col.DESCR_COLECAO
        FROM BASI_140 col
        ORDER BY
          col.COLECAO
    '''
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
