from pprint import pprint

from utils.functions.models import rows_to_dict_list
from utils.functions.queries import debug_cursor_execute


def periodos_confeccao(cursor):
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
    return rows_to_dict_list(cursor)
