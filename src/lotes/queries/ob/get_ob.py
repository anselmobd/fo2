from utils.functions.models import rows_to_dict_list_lower


def get_ob(cursor, os):
    sql = f"""
        SELECT 
          b.ORDEM_PRODUCAO OB
        , b.OBSERVACAO
        FROM PCPB_010 b
        WHERE b.OBSERVACAO LIKE '{os}.%'
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
