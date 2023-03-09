from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


__all__ = ['get_estoque_dep_niv_ref_cor_tam', 'get_estoque_dep_ref_cor_tam']


def get_estoque_dep_niv_ref_cor_tam(cursor, deposito, niv, ref, cor, tam):
    sql = f'''
        SELECT
          e.QTDE_ESTOQUE_ATU ESTOQUE
        FROM ESTQ_040 e
        WHERE 1=1
          AND e.CDITEM_NIVEL99 = {niv}
          AND e.CDITEM_GRUPO = '{ref}'
          AND e.CDITEM_SUBGRUPO = '{tam}'
          AND e.CDITEM_ITEM = '{cor}'
          AND e.DEPOSITO = {deposito}
    '''
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)


def get_estoque_dep_ref_cor_tam(cursor, deposito, ref, cor, tam):
    return get_estoque_dep_niv_ref_cor_tam(cursor, deposito, 1, ref, cor, tam)
