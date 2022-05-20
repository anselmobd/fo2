from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def query(cursor):
    sql = f"""
        SELECT
          1 NIVEL
        FROM DUAL
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
