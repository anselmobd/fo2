from pprint import pprint

from django.conf import settings
from django.db import connection

from utils.functions.models import rows_to_dict_list


def historico(pedido):
    cursor = connection.cursor()
    esquema = "" if (
        settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'
    ) else "systextil_logs."
    sql = f"""
        select 
          h.data_ocorr
        , h.usuario
        , h.maquina_rede
        , h.long01
        from {esquema}hist_100 h
        where h.programa = 'pedi_f130'
          and h.tabela = 'PEDI_100'
          and h.num01 = {pedido}
        order by
          h.sequencia desc
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
