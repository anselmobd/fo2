from pprint import pprint

from systextil.queries.produto.modelo import sql_sele_modelostr_ref, sql_modelostr_ref
from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute


def multiplas_colecoes(cursor):
    sql = f"""
        WITH problema AS
        ( SELECT
            {sql_sele_modelostr_ref('r.REFERENCIA')}
          , count( DISTINCT r.COLECAO ) colecoes
          FROM BASI_030 r -- item (ref+tam+cor)
          WHERE r.NIVEL_ESTRUTURA = 1
            AND r.REFERENCIA < 'C0000'
            AND r.DESCR_REFERENCIA NOT LIKE '-%'
          GROUP BY
            {sql_modelostr_ref('r.REFERENCIA')}
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
         AND {sql_modelostr_ref('r.REFERENCIA')} = p.modelo
        JOIN BASI_140 col
          ON col.COLECAO = r.COLECAO
        ORDER BY
          p.colecoes DESC
        , p.modelo
        , r.COLECAO
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
