from pprint import pprint

from django.db import connections

from utils.functions.models.dictlist import dictlist


def historico(pedido):
    cursor = connections['systextil_log'].cursor()
    sql = f"""
        select 
          h.data_ocorr
        , h.usuario
        , h.maquina_rede
        , h.long01 descricao
        from systextil_logs.hist_100 h
        where h.programa = 'pedi_f130'
          -- and h.tabela = 'PEDI_100'
          and h.num01 = {pedido}
        order by
          h.sequencia desc
    """
    cursor.execute(sql)
    return dictlist(cursor)
