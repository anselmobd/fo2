from utils.functions.models import rows_to_dict_list_lower


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
    elif deposito == 'A00':
        filtro_deposito = "AND e.DEPOSITO IN (101, 102, 122, 231)"
    else:
        filtro_deposito = "AND e.DEPOSITO = '{deposito}'".format(
            deposito=deposito)

    filtro_zerados = ''
    if not zerados:
        filtro_zerados = "AND e.qtde_estoque_atu != 0"

    if group in ['', 'rtcd']:
        select_fields = '''--
            , e.cditem_grupo
            , e.cditem_subgrupo
            , e.cditem_item
            , e.deposito
            , e.deposito || ' - ' || d.DESCRICAO DEP_DESCR
            , e.lote_acomp'''
        field_quantidade = ', e.qtde_estoque_atu qtd'
        group_fields = ''
        order_by = '''--
            , e.cditem_grupo
            , ta.ORDEM_TAMANHO
            , e.cditem_subgrupo
            , e.cditem_item
            , e.deposito
            , e.lote_acomp'''
    elif group == 'rctd':
        select_fields = '''--
            , e.cditem_grupo
            , e.cditem_subgrupo
            , e.cditem_item
            , e.deposito
            , e.deposito || ' - ' || d.DESCRICAO DEP_DESCR
            , e.lote_acomp'''
        field_quantidade = ', e.qtde_estoque_atu qtd'
        group_fields = ''
        order_by = '''--
            , e.cditem_grupo
            , e.cditem_item
            , ta.ORDEM_TAMANHO
            , e.cditem_subgrupo
            , e.deposito
            , e.lote_acomp'''
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
    elif group == 'd':
        select_fields = '''--
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
            , e.deposito
            , d.DESCRICAO'''
        order_by = '''--
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
            , ta.ORDEM_TAMANHO
            , e.cditem_subgrupo
            , e.cditem_item'''
        order_by = '''--
            , ta.ORDEM_TAMANHO
            , e.cditem_subgrupo
            , e.cditem_item'''
    elif group == 'ct':
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
            , e.cditem_item
            , ta.ORDEM_TAMANHO
            , e.cditem_subgrupo'''
        order_by = '''--
            , e.cditem_item
            , ta.ORDEM_TAMANHO
            , e.cditem_subgrupo'''

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

    sql = f'''
        SELECT
          e.cditem_nivel99
        {select_fields} -- select_fields
        {field_quantidade} -- field_quantidade
        FROM ESTQ_040 e
        LEFT JOIN BASI_205 d
          ON d.CODIGO_DEPOSITO = e.DEPOSITO
        LEFT JOIN BASI_220 ta
          ON ta.TAMANHO_REF = e.cditem_subgrupo
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
    '''
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
