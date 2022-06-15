from pprint import pprint

from django.conf import settings
from django.db import connection

from utils.functions.models import dictlist


def historico(pedido):
    cursor = connection.cursor()
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
