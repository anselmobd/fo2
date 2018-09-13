from django.db import models

from fo2.models import rows_to_dict_list_lower


def por_deposito(cursor, nivel, ref, tam, cor):
    filtro_nivel = ''
    if nivel is not None:
        filtro_nivel = "AND e.CDITEM_NIVEL99 = {nivel}".format(nivel=nivel)

    filtro_ref = ''
    if ref != '':
        filtro_ref = "AND e.CDITEM_GRUPO = '{ref}'".format(ref=ref)

    filtro_tam = ''
    if tam != '':
        filtro_tam = "AND e.CDITEM_SUBGRUPO = '{tam}'".format(tam=tam)

    filtro_cor = ''
    if cor != '':
        filtro_cor = "AND e.CDITEM_ITEM = '{cor}'".format(cor=cor)

    sql = '''
        SELECT
          e.*
        FROM ESTQ_040 e
        WHERE 1=1
          {filtro_nivel} -- filtro_nivel
          {filtro_ref} -- filtro_ref
          {filtro_tam} -- filtro_tam
          {filtro_cor} -- filtro_cor
          -- AND e.DEPOSITO = 231
    '''.format(
        filtro_nivel=filtro_nivel,
        filtro_ref=filtro_ref,
        filtro_tam=filtro_tam,
        filtro_cor=filtro_cor,
    )
    print(sql)
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
