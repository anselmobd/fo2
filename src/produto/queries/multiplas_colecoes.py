from pprint import pprint

from utils.functions.models import rows_to_dict_list
from utils.functions.queries import debug_cursor_execute


def multiplas_colecoes(cursor):
    sql = """
        WITH problema AS
        ( SELECT
            TRIM(LEADING '0' FROM (
              REGEXP_REPLACE(r.REFERENCIA, '[^0-9]', ''))) MODELO
          , count( DISTINCT r.COLECAO ) colecoes
          FROM BASI_030 r -- item (ref+tam+cor)
          WHERE r.NIVEL_ESTRUTURA = 1
            AND r.REFERENCIA < 'C0000'
            AND r.DESCR_REFERENCIA NOT LIKE '-%'
          GROUP BY
            TRIM(LEADING '0' FROM (
              REGEXP_REPLACE(r.REFERENCIA, '[^0-9]', '')))
          HAVING
            count( DISTINCT r.COLECAO ) > 1
        )
        SELECT
          p.modelo
        , p.colecoes
        , r.COLECAO
        , col.DESCR_COLECAO
        , r.REFERENCIA REF
        , r.DESCR_REFERENCIA DESCR
        FROM problema p
        JOIN BASI_030 r
          ON r.NIVEL_ESTRUTURA = 1
         AND r.REFERENCIA < 'C0000'
         AND r.DESCR_REFERENCIA NOT LIKE '-%'
         AND TRIM(LEADING '0' FROM (
               REGEXP_REPLACE(r.REFERENCIA, '[^0-9]', '')))
             = p.modelo
        JOIN BASI_140 col
          ON col.COLECAO = r.COLECAO
        ORDER BY
          p.colecoes DESC
        , p.modelo
        , r.COLECAO
    """
    debug_cursor_execute(cursor, sql)
    return rows_to_dict_list(cursor)
