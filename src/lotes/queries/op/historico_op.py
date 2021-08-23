from pprint import pprint

from utils.functions.models import rows_to_dict_list


def historico_op(cursor, op, oc=None, usuario=None):
    filter_oc = ""
    if oc is not None and oc != "":
      filter_oc = f"AND h.ordem_confeccao = {oc}"

    filter_usuario = ""
    if usuario is not None and usuario != "":
      filter_usuario = f"AND h.usuario_sistema LIKE '%{usuario}%'"

    sql = f"""
      select 
        h.*
      from systextil_logs.hist_010 h
      where h.ordem_producao = '{op}'
        {filter_oc} -- filter_oc
        {filter_usuario} -- filter_usuario
      order by
        h.periodo_producao
      , h.ordem_confeccao
      , h.data_ocorr
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
