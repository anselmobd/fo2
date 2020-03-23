from utils.functions.models import rows_to_dict_list_lower


def get_preco_medio_niv_ref_cor_tam(cursor, niv, ref, cor, tam):
    filtra_tam = ''
    if tam != '000':
        filtra_tam = f"""--
            AND rtc.SUBGRU_ESTRUTURA = '{tam}'
        """

    sql = f'''
        SELECT
          rtc.GRUPO_ESTRUTURA REF
        , rtc.SUBGRU_ESTRUTURA TAM
        , rtc.ITEM_ESTRUTURA COR
        , coalesce(rtc.PRECO_MEDIO, 0) PRECO_MEDIO
        FROM BASI_010 rtc
        WHERE 1=1
          AND rtc.NIVEL_ESTRUTURA = {niv}
          AND rtc.GRUPO_ESTRUTURA = '{ref}'
          {filtra_tam} -- filtra_tam
          AND rtc.ITEM_ESTRUTURA = '{cor}'
    '''
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def get_preco_medio_ref_cor_tam(cursor, ref, cor, tam):
    return get_preco_medio_niv_ref_cor_tam(cursor, 1, ref, cor, tam)
