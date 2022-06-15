from pprint import pprint

from django.conf import settings
from django.db import connection

from o2.queries import MountQuery, OQuery

from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute


def hist_narrativa(referencia):
    MQ = MountQuery(
        fields=[
          "h.data_ocorr",
          "h.usuario",
          "h.str03 tam",
          "h.str04 cor",
          "h.str05 narrativa",
        ],
        table="systextil_logs.hist_100 h",
        where=[
            "h.tabela = 'basi_010'",
            "h.programa = 'basi_f325'",
            "h.str01 = '1'",
            f"h.str02 = '{referencia}'",
        ],
        order=[
            "h.sequencia desc",
        ],
    )
    return OQuery(MQ).debug_execute()

    sql = MountQuery(
        fields=[
          "h.data_ocorr",
          "h.usuario",
          "h.str03 tam",
          "h.str04 cor",
          "h.str05 narrativa",
        ],
        table="systextil_logs.hist_100 h",
        where=[
            "h.tabela = 'basi_010'",
            "h.programa = 'basi_f325'",
            "h.str01 = '1'",
            f"h.str02 = '{referencia}'",
        ],
        order=[
            "h.sequencia desc",
        ],
    ).query
    return OQuery(sql).debug_execute()

    return MountQuery(
        fields=[
          "h.data_ocorr",
          "h.usuario",
          "h.str03 tam",
          "h.str04 cor",
          "h.str05 narrativa",
        ],
        table="systextil_logs.hist_100 h",
        where=[
            "h.tabela = 'basi_010'",
            "h.programa = 'basi_f325'",
            "h.str01 = '1'",
            f"h.str02 = '{referencia}'",
        ],
        order=[
            "h.sequencia desc",
        ],
    ).oquery.debug_execute()

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
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
