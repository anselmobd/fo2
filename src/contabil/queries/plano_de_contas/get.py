from pprint import pprint

from utils.functions.models import dictlist_lower


def por_reduzida(cursor, plano, reduzida):
    sql = f"""
        SELECT 
          pc.*
        FROM CONT_535 pc
        WHERE pc.COD_PLANO_CTA = {plano}
          AND pc.COD_REDUZIDO = {reduzida}
    """
    cursor.execute(sql)
    return dictlist_lower(cursor)
