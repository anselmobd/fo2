from pprint import pprint
from functools import lru_cache

from utils.functions.models import rows_to_dict_list


@lru_cache(maxsize=128)
def ref_custo(cursor, nivel, ref, tam, cor, alt):
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
    return rows_to_dict_list(cursor)
