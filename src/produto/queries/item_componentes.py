from pprint import pprint

from django.core.cache import cache

from utils.cache import entkeys
from utils.functions import fo2logger, my_make_key_cache
from utils.functions.models import rows_to_dict_list


def item_comps_custo(cursor, nivel, ref, tam, cor, alt):
    data = item_comps(cursor, nivel, ref, tam, cor, alt)
    for row in data:
        row['SEQ'] = row['CSEQ']
        row['NIVEL'] = row['CNIV']
        row['REF'] = row['CREF']
        row['TAM'] = row['CTAM_B']
        row['COR'] = row['CCOR_B']
        row['ALT'] = row['CALT']
        row['CONSUMO'] = row['CCONSUMO_B']
        row['PRECO'] = row['CPRECO']
        row['DESCR'] = row['CDESCR']
    return data


def item_comps(cursor, nivel, ref, tam, cor, alt):

    # key_cache = make_key_cache(ignore=['cursor'])
    key_cache = my_make_key_cache(
        'item_comps', nivel, ref, tam, cor, alt
    )
    cached_result = cache.get(key_cache)
    if cached_result is not None:
        fo2logger.info('cached '+key_cache)
        return cached_result

    sql = f"""
        WITH filtro AS
        (
        SELECT
          '{nivel}' NIV
        , '{ref}' REF
        , '{tam}' TAM
        , '{cor}' COR
        , {alt} ALT
        FROM DUAL
        )
        , alternativa AS
        (
        SELECT DISTINCT
          e.NIVEL_ITEM NIV
        , e.GRUPO_ITEM REF
        , e.SUB_ITEM ATAM
        , e.ITEM_ITEM ACOR
        , e.ALTERNATIVA_ITEM ALT
        , e.RELACAO_BANHO RBANHO
        FROM BASI_050 e
        JOIN filtro f
          ON f.NIV = e.NIVEL_ITEM
         AND f.REF = e.GRUPO_ITEM
         AND f.ALT = e.ALTERNATIVA_ITEM
        )
        , subgrupo AS
        (
        SELECT DISTINCT
          sg.BASI030_NIVEL030 NIV
        , sg.BASI030_REFERENC REF
        , sg.TAMANHO_REF TAM
        FROM BASI_020 sg
        JOIN filtro f
          ON f.NIV = sg.BASI030_NIVEL030
         AND f.REF = sg.BASI030_REFERENC
        )
        , alt_sg AS
        (
        SELECT DISTINCT
          a.*
        , CASE WHEN a.ATAM = '000'
          THEN sg.TAM
          ELSE a.ATAM
          END TAM
        FROM alternativa a
        JOIN subgrupo sg
          ON sg.NIV = a.NIV
         AND sg.REF = a.REF
         AND ( a.ATAM = '000'
             OR sg.TAM = a.ATAM
             )
        )
        , item AS
        (
        SELECT DISTINCT
          i.NIVEL_ESTRUTURA NIV
        , i.GRUPO_ESTRUTURA REF
        , i.SUBGRU_ESTRUTURA TAM
        , i.ITEM_ESTRUTURA COR
        FROM BASI_010 i
        JOIN filtro f
          ON f.NIV = i.NIVEL_ESTRUTURA
         AND f.REF = i.GRUPO_ESTRUTURA
        )
        , alt_item AS
        (
        SELECT DISTINCT
          a.*
        , CASE WHEN a.ACOR = '000000'
          THEN i.COR
          ELSE a.ACOR
          END COR
        FROM alt_sg a
        JOIN item i
          ON i.NIV = a.NIV
         AND i.REF = a.REF
         AND i.TAM = a.TAM
         AND ( a.ACOR = '000000'
             OR i.COR = a.ACOR
             )
        )
        , alt_filtrada AS
        (
        SELECT
          a.*
        FROM alt_item a
        JOIN filtro f
          ON f.NIV = a.NIV
         AND f.REF = a.REF
         AND f.TAM = a.TAM
         AND f.COR = a.COR
        )
        , componentes AS
        (
        SELECT
          a.*
        , e.SEQUENCIA CSEQ
        , e.NIVEL_COMP CNIV
        , e.GRUPO_COMP CREF
        , e.SUB_COMP CTAM
        , e.ITEM_COMP CCOR
        , e.ALTERNATIVA_COMP CALT
        , e.CONSUMO CCONSUMO
        , e.TIPO_CALCULO TCALC
        FROM BASI_050 e
        JOIN alt_filtrada a
          ON a.NIV = e.NIVEL_ITEM
         AND a.REF = e.GRUPO_ITEM
         AND a.ATAM = e.SUB_ITEM
         AND a.ACOR = e.ITEM_ITEM
         AND a.ALT = e.ALTERNATIVA_ITEM
        )
        , comb_cor AS
        (
        SELECT
          c.*
        , CASE WHEN c.CCOR = '000000'
          THEN b.ITEM_COMP
          ELSE c.CCOR
          END CCOR_B
        FROM BASI_040 b
        RIGHT JOIN componentes c
          ON c.NIV = b.NIVEL_ITEM
         AND c.REF = b.GRUPO_ITEM
         AND ( c.CCOR = '000000'
             AND c.ATAM = b.SUB_ITEM
             AND c.COR = b.ITEM_ITEM
             )
         AND c.ALT = b.ALTERNATIVA_ITEM
         AND c.CSEQ = b.SEQUENCIA
        )
        , comb_tam AS
        (
        SELECT
          c.*
        , CASE WHEN c.CTAM = '000'
          THEN b.SUB_COMP
          ELSE c.CTAM
          END CTAM_B
        FROM BASI_040 b
        RIGHT JOIN comb_cor c
          ON c.NIV = b.NIVEL_ITEM
         AND c.REF = b.GRUPO_ITEM
         AND ( c.CTAM = '000'
             AND c.ACOR = b.ITEM_ITEM
             AND c.TAM = b.SUB_ITEM
             )
         AND c.ALT = b.ALTERNATIVA_ITEM
         AND c.CSEQ = b.SEQUENCIA
        )
        , comb_consumo AS
        (
        SELECT
          c.*
        , CASE WHEN c.CCONSUMO = 0
          THEN b.CONSUMO
          ELSE c.CCONSUMO
          END CCONSUMO_B
        FROM BASI_040 b
        RIGHT JOIN comb_tam c
          ON c.NIV = b.NIVEL_ITEM
         AND c.REF = b.GRUPO_ITEM
         AND ( c.CCONSUMO = 0
             AND c.ACOR = b.ITEM_ITEM
             AND c.TAM = b.SUB_ITEM
             )
         AND c.ALT = b.ALTERNATIVA_ITEM
         AND c.CSEQ = b.SEQUENCIA
        )
        , estrutura AS
        (
        SELECT
          c.*
        , i.PRECO_CUSTO_INFO CPRECO
        , i.NARRATIVA CDESCR
        FROM comb_consumo c
        JOIN BASI_010 i
          ON i.NIVEL_ESTRUTURA = c.CNIV
         AND i.GRUPO_ESTRUTURA = c.CREF
         AND i.SUBGRU_ESTRUTURA = c.CTAM_B
         AND i.ITEM_ESTRUTURA = c.CCOR_B
        )
        SELECT
          a.*
        FROM estrutura a
        ORDER BY
          a.NIV
        , a.REF
        , a.ATAM
        , a.TAM
        , a.ACOR
        , a.COR
        , a.ALT
        , a.CSEQ
    """
    cursor.execute(sql)
    result = rows_to_dict_list(cursor)

    cache.set(key_cache, result, timeout=entkeys._MINUTE * 5)
    fo2logger.info('calculated '+key_cache)
    return result
