from pprint import pprint

from django.core.cache import cache

from systextil.queries.produto.modelo import sql_modelostr_ref
from utils.functions import my_make_key_cache, fo2logger
from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute

import lotes.models


def colecoes_de_modelo(cursor, modelo):
    key_cache = my_make_key_cache(
        'colecoes_de_modelo', modelo)

    cached_result = cache.get(key_cache)
    if cached_result is not None:
        fo2logger.info('cached '+key_cache)
        return cached_result

    sql = f"""
        SELECT
          r.COLECAO
        FROM BASI_030 r -- item (ref+tam+cor)
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.REFERENCIA < 'C0000'
          AND r.DESCR_REFERENCIA NOT LIKE '-%'
          AND {sql_modelostr_ref('r.REFERENCIA')} = {modelo}
        GROUP BY
          r.COLECAO
    """
    debug_cursor_execute(cursor, sql)
    result = dictlist(cursor)

    cache.set(key_cache, result)
    fo2logger.info('calculated '+key_cache)
    return result


def colecao_de_modelo(cursor, modelo):
    rows = colecoes_de_modelo(cursor, modelo)
    if len(rows) != 1:
        return -1
    return rows[0]['COLECAO']


def lead_de_modelo(cursor, modelo):
    lead = 0
    rows = colecoes_de_modelo(cursor, modelo)
    for row in rows:
        try:
            lc = lotes.models.RegraColecao.objects.get(colecao=row['COLECAO'])
            lc_lead = lc.lead
        except lotes.models.RegraColecao.DoesNotExist:
            lc_lead = 0
            break
        if lead == 0:
            lead = lc_lead
        else:
            if lead != lc_lead:
                lead = 0
                break
    return lead
