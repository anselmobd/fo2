from pprint import pprint

from django.conf import settings
from django.db import connection

from utils.functions.models import rows_to_dict_list


def hist_narrativa(referencia):
    cursor = connection.cursor()
    sql = f"""
      select 
        h.data_ocorr
      , h.usuario
      , h.str03 tam
      , h.str04 cor
      , h.str05 narrativa
      from systextil_logs.hist_100 h
      where 1=1
        and h.tabela = 'basi_010'
        and h.programa = 'basi_f325'
        and h.str01 = '1'
        and h.str02 = '{referencia}'
      order by
        h.sequencia desc
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
