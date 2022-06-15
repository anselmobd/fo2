from pprint import pprint

from utils.functions.models import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor):
    sql = '''
        SELECT
          e.CODIGO_ESTAGIO EST
        , e.DESCRICAO DESCR
        , CASE WHEN e.CODIGO_DEPOSITO = 0 THEN ' '
          ELSE e.CODIGO_DEPOSITO || '-' || d.DESCRICAO
          END DEP
        , e.LEED_TIME LT
        FROM MQOP_005 e
        LEFT JOIN BASI_205 d
          ON d.CODIGO_DEPOSITO = e.CODIGO_DEPOSITO
        ORDER BY
          e.CODIGO_ESTAGIO
    '''
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
