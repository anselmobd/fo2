from utils.functions.models import dictlist_lower


def get_ob(cursor, os):
    sql = f"""
        SELECT 
          b.ORDEM_PRODUCAO OB
        , b.OBSERVACAO
        FROM PCPB_010 b
        WHERE b.OBSERVACAO LIKE '{os}.%'
    """
    cursor.execute(sql)
    return dictlist_lower(cursor)
