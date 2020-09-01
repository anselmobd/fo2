from pprint import pprint

from django.db.utils import DatabaseError

from utils.functions.models import rows_to_dict_list


def gtin(cursor, ref=None, tam=None, cor=None, gtin=None):
    filtra_ref = ''
    if ref is not None and ref != '':
        filtra_ref = f''' --
            AND rtc.GRUPO_ESTRUTURA = '{ref}'
        '''

    filtra_tam = ''
    if tam is not None and tam != '':
        filtra_tam = f''' --
            AND rtc.SUBGRU_ESTRUTURA = '{tam}'
        '''

    filtra_cor = ''
    if cor is not None and cor != '':
        filtra_cor = f''' --
            AND rtc.ITEM_ESTRUTURA = '{cor}'
        '''

    filtra_gtin = ''
    if gtin is not None and gtin != '':
        filtra_gtin = f''' --
            AND ( rtc.CODIGO_BARRAS IS NOT NULL
                AND rtc.CODIGO_BARRAS = '{gtin}' )
        '''

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


def set_gtin(cursor, niv, ref, tam, cor, gtin):

    sql_select = f"""
        SELECT
          rtc.CODIGO_BARRAS GTIN
        FROM BASI_010 rtc -- item (ref+tam+cor)
        WHERE rtc.NIVEL_ESTRUTURA = '{niv}'
          AND rtc.GRUPO_ESTRUTURA = '{ref}'
          AND rtc.SUBGRU_ESTRUTURA = '{tam}'
          AND rtc.ITEM_ESTRUTURA = '{cor}'
    """
    try:
        cursor.execute(sql_select)
        data = rows_to_dict_list(cursor)
        if len(data) != 1:
            return -1, 'Item não único'
        if data[0]['GTIN'] == gtin:
            return 1, None
    except DatabaseError as error:
        return -2, error

    sql_update = f"""
        UPDATE BASI_010 rtc -- item (ref+tam+cor)
        SET
          rtc.CODIGO_BARRAS = {gtin}
        WHERE rtc.NIVEL_ESTRUTURA = '{niv}'
          AND rtc.GRUPO_ESTRUTURA = '{ref}'
          AND rtc.SUBGRU_ESTRUTURA = '{tam}'
          AND rtc.ITEM_ESTRUTURA = '{cor}'
    """
    try:
        cursor.execute(sql_update)
    except DatabaseError as error:
        return -3, error

    try:
        cursor.execute(sql_select)
        data = rows_to_dict_list(cursor)
        if data[0]['GTIN'] != gtin:
            return -4, 'GTIN não atualizado'
    except DatabaseError as error:
        return -5, error

    return 0, None
