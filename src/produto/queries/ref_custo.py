from pprint import pprint

from django.core.cache import cache

from utils.cache import entkeys
from utils.functions import my_make_key_cache, fo2logger
from utils.functions.models import rows_to_dict_list


def ref_custo(cursor, nivel, ref, tam, cor, alt):

    # key_cache = make_key_cache()
    key_cache = my_make_key_cache(
        'ref_custo', nivel, ref, tam, cor, alt)
    cached_result = cache.get(key_cache)
    if cached_result is not None:
        fo2logger.info('cached '+key_cache)
        return cached_result

    filtra_nivel = ''
    if nivel != '':
        filtra_nivel = f'''--
          AND i.NIVEL_ESTRUTURA = '{nivel}' '''

    filtra_ref = ''
    if ref != '':
        filtra_ref = f'''--
          AND i.GRUPO_ESTRUTURA = '{ref}' '''

    filtra_tam = ''
    if tam != '':
        filtra_tam = f'''--
          AND i.SUBGRU_ESTRUTURA = '{tam}' '''

    filtra_cor = ''
    if cor != '':
        filtra_cor = f'''--
          AND i.ITEM_ESTRUTURA = '{cor}' '''

    filtra_alt = ''
    if alt != '':
        filtra_alt = f'''--
          AND e.ALTERNATIVA_ITEM = '{alt}' '''

    sql = f"""
        SELECT
          e.SEQUENCIA SEQ
        , e.NIVEL_COMP NIVEL
        , e.GRUPO_COMP REF
        , CASE WHEN e.SUB_COMP = '000'
          THEN cot.SUB_COMP
          ELSE e.SUB_COMP
          END TAM
        , CASE WHEN e.ITEM_COMP = '000000'
          THEN coc.ITEM_COMP
          ELSE e.ITEM_COMP
          END COR
        , icomp.NARRATIVA DESCR
        , e.ALTERNATIVA_COMP ALT
        , e.CONSUMO
        , icomp.PRECO_CUSTO_INFO PRECO
        , e.CONSUMO * icomp.PRECO_CUSTO_INFO CUSTO
        FROM BASI_010 i
        JOIN BASI_050 e
          ON e.NIVEL_ITEM = i.NIVEL_ESTRUTURA
         AND e.GRUPO_ITEM = i.GRUPO_ESTRUTURA
        LEFT JOIN BASI_040 coc -- combinação cor
          ON e.ITEM_COMP = '000000'
         AND coc.NIVEL_ITEM = e.NIVEL_ITEM
         AND coc.GRUPO_ITEM = e.GRUPO_ITEM
         AND coc.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
         AND coc.SEQUENCIA = e.SEQUENCIA
         AND coc.SUB_ITEM = '000'
         AND coc.ITEM_ITEM = i.ITEM_ESTRUTURA
        LEFT JOIN BASI_040 cot -- combinação tamanho
          ON e.SUB_COMP = '000'
         AND cot.NIVEL_ITEM = e.NIVEL_ITEM
         AND cot.GRUPO_ITEM = e.GRUPO_ITEM
         AND cot.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
         AND cot.SEQUENCIA = e.SEQUENCIA
         AND cot.ITEM_ITEM = '000000'
         AND cot.SUB_ITEM = i.SUBGRU_ESTRUTURA
        JOIN BASI_010 icomp
          ON icomp.NIVEL_ESTRUTURA = e.NIVEL_COMP
         AND icomp.GRUPO_ESTRUTURA = e.GRUPO_COMP
         AND icomp.SUBGRU_ESTRUTURA =
              CASE WHEN e.SUB_COMP = '000'
              THEN cot.SUB_COMP
              ELSE e.SUB_COMP
              END
         AND icomp.ITEM_ESTRUTURA =
              CASE WHEN e.ITEM_COMP = '000000'
              THEN coc.ITEM_COMP
              ELSE e.ITEM_COMP
              END
        WHERE 1 = 1
          {filtra_nivel} -- filtra_nivel
          {filtra_ref} -- filtra_ref
          {filtra_tam} -- filtra_tam
          {filtra_cor} -- filtra_cor
          {filtra_alt} -- filtra_alt
        ORDER BY
          e.SEQUENCIA
    """
    cursor.execute(sql)
    result = rows_to_dict_list(cursor)

    cache.set(key_cache, result, timeout=entkeys._MINUTE * 5)
    fo2logger.info('calculated '+key_cache)
    return result
