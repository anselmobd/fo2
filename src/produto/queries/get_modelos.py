from pprint import pprint

from systextil.queries.produto.modelo import sql_sele_modeloint_ref
from utils.functions.queries import debug_cursor_execute


__all__ = ['list_modelos_query']


def list_modelos_query(cursor):
    sql = f"""
        SELECT DISTINCT
          {sql_sele_modeloint_ref('r.REFERENCIA')}
        FROM BASI_030 r -- ref
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.DESCR_REFERENCIA NOT LIKE '-%'
          AND r.REFERENCIA < 'C0000'
        ORDER BY
          1
    """
    debug_cursor_execute(cursor, sql)
    return [row[0] for row in cursor]
