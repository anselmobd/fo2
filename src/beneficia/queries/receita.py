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
