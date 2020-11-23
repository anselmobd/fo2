from pprint import pprint

from utils.functions.models import rows_to_dict_list


def ped_inform(cursor, pedido):
    sql = """
        select 
          *
        from systextil_logs.hist_100 h
        where h.programa = 'pedi_f130'
          and h.num01 = %s
        order by
          h.sequencia
    """
    cursor.execute(sql, [pedido])
    return rows_to_dict_list(cursor)
