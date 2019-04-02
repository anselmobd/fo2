from django.db import models

from fo2.models import rows_to_dict_list_lower


def por_deposito(cursor, nivel, ref, tam, cor, deposito='999'):
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

    filtro_deposito = ''
    if deposito != '999':
        filtro_deposito = "AND e.DEPOSITO = '{deposito}'".format(
            deposito=deposito)

    sql = '''
        SELECT
          e.cditem_nivel99
        , e.cditem_grupo
        , e.cditem_subgrupo
        , e.cditem_item
        , e.deposito
        , e.deposito || ' - ' || d.DESCRICAO DEP_DESCR
        , e.qtde_estoque_atu
        FROM ESTQ_040 e
        LEFT JOIN BASI_205 d
          ON d.CODIGO_DEPOSITO = e.DEPOSITO
        WHERE 1=1
          {filtro_nivel} -- filtro_nivel
          {filtro_ref} -- filtro_ref
          {filtro_tam} -- filtro_tam
          {filtro_cor} -- filtro_cor
          {filtro_deposito} -- filtro_deposito
        ORDER BY
          e.CDITEM_NIVEL99
        , e.CDITEM_GRUPO
        , e.CDITEM_SUBGRUPO
        , e.CDITEM_ITEM
        , e.DEPOSITO
    '''.format(
        filtro_nivel=filtro_nivel,
        filtro_ref=filtro_ref,
        filtro_tam=filtro_tam,
        filtro_cor=filtro_cor,
        filtro_deposito=filtro_deposito,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
