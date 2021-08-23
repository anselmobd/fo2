from pprint import pprint

from utils.functions.models import rows_to_dict_list


def historico_op(cursor, op, oc=None):
    filter_oc = ""
    if oc is not None and oc != "":
      filter_oc = f"AND h.ordem_confeccao = {oc}"

    sql = f"""
      select 
        h.*
      from systextil_logs.hist_010 h
      where 1=1
        and h.ordem_producao = '{op}'
        {filter_oc} -- filter_oc
      order by
        h.periodo_producao
      , h.ordem_confeccao
      , h.data_ocorr
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
