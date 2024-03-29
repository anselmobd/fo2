from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


__all__=['posicao_estoque']


def posicao_estoque(
        cursor, nivel, ref, tam, cor, deposito='999', zerados=True, group='',
        tipo='t', modelo=None, empresa=None):
    """Retorna quantidades de itens nos depósitos
    Recebe filtros por:
        nivel
        ref: referência
            pode ser uma referência ou uma lista
        tam: tamanho
        cor
        deposito
        zerados: boleano se mostra itens sem estoque
        tipo:
            t: todos
            a: PA
            g: PG
            b: PB
            p: PG/PB
            v: PA/PG/PB
            m: MD (MP)
        modelo
            pode ser uma modelo ou uma lista
        empresa: depósitos da empresa
    Recebe configuração:
        group: indica campos a serem devolvidos e agrupados, 
               campos totalizados e ordenação
            rtcd: Referência/Tamanho/Cor/Depósito -> qtd
            rctd: Referência/Cor/Tamanho/Depósito -> qtd
            rd: Referência/Depósito -> qtd+, qtd- e qtd
            md: Modelo/Depósito -> qtd+, qtd- e qtd
            tc: Tamanho/Cor -> qtd+, qtd- e qtd
            ct: Cor/Tamanho -> qtd+, qtd- e qtd
            r: Referência -> qtd+, qtd- e qtd
            m: Modelo -> qtd+, qtd- e qtd
            d: Depósito -> qtd+, qtd- e qtd
    """

    sql_modelo = "REGEXP_SUBSTR(e.CDITEM_GRUPO, '[1-9][0-9]*')"

    filtro_nivel = ''
    if nivel is not None:
        filtro_nivel = f"AND e.CDITEM_NIVEL99 = {nivel}"

    if ref:
        if isinstance(ref, (tuple, list)):
            refs = set(ref)
        else:
            refs = {ref, }
        refs_sql = ', '.join([f"'{r1}'" for r1 in list(refs)])
        filtro_ref = f"""--
            AND e.CDITEM_GRUPO in ({refs_sql})
        """
    else:
        filtro_ref = ''

    if modelo:
        if isinstance(modelo, (tuple, list)):
            modelos = set(modelo)
        else:
            modelos = {modelo, }
        modelos_sql = ', '.join([f"'{m1}'" for m1 in list(modelos)])
        filtro_modelo = f"""--
            AND {sql_modelo} in ({modelos_sql})
        """
    else:
        filtro_modelo = ''

    filtro_tam = ''
    if tam != '':
        filtro_tam = f"AND e.CDITEM_SUBGRUPO = '{tam}'"

    filtro_cor = ''
    if cor != '':
        filtro_cor = f"AND e.CDITEM_ITEM = '{cor}'"

    if deposito == '999':
        filtro_deposito = ''
    elif deposito == 'A00':
        filtro_deposito = "AND e.DEPOSITO IN (101, 102, 231)"
    else:
        filtro_deposito = f"AND e.DEPOSITO = '{deposito}'"

    filtro_zerados = ''
    if not zerados:
        filtro_zerados = "AND e.qtde_estoque_atu != 0"

    qtd_pos_e_neg = '''--
        , sum(e.qtde_estoque_atu) qtd
        , sum(case when e.qtde_estoque_atu > 0
                then e.qtde_estoque_atu else 0 end) qtd_positiva
        , sum(case when e.qtde_estoque_atu < 0
                then e.qtde_estoque_atu else 0 end) qtd_negativa'''

    if group in ['', 'rtcd']:
        select_fields = '''--
            , e.cditem_grupo ref
            , e.cditem_subgrupo tam
            , e.cditem_item cor
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
            , e.cditem_grupo ref
            , e.cditem_subgrupo tam
            , e.cditem_item cor
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
    elif group == 'rd':
        select_fields = '''--
            , e.cditem_grupo ref
            , e.deposito
            , e.deposito || ' - ' || d.DESCRICAO DEP_DESCR'''
        field_quantidade = qtd_pos_e_neg
        group_fields = '''--
            GROUP BY
              e.cditem_nivel99
            , e.cditem_grupo
            , e.deposito
            , d.DESCRICAO'''
        order_by = '''--
            , e.cditem_grupo
            , e.deposito'''
    elif group == 'md':
        select_fields = f'''--
            , {sql_modelo} modelo
            , e.deposito
            , e.deposito || ' - ' || d.DESCRICAO DEP_DESCR'''
        field_quantidade = qtd_pos_e_neg
        group_fields = f'''--
            GROUP BY
              e.cditem_nivel99
            , {sql_modelo}
            , e.deposito
            , d.DESCRICAO'''
        order_by = f'''--
            , {sql_modelo}
            , e.deposito'''
    elif group == 'r':
        select_fields = ''', e.cditem_grupo ref'''
        field_quantidade = qtd_pos_e_neg
        group_fields = '''--
            GROUP BY
              e.cditem_nivel99
            , e.cditem_grupo'''
        order_by = '''--
            , e.cditem_grupo'''
    elif group == 'm':
        select_fields = f", {sql_modelo} modelo"
        field_quantidade = qtd_pos_e_neg
        group_fields = f'''--
            GROUP BY
              e.cditem_nivel99
            , {sql_modelo}'''
        order_by = f'''--
            , {sql_modelo}'''
    elif group == 'd':
        select_fields = '''--
            , e.deposito
            , e.deposito || ' - ' || d.DESCRICAO DEP_DESCR'''
        field_quantidade = qtd_pos_e_neg
        group_fields = '''--
            GROUP BY
              e.cditem_nivel99
            , e.deposito
            , d.DESCRICAO'''
        order_by = '''--
            , e.deposito'''
    elif group == 'tc':
        select_fields = '''--
            , e.cditem_subgrupo tam
            , e.cditem_item cor'''
        field_quantidade = qtd_pos_e_neg
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
            , e.cditem_subgrupo tam
            , e.cditem_item cor'''
        field_quantidade = qtd_pos_e_neg
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

    filtro_empresa = f"AND d.LOCAL_DEPOSITO = {empresa}" if empresa else ''

    sql = f'''
        SELECT
          e.cditem_nivel99 nivel
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
          {filtro_empresa} -- filtro_empresa
        {group_fields} -- group_fields
        ORDER BY
          e.CDITEM_NIVEL99
        {order_by} -- order_by
    '''
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
