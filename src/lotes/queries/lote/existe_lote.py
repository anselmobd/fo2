from pprint import pprint

from utils.functions.models import rows_to_dict_list


def existe_lote(cursor, periodo, ordem_confeccao):
    sql = '''
        SELECT DISTINCT
          l.PERIODO_PRODUCAO
        , l.ORDEM_CONFECCAO
        FROM PCPC_040 l
        WHERE l.PERIODO_PRODUCAO = %s
          AND l.ORDEM_CONFECCAO = %s
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    return rows_to_dict_list(cursor)
