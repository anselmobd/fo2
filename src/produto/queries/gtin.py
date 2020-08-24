from pprint import pprint

from utils.functions.models import rows_to_dict_list


def gtin(cursor, ref=None, tam=None, cor=None, gtin=None):
    filtra_ref = ''
    if ref != '':
        filtra_ref = f'''--
          AND rtc.GRUPO_ESTRUTURA = '{ref}' '''

    filtra_tam = ''
    if tam is not None and tam != '':
        filtra_tam = f'''--
          AND rtc.SUBGRU_ESTRUTURA = '{tam}' '''

    filtra_cor = ''
    if cor is not None and cor != '':
        filtra_cor = f'''--
          AND rtc.ITEM_ESTRUTURA = '{cor}' '''

    filtra_gtin = ''
    if gtin != '':
        filtra_gtin = f'''--
          AND ( rtc.CODIGO_BARRAS IS NOT NULL
              AND rtc.CODIGO_BARRAS = '{gtin}' ) '''

    sql = f"""
        SELECT
          rtc.GRUPO_ESTRUTURA REF
        , rtc.SUBGRU_ESTRUTURA TAM
        , rtc.ITEM_ESTRUTURA COR
        , CASE WHEN rtc.CODIGO_BARRAS IS NULL
                 OR rtc.CODIGO_BARRAS LIKE ' %'
          THEN 'SEM GTIN'
          ELSE rtc.CODIGO_BARRAS
          END GTIN
        , ( SELECT
              count(*)
            FROM BASI_010 ean
            WHERE ean.CODIGO_BARRAS = rtc.CODIGO_BARRAS
          ) QTD
        FROM BASI_010 rtc -- item (ref+tam+cor)
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = rtc.SUBGRU_ESTRUTURA
        WHERE rtc.NIVEL_ESTRUTURA = 1
          {filtra_ref} -- filtra_ref
          {filtra_tam} -- filtra_tam
          {filtra_cor} -- filtra_cor
          {filtra_gtin} -- filtra_gtin
        ORDER BY
          rtc.GRUPO_ESTRUTURA
        , rtc.ITEM_ESTRUTURA
        , t.ORDEM_TAMANHO
        , rtc.SUBGRU_ESTRUTURA
    """

    cursor.execute(sql)
    return rows_to_dict_list(cursor)
