from pprint import pprint

from django.core.cache import cache

from utils.cache import timeout
from utils.functions import (
    fo2logger,
    my_make_key_cache,
)
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from lotes.functions.varias import modelo_de_ref

__all__ = ['to_set', 'query']


def to_set(cursor, modelo, com_op=None, com_ped=None):
    data = query(cursor, modelo, com_op, com_ped)
    return set([
        row['ref']
        for row in data
    ])

def query(cursor, modelo, com_op=False, com_ped=False):

    key_cache = my_make_key_cache(
        'cd/queries/novo_modulo/refs_de_modelo/query',
        modelo, com_op, com_ped,
    )

    refs = cache.get(key_cache)

    if refs is not None:
        fo2logger.info('cached '+key_cache)
        return refs

    if isinstance(modelo, str):
        modelo = int(modelo)
    filtra_com_op = f"""--
        AND EXISTS (
          SELECT 
            1
          FROM pcpc_020 op 
          WHERE op.REFERENCIA_PECA = r.REFERENCIA 
            AND op.COD_CANCELAMENTO = 0
        )
    """ if com_op else ''
    filtra_com_ped = f"""--
        AND EXISTS (
          SELECT 
            1
          FROM PEDI_110 iped -- item de pedido de venda
          JOIN PEDI_100 cped -- capa de pedido de venda
            ON iped.PEDIDO_VENDA = cped.PEDIDO_VENDA
          WHERE iped.CD_IT_PE_GRUPO = r.REFERENCIA 
            AND iped.CD_IT_PE_NIVEL99 = 1
            AND cped.CODIGO_EMPRESA = 1
            AND cped.COD_CANCELAMENTO = 0
        )
    """ if com_ped else ''
    sql = f"""
        SELECT 
          r.REFERENCIA REF
        FROM BASI_030 r
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.REFERENCIA LIKE '%{modelo}%'
          AND r.DESCR_REFERENCIA NOT LIKE '-%'
          {filtra_com_op} -- filtra_com_op
          {filtra_com_ped} -- filtra_com_ped
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)
    refs = [
        row
        for row in dados        
        if modelo_de_ref(row['ref']) == modelo
    ]

    cache.set(key_cache, refs, timeout=timeout.MINUTE)
    fo2logger.info('calculated '+key_cache)

    return refs
