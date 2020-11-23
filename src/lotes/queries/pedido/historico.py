from pprint import pprint

from django.db import connection

from fo2.settings import DEBUG, DATABASES

from utils.functions.models import rows_to_dict_list
from utils.functions import fo2logger


def historico(pedido):
    cursor = connection.cursor()
    esquema = "" if (
        DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'
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
          h.sequencia
    """
    cursor.execute(sql)
    fo2logger.info(sql)
    data = rows_to_dict_list(cursor)
    fo2logger.info(data)
    return data
