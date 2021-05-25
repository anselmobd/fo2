from pprint import pprint

from django.core.cache import cache

from utils.functions.models import rows_to_dict_list_lower
from utils.functions import my_make_key_cache, fo2logger


def pa_de_modelo(cursor, modelo=None):

    key_cache = my_make_key_cache('pa_de_modelo', modelo)
    cached_result = cache.get(key_cache)
    if cached_result is not None:
        fo2logger.info('cached '+key_cache)
        return cached_result

    sql = f"""
        SELECT DISTINCT
          v.REFERENCIA REF
        FROM BASI_030 v -- ref
        WHERE 1=1
          AND v.NIVEL_ESTRUTURA = 1 
          AND v.REFERENCIA LIKE '%{modelo}%' 
          AND TRIM(
                LEADING '0' FROM (
                  REGEXP_REPLACE(
                    v.REFERENCIA
                  , '^([^a-zA-Z]+)[a-zA-Z]*$'
                  , '\\1'
                  )
                )
              ) = '{modelo}'
    """
    cursor.execute(sql)

    cached_result = rows_to_dict_list_lower(cursor)
    cache.set(key_cache, cached_result)
    fo2logger.info('calculated '+key_cache)
    return cached_result
