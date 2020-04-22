from utils.functions.models import GradeQtd

from utils.functions import arg_def


def sortimento(cursor, **kwargs):
    def argdef(arg, default):
        return arg_def(kwargs, arg, default)

    pedido = argdef('pedido', None)
    tipo_sort = argdef('tipo_sort', 'rc')
    descr_sort = argdef('descr_sort', True)
    modelo = argdef('modelo', None)
    periodo = argdef('periodo', None)
    cancelado = argdef('cancelado', 't')  # default todos os pedidos
    faturado = argdef('faturado', 't')  # default todos os pedidos
    faturavel = argdef('faturavel', 't')  # default todos os pedidos
    total = argdef('total', None)

    filtra_pedido = ''
    if pedido is not None:
        filtra_pedido = 'AND i.PEDIDO_VENDA = {}'.format(pedido)

    if tipo_sort == 'rc':
        sort_expression = "i.CD_IT_PE_GRUPO || ' - ' || i.CD_IT_PE_ITEM"
        sort_group = "i.CD_IT_PE_GRUPO, i.CD_IT_PE_ITEM"
        sort_name = 'Produto-Cor'
        sort_name_plural = 'Produtos-Cores'
    else:  # if tipo_sort == 'c':
        sort_expression = "i.CD_IT_PE_ITEM"
        sort_group = "i.CD_IT_PE_ITEM"
        sort_name = 'Cor'
        sort_name_plural = 'Cores'

    filtro_modelo = ''
    if modelo is not None:
        filtro_modelo = '''--
            AND TRIM(LEADING '0' FROM
                     (REGEXP_REPLACE(i.CD_IT_PE_GRUPO,
                                     '^[abAB]?([^a-zA-Z]+)[a-zA-Z]*$', '\\1'
                                     ))) = '{}' '''.format(modelo)

    filtra_periodo = ''
    if periodo is not None:
        periodo_list = periodo.split(':')
        if periodo_list[0] != '':
            filtra_periodo += '''
                AND ped.DATA_ENTR_VENDA > CURRENT_DATE + {}
            '''.format(periodo_list[0])
        if periodo_list[1] != '':
            filtra_periodo += '''
                AND ped.DATA_ENTR_VENDA <= CURRENT_DATE + {}
            '''.format(periodo_list[1])

    filtro_cancelado = ''
    if cancelado in ['n', 'a']:  # não cancelado ou ativo
        filtro_cancelado = '''--
            AND ped.STATUS_PEDIDO <> 5 -- não cancelado
        '''
    elif cancelado in ['c', 'i']:  # cancelado ou inativo
        filtro_cancelado = '''--
            AND ped.STATUS_PEDIDO = 5 -- cancelado
        '''

    filtro_faturado = ''
    if faturado == 'f':  # faturado
        filtro_faturado = '''--
            AND f.NUM_NOTA_FISCAL IS NOT NULL -- faturado
        '''
    elif faturado == 'n':  # não faturado
        filtro_faturado = '''--
            AND f.NUM_NOTA_FISCAL IS NULL -- não faturado
        '''

    filtro_faturavel = ''
    if faturavel == 'f':  # faturavel
        filtro_faturavel = """--
            AND fok.NUM_NOTA_FISCAL IS NULL"""
    elif faturavel == 'n':  # não faturavel
        filtro_faturavel = """--
            AND fok.NUM_NOTA_FISCAL IS NOT NULL"""

    grade_args = {}
    if total is not None:
        grade_args = {
            'total': total,
            'forca_total': True,
        }

    # Grade de pedido
    grade = GradeQtd(cursor)

    # tamanhos
    grade.col(
        id='TAMANHO',
        name='Tamanho',
        **grade_args,
        sql='''
            SELECT DISTINCT
              i.CD_IT_PE_SUBGRUPO TAMANHO
            , t.ORDEM_TAMANHO
            FROM PEDI_110 i -- item de pedido de venda
            JOIN PEDI_100 ped -- pedido de venda
              ON ped.PEDIDO_VENDA = i.PEDIDO_VENDA
            LEFT JOIN FATU_050 f -- fatura
              ON f.PEDIDO_VENDA = ped.PEDIDO_VENDA
             AND f.SITUACAO_NFISC <> 2  -- cancelada
            LEFT JOIN FATU_050 fok -- fatura
              ON fok.PEDIDO_VENDA = ped.PEDIDO_VENDA
             AND fok.SITUACAO_NFISC <> 2  -- cancelada
            LEFT JOIN BASI_220 t -- tamanhos
              ON t.TAMANHO_REF = i.CD_IT_PE_SUBGRUPO
            WHERE 1=1
              {filtra_pedido} -- filtra_pedido
              {filtro_modelo} -- filtro_modelo
              {filtra_periodo} -- filtra_periodo
              {filtro_cancelado} -- filtro_cancelado
              {filtro_faturado} -- filtro_faturado
              {filtro_faturavel} -- filtro_faturavel
            ORDER BY
              t.ORDEM_TAMANHO
        '''.format(
            filtra_pedido=filtra_pedido,
            filtro_modelo=filtro_modelo,
            filtra_periodo=filtra_periodo,
            filtro_cancelado=filtro_cancelado,
            filtro_faturado=filtro_faturado,
            filtro_faturavel=filtro_faturavel,
        )
    )

    # cores
    sql = '''
        SELECT
          {sort_expression} SORTIMENTO
    '''
    if descr_sort:
        sql += '''
            , {sort_expression} || ' - ' ||
              max( rtc.DESCRICAO_15 ) DESCR
        '''
    else:
        sql += '''
            , {sort_expression} DESCR
        '''
    sql += '''
        FROM PEDI_110 i -- item de pedido de venda
        JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = i.PEDIDO_VENDA
        LEFT JOIN FATU_050 f -- fatura
          ON f.PEDIDO_VENDA = ped.PEDIDO_VENDA
         AND f.SITUACAO_NFISC <> 2  -- cancelada
        LEFT JOIN FATU_050 fok -- fatura
          ON fok.PEDIDO_VENDA = ped.PEDIDO_VENDA
         AND fok.SITUACAO_NFISC <> 2  -- cancelada
    '''
    if descr_sort:
        sql += '''
            JOIN BASI_010 rtc -- item (ref+tam+cor)
              on rtc.NIVEL_ESTRUTURA = i.CD_IT_PE_NIVEL99
             AND rtc.GRUPO_ESTRUTURA = i.CD_IT_PE_GRUPO
             AND rtc.SUBGRU_ESTRUTURA = i.CD_IT_PE_SUBGRUPO
             AND rtc.ITEM_ESTRUTURA = i.CD_IT_PE_ITEM
        '''
    sql += '''
        WHERE 1=1
          {filtra_pedido} -- filtra_pedido
          {filtro_modelo} -- filtro_modelo
          {filtra_periodo} -- filtra_periodo
          {filtro_cancelado} -- filtro_cancelado
          {filtro_faturado} -- filtro_faturado
          {filtro_faturavel} -- filtro_faturavel
        GROUP BY
          {sort_group} -- sort_group
        ORDER BY
          2
        '''
    sql = sql.format(
        filtra_pedido=filtra_pedido,
        filtro_modelo=filtro_modelo,
        filtra_periodo=filtra_periodo,
        filtro_cancelado=filtro_cancelado,
        filtro_faturado=filtro_faturado,
        filtro_faturavel=filtro_faturavel,
        sort_expression=sort_expression,
        sort_group=sort_group,
    )
    grade.row(
        id='SORTIMENTO',
        facade='DESCR',
        name=sort_name,
        name_plural=sort_name_plural,
        **grade_args,
        sql=sql
    )

    # sortimento
    grade.value(
        id='QUANTIDADE',
        sql='''
            SELECT
              {sort_expression} SORTIMENTO
            , i.CD_IT_PE_SUBGRUPO TAMANHO
            , sum(i.QTDE_PEDIDA) QUANTIDADE
            FROM PEDI_110 i -- item de pedido de venda
            JOIN PEDI_100 ped -- pedido de venda
              ON ped.PEDIDO_VENDA = i.PEDIDO_VENDA
            LEFT JOIN FATU_050 f -- fatura
              ON f.PEDIDO_VENDA = ped.PEDIDO_VENDA
             AND f.SITUACAO_NFISC <> 2  -- cancelada
            LEFT JOIN FATU_050 fok -- fatura
              ON fok.PEDIDO_VENDA = ped.PEDIDO_VENDA
             AND fok.SITUACAO_NFISC <> 2  -- cancelada
            WHERE 1=1
              {filtra_pedido} -- filtra_pedido
              {filtro_modelo} -- filtro_modelo
              {filtra_periodo} -- filtra_periodo
              {filtro_cancelado} -- filtro_cancelado
              {filtro_faturado} -- filtro_faturado
              {filtro_faturavel} -- filtro_faturavel
            GROUP BY
              {sort_group} -- sort_group
            , i.CD_IT_PE_SUBGRUPO
        '''.format(
            filtra_pedido=filtra_pedido,
            filtro_modelo=filtro_modelo,
            filtra_periodo=filtra_periodo,
            filtro_cancelado=filtro_cancelado,
            filtro_faturado=filtro_faturado,
            filtro_faturavel=filtro_faturavel,
            sort_expression=sort_expression,
            sort_group=sort_group,
        )
    )

    fields = grade.table_data['fields']
    data = grade.table_data['data']
    if total is None:
        result = (
            grade.table_data['header'],
            fields,
            data,
            grade.total,
        )
    else:
        result = (
            grade.table_data['header'],
            fields,
            data,
            grade.table_data['style'],
            grade.total,
        )
    return result
