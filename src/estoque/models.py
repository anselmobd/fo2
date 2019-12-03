import time
from pprint import pprint

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


def grade_estoque(cursor, ref, dep, data_ini=None, tipo_grade=None):

    filtro_data_ini = ''
    if data_ini is not None:
        filtro_data_ini = (
            "AND ee.DATA_MOVIMENTO >= "
            "TO_DATE('{data_ini}', 'yyyy-mm-dd')".format(data_ini=data_ini)
        )

    if tipo_grade is None:
        tipo_grade = {
            't': 'c',  # tamanho como cadastrado
            'c': 'e',  # cores com estoque
        }

    # Grade de OP
    grade = GradeQtd(cursor)

    # tamanhos
    if tipo_grade['t'] == 'm':  # com movimento
        sql = '''
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
    elif tipo_grade['t'] == 'e':  # com estoque
        sql = '''
            SELECT DISTINCT
              e.CDITEM_SUBGRUPO TAMANHO
            , tam.ORDEM_TAMANHO SEQUENCIA_TAMANHO
            FROM ESTQ_040 e
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = e.CDITEM_SUBGRUPO
            WHERE e.CDITEM_NIVEL99 = 1
              AND e.CDITEM_GRUPO = '{ref}'
              AND e.DEPOSITO = {dep}
              AND e.QTDE_ESTOQUE_ATU <> 0
            ORDER BY
              2
        '''.format(
            ref=ref,
            dep=dep,
        )

    elif tipo_grade['t'] == 'c':  # como cadastrado
        sql = '''
            SELECT
              t.TAMANHO_REF TAMANHO
            , tam.ORDEM_TAMANHO SEQUENCIA_TAMANHO
            FROM basi_020 t
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = t.TAMANHO_REF
            WHERE t.BASI030_NIVEL030 = 1
              AND t.BASI030_REFERENC = '{ref}'
            ORDER BY
              2
        '''.format(
            ref=ref,
        )

    grade.col(
        id='TAMANHO',
        name='Tamanho',
        total='Total',
        forca_total=True,
        sql=sql,
    )

    # cores
    if tipo_grade['c'] == 'm':  # com movimento
        sql = '''
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
    elif tipo_grade['c'] == 'e':  # com estoque
        sql = '''
            SELECT DISTINCT
              e.CDITEM_ITEM SORTIMENTO
            FROM ESTQ_040 e
            WHERE e.CDITEM_NIVEL99 = 1
              AND e.CDITEM_GRUPO = '{ref}'
              AND e.DEPOSITO = {dep}
              AND e.QTDE_ESTOQUE_ATU <> 0
            ORDER BY
              e.CDITEM_ITEM
        '''.format(
            ref=ref,
            dep=dep,
        )

    grade.row(
        id='SORTIMENTO',
        name='Cor',
        name_plural='Cores',
        total='Total',
        forca_total=True,
        sql=sql,
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


def referencia_deposito(cursor, modelo):
    filtro_modelo = ''
    if modelo != '':
        filtro_modelo = '''--
            AND
              TRIM(
                LEADING '0' FROM (
                  REGEXP_REPLACE(
                    rtc.GRUPO_ESTRUTURA,
                    '^[abAB]?([0-9]+)[a-zA-Z]*$',
                    '\\1'
                  )
                )
              ) = '{modelo}'
        '''.format(
            modelo=modelo,
        )

    sql = '''
        SELECT DISTINCT
          i.REF
        , i.DEP
        FROM (
          SELECT
            rtc.GRUPO_ESTRUTURA REF
          , rtc.SUBGRU_ESTRUTURA TAM
          , rtc.ITEM_ESTRUTURA COR
          , d.CODIGO_DEPOSITO DEP
          FROM BASI_010 rtc, BASI_205 d
          WHERE 1=1
            AND rtc.NIVEL_ESTRUTURA = 1
            AND d.CODIGO_DEPOSITO IN (101, 102, 231)
            AND rtc.GRUPO_ESTRUTURA < 'C0000'
            {filtro_modelo} -- filtro_modelo
        ) i
        LEFT JOIN ESTQ_040 e
          ON e.CDITEM_NIVEL99 = 1
         AND e.CDITEM_GRUPO = i.REF
         AND e.CDITEM_SUBGRUPO = i.TAM
         AND e.CDITEM_ITEM = i.COR
         AND e.DEPOSITO = i.DEP
         AND e.QTDE_ESTOQUE_ATU <> 0
        LEFT JOIN ESTQ_300_ESTQ_310 m -- movimentação de estoque
          ON m.NIVEL_ESTRUTURA = 1
         AND m.GRUPO_ESTRUTURA = i.REF
         AND m.SUBGRUPO_ESTRUTURA = i.TAM
         AND m.ITEM_ESTRUTURA = i.COR
         AND m.CODIGO_DEPOSITO = i.DEP
        WHERE (  e.DEPOSITO IS NOT NULL
              OR m.CODIGO_DEPOSITO IS NOT NULL
              )
        ORDER BY
          NLSSORT(i.REF,'NLS_SORT=BINARY_AI')
        , i.DEP
    '''.format(
        filtro_modelo=filtro_modelo,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def estoque_deposito_ref(cursor, deposito, ref):
    sql = '''
        SELECT
          i.REF
        , i.COR
        , ta.ORDEM_TAMANHO
        , i.TAM
        , i.DEP
        , COALESCE(e.QTDE_ESTOQUE_ATU, 0) QTD
        FROM (
          SELECT
            rtc.GRUPO_ESTRUTURA REF
          , rtc.SUBGRU_ESTRUTURA TAM
          , rtc.ITEM_ESTRUTURA COR
          , d.CODIGO_DEPOSITO DEP
          FROM BASI_010 rtc, BASI_205 d
          WHERE 1=1
            AND rtc.NIVEL_ESTRUTURA = 1
            AND d.CODIGO_DEPOSITO = '{deposito}'
            AND rtc.GRUPO_ESTRUTURA = '{ref}'
        ) i
        LEFT JOIN BASI_220 ta
          ON ta.TAMANHO_REF = i.TAM
        LEFT JOIN ESTQ_040 e
          ON e.CDITEM_NIVEL99 = 1
         AND e.CDITEM_GRUPO = i.REF
         AND e.CDITEM_SUBGRUPO = i.TAM
         AND e.CDITEM_ITEM = i.COR
         AND e.DEPOSITO = i.DEP
        ORDER BY
          NLSSORT(i.REF,'NLS_SORT=BINARY_AI')
        , i.COR
        , ta.ORDEM_TAMANHO
    '''.format(
        deposito=deposito,
        ref=ref,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def ajusta_estoque_dep_ref_cor_tam(cursor, deposito, ref, cor, tam, qtd):
    sql = '''
        SELECT
          {qtd} - e.QTDE_ESTOQUE_ATU AJUSTE
        FROM ESTQ_040 e
        WHERE 1=1
          AND e.CDITEM_NIVEL99 = 1
          AND e.CDITEM_GRUPO = '{ref}'
          AND e.CDITEM_SUBGRUPO = '{tam}'
          AND e.CDITEM_ITEM = '{cor}'
          AND e.DEPOSITO = {deposito}
    '''.format(
        qtd=qtd,
        deposito=deposito,
        ref=ref,
        cor=cor,
        tam=tam,
    )
    cursor.execute(sql)
    estoque = rows_to_dict_list_lower(cursor)
    # pprint(estoque)
    if len(estoque) == 0:
        ajuste = qtd
    else:
        ajuste = estoque[0]['ajuste']
    if ajuste == 0:
        return []

    sinal = 1 if ajuste > 0 else -1
    ajuste *= sinal

    sql = '''
        SELECT
          coalesce(rtc.PRECO_MEDIO, 0) PRECO_MEDIO
        FROM BASI_010 rtc
        WHERE 1=1
          AND rtc.NIVEL_ESTRUTURA = 1
          AND rtc.GRUPO_ESTRUTURA = '{ref}'
          AND rtc.SUBGRU_ESTRUTURA = '{tam}'
          AND rtc.ITEM_ESTRUTURA = '{cor}'
    '''.format(
        ref=ref,
        cor=cor,
        tam=tam,
    )
    cursor.execute(sql)
    produto = rows_to_dict_list_lower(cursor)
    if len(produto) == 0:
        return []
    preco_medio = produto[0]['preco_medio']

    num_doc = '702{}'.format(time.strftime('%y%m%d'))

    transacoes = {
        1: {
            'codigo': 105,
            'es': 'E',
        },
        -1: {
            'codigo': 3,
            'es': 'S',
        },
    }

    sql = '''
        INSERT INTO ESTQ_300 (
          CODIGO_DEPOSITO
        , NIVEL_ESTRUTURA
        , GRUPO_ESTRUTURA
        , SUBGRUPO_ESTRUTURA
        , ITEM_ESTRUTURA
        , DATA_MOVIMENTO
        , SEQUENCIA_FICHA
        , SEQUENCIA_INSERCAO
        , NUMERO_LOTE
        , NUMERO_DOCUMENTO
        , SERIE_DOCUMENTO
        , CNPJ_9
        , CNPJ_4
        , CNPJ_2
        , SEQUENCIA_DOCUMENTO
        , CODIGO_TRANSACAO
        , ENTRADA_SAIDA
        , CENTRO_CUSTO
        , QUANTIDADE
        , SALDO_FISICO
        , VALOR_MOVIMENTO_UNITARIO
        , VALOR_CONTABIL_UNITARIO
        , PRECO_MEDIO_UNITARIO
        , SALDO_FINANCEIRO
        , GRUPO_MAQUINA
        , SUBGRU_MAQUINA
        , NUMERO_MAQUINA
        , ORDEM_SERVICO
        , CONTABILIZADO
        , USUARIO_SYSTEXTIL
        , PROCESSO_SYSTEXTIL
        , DATA_INSERCAO
        , USUARIO_REDE
        , MAQUINA_REDE
        , APLICATIVO
        , TABELA_ORIGEM
        , FLAG_ELIMINA
        , VALOR_MOVIMENTO_UNITARIO_PROJ
        , VALOR_CONTABIL_UNITARIO_PROJ
        , PRECO_MEDIO_UNITARIO_PROJ
        , SALDO_FINANCEIRO_PROJ
        , VALOR_MOVTO_UNIT_ESTIMADO
        , PRECO_MEDIO_UNIT_ESTIMADO
        , SALDO_FINANCEIRO_ESTIMADO
        , VALOR_TOTAL
        , PROJETO
        , SUBPROJETO
        , SERVICO
        , QUANTIDADE_QUILO
        , SALDO_FISICO_QUILO
        , ESTAGIO_OP
        , NUMERO_NF
        , NUMERO_OP
        , NUMERO_OS
        , TIPO_ORDEM
        , TIPO_SPED_TRANSACAO
        ) VALUES (
          {deposito}  -- CODIGO_DEPOSITO
        , '1'  -- NIVEL_ESTRUTURA
        , '{ref}'  -- GRUPO_ESTRUTURA
        , '{tam}'  -- SUBGRUPO_ESTRUTURA
        , '{cor}'  -- ITEM_ESTRUTURA
        , sysdate  -- TIMESTAMP '2019-11-28 00:00:00.000000'  -- DATA_MOVIMENTO
        , 0  -- SEQUENCIA_FICHA
        , 1  -- SEQUENCIA_INSERCAO
        , 0  -- NUMERO_LOTE
        , {num_doc}  -- NUMERO_DOCUMENTO
        , NULL  -- SERIE_DOCUMENTO
        , 0  -- CNPJ_9
        , 0  -- CNPJ_4
        , 0  -- CNPJ_2
        , 0  -- SEQUENCIA_DOCUMENTO
        , {trans}  -- CODIGO_TRANSACAO
        , '{es}'  -- ENTRADA_SAIDA
        , 0  -- CENTRO_CUSTO
        , {ajuste}  -- QUANTIDADE
        , 0  -- SALDO_FISICO
        , {preco_medio}  -- VALOR_MOVIMENTO_UNITARIO
        , 0  -- 2  -- VALOR_CONTABIL_UNITARIO
        , 0  -- PRECO_MEDIO_UNITARIO
        , 0  -- SALDO_FINANCEIRO
        , NULL  -- GRUPO_MAQUINA
        , NULL  -- SUBGRU_MAQUINA
        , 0  -- NUMERO_MAQUINA
        , NULL  -- ORDEM_SERVICO
        , 0  -- CONTABILIZADO
        , 'ANSELMO_SIS'  -- USUARIO_SYSTEXTIL
        , 'estq_f950'  -- PROCESSO_SYSTEXTIL
        , sysdate  -- TIMESTAMP '2019-11-28 12:00:00.000000'  -- DATA_INSERCAO
        , 'ANSELMO_SIS'  -- USUARIO_REDE
        , '192.168.1.242'  -- MAQUINA_REDE
        , 'estq_f950'  -- APLICATIVO
        , 'ESTQ_300'  -- TABELA_ORIGEM
        , 0  -- FLAG_ELIMINA
        , 0  -- VALOR_MOVIMENTO_UNITARIO_PROJ
        , 0  -- VALOR_CONTABIL_UNITARIO_PROJ
        , 0  -- PRECO_MEDIO_UNITARIO_PROJ
        , 0  -- SALDO_FINANCEIRO_PROJ
        , 0  -- VALOR_MOVTO_UNIT_ESTIMADO
        , 0  -- PRECO_MEDIO_UNIT_ESTIMADO
        , 0  -- SALDO_FINANCEIRO_ESTIMADO
        , {valor_total}  -- VALOR_TOTAL
        , 0  -- PROJETO
        , 0  -- SUBPROJETO
        , 0  -- SERVICO
        , 0  -- QUANTIDADE_QUILO
        , 0  -- SALDO_FISICO_QUILO
        , NULL  -- ESTAGIO_OP
        , NULL  -- NUMERO_NF
        , NULL  -- NUMERO_OP
        , NULL  -- NUMERO_OS
        , NULL  -- TIPO_ORDEM
        , NULL  -- TIPO_SPED_TRANSACAO
        )
    '''.format(
        deposito=deposito,
        ref=ref,
        tam=tam,
        cor=cor,
        num_doc=num_doc,
        trans=transacoes[sinal]['codigo'],
        es=transacoes[sinal]['es'],
        ajuste=ajuste,
        preco_medio=preco_medio,
        valor_total=ajuste*preco_medio,
    )
    # print(sql)
    cursor.execute(sql)

    return [{
        'ajuste': ajuste,
        'trans': transacoes[sinal]['codigo'],
        'es': transacoes[sinal]['es'],
    }]
