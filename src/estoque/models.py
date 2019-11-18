from django.db import models

from fo2.models import rows_to_dict_list_lower, GradeQtd


def posicao_estoque(
        cursor, nivel, ref, tam, cor, deposito='999', zerados=True, group='',
        tipo='t', modelo=None):
    filtro_nivel = ''
    if nivel is not None:
        filtro_nivel = "AND e.CDITEM_NIVEL99 = {nivel}".format(nivel=nivel)

    filtro_ref = ''
    if ref != '':
        filtro_ref = "AND e.CDITEM_GRUPO = '{ref}'".format(ref=ref)

    filtro_modelo = ''
    if modelo is not None:
        filtro_modelo = """--
            AND TRIM( LEADING '0' FROM
                  REGEXP_REPLACE(
                    e.CDITEM_GRUPO,
                    '^[a-zA-Z]?([0123456789]+)[a-zA-Z]*$',
                    '\\1'
                  )
                ) = '{}'
        """.format(modelo)

    filtro_tam = ''
    if tam != '':
        filtro_tam = "AND e.CDITEM_SUBGRUPO = '{tam}'".format(tam=tam)

    filtro_cor = ''
    if cor != '':
        filtro_cor = "AND e.CDITEM_ITEM = '{cor}'".format(cor=cor)

    if deposito == '999':
        filtro_deposito = ''
    elif deposito == '1001':
        filtro_deposito = "AND e.DEPOSITO IN (231, 101, 102)"
    else:
        filtro_deposito = "AND e.DEPOSITO = '{deposito}'".format(
            deposito=deposito)

    filtro_zerados = ''
    if not zerados:
        filtro_zerados = "AND e.qtde_estoque_atu != 0"

    if group == '':
        select_fields = '''--
            , e.cditem_grupo
            , e.cditem_subgrupo
            , e.cditem_item
            , e.deposito
            , e.deposito || ' - ' || d.DESCRICAO DEP_DESCR'''
        field_quantidade = ', e.qtde_estoque_atu qtd'
        group_fields = ''
        order_by = '''--
            , e.cditem_grupo
            , e.cditem_subgrupo
            , e.cditem_item
            , e.deposito'''
    elif group == 'r':
        select_fields = '''--
            , e.cditem_grupo
            , e.deposito
            , e.deposito || ' - ' || d.DESCRICAO DEP_DESCR'''
        field_quantidade = '''--
            , sum(case when e.qtde_estoque_atu > 0
                  then e.qtde_estoque_atu else 0 end) qtd_positiva
            , sum(case when e.qtde_estoque_atu < 0
                  then e.qtde_estoque_atu else 0 end) qtd_negativa'''
        group_fields = '''--
            GROUP BY
              e.cditem_nivel99
            , e.cditem_grupo
            , e.deposito
            , d.DESCRICAO'''
        order_by = '''--
            , e.cditem_grupo
            , e.deposito'''
    elif group == 'tc':
        select_fields = '''--
            , e.cditem_subgrupo
            , e.cditem_item'''
        field_quantidade = '''--
            , sum(case when e.qtde_estoque_atu > 0
                  then e.qtde_estoque_atu else 0 end) qtd_positiva
            , sum(case when e.qtde_estoque_atu < 0
                  then e.qtde_estoque_atu else 0 end) qtd_negativa'''
        group_fields = '''--
            GROUP BY
              e.cditem_nivel99
            , e.cditem_subgrupo
            , e.cditem_item'''
        order_by = '''--
            , e.cditem_subgrupo
            , e.cditem_item'''

    filtro_tipo = ''
    if tipo == 'a':
        filtro_tipo = "AND e.cditem_grupo < 'A0000'"
    elif tipo == 'g':
        filtro_tipo = "AND e.cditem_grupo like 'A%'"
    elif tipo == 'b':
        filtro_tipo = "AND e.cditem_grupo like 'B%'"
    elif tipo == 'p':
        filtro_tipo = \
            "AND (e.cditem_grupo like 'A%' OR e.cditem_grupo like 'B%')"
    elif tipo == 'v':
        filtro_tipo = "AND e.cditem_grupo < 'C0000'"
    elif tipo == 'm':
        filtro_tipo = "AND e.cditem_grupo >= 'C0000'"

    sql = '''
        SELECT
          e.cditem_nivel99
        {select_fields} -- select_fields
        {field_quantidade} -- field_quantidade
        FROM ESTQ_040 e
        LEFT JOIN BASI_205 d
          ON d.CODIGO_DEPOSITO = e.DEPOSITO
        WHERE 1=1
          {filtro_nivel} -- filtro_nivel
          {filtro_ref} -- filtro_ref
          {filtro_modelo} -- filtro_modelo
          {filtro_tam} -- filtro_tam
          {filtro_cor} -- filtro_cor
          {filtro_deposito} -- filtro_deposito
          {filtro_zerados} -- filtro_zerados
          {filtro_tipo} -- filtro_tipo
        {group_fields} -- group_fields
        ORDER BY
          e.CDITEM_NIVEL99
        {order_by} -- order_by
    '''.format(
        select_fields=select_fields,
        field_quantidade=field_quantidade,
        filtro_nivel=filtro_nivel,
        filtro_ref=filtro_ref,
        filtro_modelo=filtro_modelo,
        filtro_tam=filtro_tam,
        filtro_cor=filtro_cor,
        filtro_deposito=filtro_deposito,
        filtro_zerados=filtro_zerados,
        filtro_tipo=filtro_tipo,
        group_fields=group_fields,
        order_by=order_by,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def valor(
        cursor, nivel, positivos, zerados, negativos, preco_zerado,
        deposito_compras):
    filtro_nivel = ''
    if nivel is not None:
        filtro_nivel = "AND e.CDITEM_NIVEL99 = {nivel}".format(nivel=nivel)

    filtro_positivos = ''
    if positivos == 's':
        filtro_positivos = "OR e.qtde_estoque_atu > 0"

    filtro_zerados = ''
    if zerados == 's':
        filtro_zerados = "OR e.qtde_estoque_atu = 0"

    filtro_negativos = ''
    if negativos == 's':
        filtro_negativos = "OR e.qtde_estoque_atu < 0"

    filtro_preco_zerado = ''
    if preco_zerado == 'n':
        filtro_preco_zerado = "AND rtc.PRECO_CUSTO_INFO != 0"

    filtro_deposito_compras = ''
    if deposito_compras == 'a':
        filtro_deposito_compras = """
            AND 1 = (
              CASE WHEN r.NIVEL_ESTRUTURA = 2 THEN
             CASE WHEN e.DEPOSITO = 202 THEN 1
             ELSE 0 END
              WHEN r.NIVEL_ESTRUTURA = 9 THEN
             CASE WHEN r.CONTA_ESTOQUE = 22 THEN
               CASE WHEN e.DEPOSITO = 212 THEN 1
               ELSE 0 END
             ELSE
               CASE WHEN e.DEPOSITO = 231 THEN 1
               ELSE 0 END
             END
              ELSE -- i.NIVEL_ESTRUTURA = 1
             CASE WHEN e.DEPOSITO in (101, 102) THEN 1
             ELSE 0 END
              END
            )
        """

    sql = '''
        SELECT
          e.cditem_nivel99 NIVEL
        , e.cditem_grupo REF
        , e.cditem_subgrupo TAM
        , e.cditem_item COR
        , r.CONTA_ESTOQUE || ' - ' || ce.DESCR_CT_ESTOQUE CONTA_ESTOQUE
        , e.deposito || ' - ' || d.DESCRICAO DEPOSITO
        , e.qtde_estoque_atu QTD
        , rtc.PRECO_CUSTO_INFO PRECO
        , e.qtde_estoque_atu * rtc.PRECO_CUSTO_INFO TOTAL
        FROM ESTQ_040 e
        JOIN BASI_030 r
          ON r.NIVEL_ESTRUTURA = e.cditem_nivel99
         AND r.REFERENCIA = e.cditem_grupo
        JOIN BASI_150 ce
          ON ce.CONTA_ESTOQUE = r.CONTA_ESTOQUE
        JOIN BASI_010 rtc
          ON rtc.NIVEL_ESTRUTURA = e.cditem_nivel99
         AND rtc.GRUPO_ESTRUTURA = e.cditem_grupo
         AND rtc.SUBGRU_ESTRUTURA = e.cditem_subgrupo
         AND rtc.ITEM_ESTRUTURA = e.cditem_item
        LEFT JOIN BASI_205 d
          ON d.CODIGO_DEPOSITO = e.DEPOSITO
        WHERE 1=1
          {filtro_nivel} -- filtro_nivel
          AND (1=2
            {filtro_positivos} -- filtro_positivos
            {filtro_zerados} -- filtro_zerados
            {filtro_negativos} -- filtro_negativos
          )
          {filtro_preco_zerado} -- filtro_preco_zerado
          {filtro_deposito_compras} -- filtro_deposito_compras
        ORDER BY
          e.CDITEM_NIVEL99
        , e.cditem_grupo
        , e.cditem_subgrupo
        , e.cditem_item
        , e.DEPOSITO
    '''.format(
        filtro_nivel=filtro_nivel,
        filtro_positivos=filtro_positivos,
        filtro_zerados=filtro_zerados,
        filtro_negativos=filtro_negativos,
        filtro_preco_zerado=filtro_preco_zerado,
        filtro_deposito_compras=filtro_deposito_compras,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def refs_com_movimento(cursor, data_ini=None):
    filtro_data_ini = ''
    if data_ini is not None:
        filtro_data_ini = (
            "AND ee.DATA_MOVIMENTO >= "
            "TO_DATE('{data_ini}', 'yyyy-mm-dd')".format(data_ini=data_ini)
        )

    sql = '''
        SELECT DISTINCT
          ee.GRUPO_ESTRUTURA REF
        FROM ESTQ_300_ESTQ_310 ee
        WHERE ee.NIVEL_ESTRUTURA = 1
          AND ee.GRUPO_ESTRUTURA < 'C0000'
          AND ee.CODIGO_DEPOSITO IN (231, 101, 102)
          {filtro_data_ini} -- filtro_data_ini
        ORDER BY
          ee.GRUPO_ESTRUTURA
    '''.format(
        filtro_data_ini=filtro_data_ini,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def grade_estoque(cursor, ref, dep, data_ini=None):

    filtro_data_ini = ''
    if data_ini is not None:
        filtro_data_ini = (
            "AND ee.DATA_MOVIMENTO >= "
            "TO_DATE('{data_ini}', 'yyyy-mm-dd')".format(data_ini=data_ini)
        )

    # Grade de OP
    grade = GradeQtd(cursor)

    # tamanhos
    grade.col(
        id='TAMANHO',
        name='Tamanho',
        total='Total',
        forca_total=True,
        sql='''
            SELECT DISTINCT
              ee.SUBGRUPO_ESTRUTURA TAMANHO
            , tam.ORDEM_TAMANHO SEQUENCIA_TAMANHO
            FROM ESTQ_300_ESTQ_310 ee -- mov.de estoque em aberto e fechado
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = ee.SUBGRUPO_ESTRUTURA
            WHERE ee.NIVEL_ESTRUTURA = 1
              AND ee.GRUPO_ESTRUTURA = '{ref}'
              AND ee.CODIGO_DEPOSITO = {dep}
              {filtro_data_ini} -- filtro_data_ini
            ORDER BY
              2
        '''.format(
            ref=ref,
            dep=dep,
            filtro_data_ini=filtro_data_ini,
        )
    )

    # cores
    grade.row(
        id='SORTIMENTO',
        name='Cor',
        name_plural='Cores',
        total='Total',
        forca_total=True,
        sql='''
            SELECT DISTINCT
              ee.ITEM_ESTRUTURA SORTIMENTO
            FROM ESTQ_300_ESTQ_310 ee -- mov. de estoque em aberto e fechado
            WHERE ee.NIVEL_ESTRUTURA = 1
              AND ee.GRUPO_ESTRUTURA = '{ref}'
              AND ee.CODIGO_DEPOSITO = {dep}
              {filtro_data_ini} -- filtro_data_ini
            ORDER BY
              ee.ITEM_ESTRUTURA
        '''.format(
            ref=ref,
            dep=dep,
            filtro_data_ini=filtro_data_ini,
        )
    )

    # sortimento
    grade.value(
        id='QUANTIDADE',
        sql='''
        SELECT
          e.CDITEM_SUBGRUPO TAMANHO
        , e.CDITEM_ITEM SORTIMENTO
        , e.QTDE_ESTOQUE_ATU QUANTIDADE
        FROM ESTQ_040 e
        WHERE e.CDITEM_NIVEL99 = 1
          AND e.CDITEM_GRUPO = '{ref}'
          AND e.DEPOSITO = {dep}
        ORDER BY
          e.CDITEM_SUBGRUPO
        , e.CDITEM_ITEM
        '''.format(
            ref=ref,
            dep=dep,
        )
    )

    fields = grade.table_data['fields']
    data = grade.table_data['data']

    style = {}
    right_style = 'text-align: right;'
    bold_style = 'font-weight: bold;'
    for i in range(2, len(fields)):
        style[i] = right_style
    style[len(fields)] = right_style + bold_style
    data[-1]['|STYLE'] = bold_style

    result = (
        grade.table_data['header'],
        fields,
        data,
        style,
        grade.total,
    )

    return result
