import datetime
from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def receita_inform(cursor, receita):
    sql = f"""
        WITH referencias AS
        ( SELECT
            sr.*
          FROM basi_030 sr
          WHERE sr.NIVEL_ESTRUTURA = 5
            AND sr.REFERENCIA = '{receita}'
        )
        SELECT
          r.REFERENCIA REF
        , r.DESCR_REFERENCIA DESCR
        FROM referencias r
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def receita_subgrupo(cursor, receita):
    sql = f"""
        SELECT DISTINCT
          t.TAMANHO_REF COD
        , t.DESCR_TAM_REFER DESCR
        FROM basi_020 t
        WHERE t.BASI030_NIVEL030 = 5
          AND t.BASI030_REFERENC = '{receita}'
        ORDER BY
          t.TAMANHO_REF
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
