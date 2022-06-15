from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def refs_com_movimento(cursor, data_ini=None):
    filtro_data_ini = ''
    if data_ini is not None:
        filtro_data_ini = (
            "AND ee.DATA_MOVIMENTO >= "
            f"DATE '{data_ini}'"
        )

    sql = f'''
        SELECT DISTINCT
          ee.GRUPO_ESTRUTURA REF
        FROM ESTQ_300_ESTQ_310 ee
        WHERE ee.NIVEL_ESTRUTURA = 1
          AND ee.GRUPO_ESTRUTURA < 'C0000'
          AND ee.CODIGO_DEPOSITO IN (231, 101, 102)
          {filtro_data_ini} -- filtro_data_ini
        ORDER BY
          ee.GRUPO_ESTRUTURA
    '''
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
