from pprint import pprint

from django.db import connections

from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute


__all__ = ['historico_op']


def historico_op(op, oc=None, dia=None, usuario=None, descr=None):
    cursor = connections['systextil_log'].cursor()
    filter_oc = ""
    if oc is not None and oc != "":
        filter_oc = f"AND h.ordem_confeccao = {oc}"

    filter_dia = ""
    if dia is not None and dia != "":
        filter_dia = f"AND h.data_ocorr::DATE = '{dia}'::DATE"

    filter_usuario = ""
    if usuario is not None and usuario != "":
        filter_usuario = f"AND h.usuario_rede LIKE '%{usuario}%'"

    filter_descr = ""
    if descr is not None and descr != "":
        descr = descr.replace(' ', '%')
        filter_descr = f"AND h.descricao_historico LIKE '%{descr}%'"

    sql = f"""
      select 
        h.*
      from systextil_logs.hist_010 h
      where h.ordem_producao = '{op}'
        {filter_oc} -- filter_oc
        {filter_dia} -- filter_dia
        {filter_usuario} -- filter_usuario
        {filter_descr} -- filter_descr
      order by
        h.periodo_producao
      , h.ordem_confeccao
      , h.data_ocorr
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
