from pprint import pprint

from utils.functions.models import rows_to_dict_list


def historico_op(cursor, op):
    sql = f"""
      select 
        h.*
      from systextil_logs.hist_010 h
      where 1=1
        and h.ordem_producao = '{op}'
      order by
        h.data_ocorr desc
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
