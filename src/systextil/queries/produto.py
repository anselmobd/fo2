from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def item(cursor, nivel, ref, tam, cor):
    sql = f"""
        SELECT DISTINCT
          r.NIVEL_ESTRUTURA NIVEL
        , r.REFERENCIA REF
        , r.DESCR_REFERENCIA DESCR
        , t.TAMANHO_REF TAM
        , t.DESCR_TAM_REFER DESCR_TAM
        , ot.ORDEM_TAMANHO ORDEM_TAM
        , c.ITEM_ESTRUTURA COR
        , c.DESCRICAO_15 DESCR_COR
        FROM BASI_030 r -- referencia
        JOIN BASI_020 t -- tamanho
          ON t.BASI030_NIVEL030 = r.NIVEL_ESTRUTURA
         AND t.BASI030_REFERENC = r.REFERENCIA
        LEFT JOIN BASI_220 ot -- cadastro de tamanhos e ordens
          ON ot.TAMANHO_REF = t.TAMANHO_REF
        JOIN BASI_010 c -- cor
          ON c.NIVEL_ESTRUTURA = r.NIVEL_ESTRUTURA
         AND c.GRUPO_ESTRUTURA = r.REFERENCIA
         AND c.SUBGRU_ESTRUTURA = t.TAMANHO_REF
        WHERE 1=1
          AND r.NIVEL_ESTRUTURA = {nivel}
          AND r.REFERENCIA = '{ref}'
          AND t.TAMANHO_REF = '{tam}'
          AND c.ITEM_ESTRUTURA = '{cor}'
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
