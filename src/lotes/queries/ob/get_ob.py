from utils.functions.models import rows_to_dict_list_lower


def get_ob(cursor, os, caixa_inicial_val, caixa_final_val):
    sql = f"""
        SELECT 
          b.*
        FROM PCPB_010 b
        WHERE b.OBSERVACAO LIKE '{os}.%'
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
