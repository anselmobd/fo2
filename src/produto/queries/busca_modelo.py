from pprint import pprint

from systextil.queries.produto.modelo import sql_modeloint_ref, sql_sele_modeloint_ref
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def busca_modelo(cursor, descricao=None):
    filtro_descricao = f'''
        AND r.DESCR_REFERENCIA LIKE '%{descricao}%'
    ''' if descricao else ''

    sql = f"""
        SELECT DISTINCT
          {sql_sele_modeloint_ref('r.REFERENCIA')}
        , MAX(r.DESCR_REFERENCIA) DESCR
        FROM BASI_030 r -- ref
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.DESCR_REFERENCIA NOT LIKE '-%'
          AND r.REFERENCIA < 'C0000'
          {filtro_descricao} -- filtro_descricao
        GROUP BY
          {sql_modeloint_ref('r.REFERENCIA')}
        ORDER BY
          1
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
