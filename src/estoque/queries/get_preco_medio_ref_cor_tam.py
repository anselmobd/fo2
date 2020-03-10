from utils.functions.models import rows_to_dict_list_lower


def get_preco_medio_ref_cor_tam(cursor, ref, cor, tam):
    filtra_tam = ''
    if tam != '000':
        filtra_tam = """--
            AND rtc.SUBGRU_ESTRUTURA = '{tam}'
        """.format(tam=tam)

    sql = '''
        SELECT
          rtc.GRUPO_ESTRUTURA REF
        , rtc.SUBGRU_ESTRUTURA TAM
        , rtc.ITEM_ESTRUTURA COR
        , coalesce(rtc.PRECO_MEDIO, 0) PRECO_MEDIO
        FROM BASI_010 rtc
        WHERE 1=1
          AND rtc.NIVEL_ESTRUTURA = 1
          AND rtc.GRUPO_ESTRUTURA = '{ref}'
          {filtra_tam} -- filtra_tam
          AND rtc.ITEM_ESTRUTURA = '{cor}'
    '''.format(
        ref=ref,
        cor=cor,
        filtra_tam=filtra_tam,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
