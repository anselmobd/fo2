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
    solicitado = argdef('solicitado', 't')  # default todos os pedidos
    total = argdef('total', None)

    filtra_pedido = ''
    if pedido is not None:
        filtra_pedido = f"AND i.PEDIDO_VENDA = {pedido}"

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
        filtro_modelo = f"""--
            AND TRIM(LEADING '0' FROM
                     (REGEXP_REPLACE(i.CD_IT_PE_GRUPO,
                                     '^[abAB]?([^a-zA-Z]+)[a-zA-Z]*$', '\\1'
                                     ))) = '{modelo}' """

    filtra_periodo = ''
    if periodo is not None:
        periodo_list = periodo.split(':')
        if periodo_list[0] != '':
            filtra_periodo += f"""--
                AND ped.DATA_ENTR_VENDA > CURRENT_DATE + {periodo_list[0]}
            """
        if periodo_list[1] != '':
            filtra_periodo += f"""--
                AND ped.DATA_ENTR_VENDA <= CURRENT_DATE + {periodo_list[1]}
            """

    filtro_cancelado = ''
    if cancelado in ['n', 'a']:  # não cancelado ou ativo
        filtro_cancelado = """--
            AND ped.STATUS_PEDIDO <> 5 -- não cancelado
        """
    elif cancelado in ['c', 'i']:  # cancelado ou inativo
        filtro_cancelado = """--
            AND ped.STATUS_PEDIDO = 5 -- cancelado
        """

    filtro_faturado = ''
    if faturado == 'f':  # faturado
        filtro_faturado = """--
            AND f.NUM_NOTA_FISCAL IS NOT NULL -- faturado
        """
    elif faturado == 'n':  # não faturado
        filtro_faturado = """--
            AND f.NUM_NOTA_FISCAL IS NULL -- não faturado
        """

    filtro_faturavel = ''
    if faturavel == 'f':  # faturavel
        filtro_faturavel = """--
            AND fok.NUM_NOTA_FISCAL IS NULL"""
    elif faturavel == 'n':  # não faturavel
        filtro_faturavel = """--
            AND fok.NUM_NOTA_FISCAL IS NOT NULL"""

    filtro_solicitado = ''
    if solicitado == 's':  # solicitado
        filtro_solicitado = """--
            AND EXISTS
                ( SELECT
                    1
                  FROM pcpc_044 sl -- solicitação / lote 
                  WHERE sl.PEDIDO_DESTINO = i.PEDIDO_VENDA
                    AND sl.SITUACAO <> 0
                )
        """
    elif solicitado == 'n':  # não solicitado
        filtro_solicitado = """--
            AND NOT EXISTS
                ( SELECT
                    1
                  FROM pcpc_044 sl -- solicitação / lote 
                  WHERE sl.PEDIDO_DESTINO = i.PEDIDO_VENDA
                    AND sl.SITUACAO <> 0
                )
        """

    grade_args = {}
    if total is not None:
        grade_args = {
            'total': total,
            'forca_total': True,
        }

    # Grade de pedido
    grade = GradeQtd(cursor)

    # tamanhos
    sql=f"""
        SELECT DISTINCT
          i.CD_IT_PE_SUBGRUPO TAMANHO
        , t.ORDEM_TAMANHO
        FROM PEDI_110 i -- item de pedido de venda
        JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = i.PEDIDO_VENDA
        LEFT JOIN FATU_050 f -- fatura
          ON f.PEDIDO_VENDA = ped.PEDIDO_VENDA
         AND f.SITUACAO_NFISC <> 2  -- cancelada
         AND f.NUMERO_CAIXA_ECF = 0
        LEFT JOIN FATU_050 fok -- fatura
          ON fok.PEDIDO_VENDA = ped.PEDIDO_VENDA
         AND fok.SITUACAO_NFISC <> 2  -- cancelada
         AND fok.NUMERO_CAIXA_ECF = 0
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = i.CD_IT_PE_SUBGRUPO
        WHERE 1=1
          {filtra_pedido} -- filtra_pedido
          {filtro_modelo} -- filtro_modelo
          {filtra_periodo} -- filtra_periodo
          {filtro_cancelado} -- filtro_cancelado
          {filtro_faturado} -- filtro_faturado
          {filtro_faturavel} -- filtro_faturavel
          {filtro_solicitado} -- filtro_solicitado
        ORDER BY
          t.ORDEM_TAMANHO
    """
    grade.col(
        id='TAMANHO',
        name='Tamanho',
        **grade_args,
        sql=sql,
    )

    # cores
    sql = f"""
        SELECT
          {sort_expression} SORTIMENTO
    """
    if descr_sort:
        sql += f"""--
            , {sort_expression} || ' - ' ||
              max( rtc.DESCRICAO_15 ) DESCR
        """
    else:
        sql += f"""--
            , {sort_expression} DESCR
        """
    sql += """--
        FROM PEDI_110 i -- item de pedido de venda
        JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = i.PEDIDO_VENDA
        LEFT JOIN FATU_050 f -- fatura
          ON f.PEDIDO_VENDA = ped.PEDIDO_VENDA
         AND f.SITUACAO_NFISC <> 2  -- cancelada
         AND f.NUMERO_CAIXA_ECF = 0
        LEFT JOIN FATU_050 fok -- fatura
          ON fok.PEDIDO_VENDA = ped.PEDIDO_VENDA
         AND fok.SITUACAO_NFISC <> 2  -- cancelada
         AND fok.NUMERO_CAIXA_ECF = 0
    """
    if descr_sort:
        sql += """--
            JOIN BASI_010 rtc -- item (ref+tam+cor)
              on rtc.NIVEL_ESTRUTURA = i.CD_IT_PE_NIVEL99
             AND rtc.GRUPO_ESTRUTURA = i.CD_IT_PE_GRUPO
             AND rtc.SUBGRU_ESTRUTURA = i.CD_IT_PE_SUBGRUPO
             AND rtc.ITEM_ESTRUTURA = i.CD_IT_PE_ITEM
        """
    sql += f"""--
        WHERE 1=1
          {filtra_pedido} -- filtra_pedido
          {filtro_modelo} -- filtro_modelo
          {filtra_periodo} -- filtra_periodo
          {filtro_cancelado} -- filtro_cancelado
          {filtro_faturado} -- filtro_faturado
          {filtro_faturavel} -- filtro_faturavel
          {filtro_solicitado} -- filtro_solicitado
        GROUP BY
          {sort_group} -- sort_group
        ORDER BY
          2
        """
    grade.row(
        id='SORTIMENTO',
        facade='DESCR',
        name=sort_name,
        name_plural=sort_name_plural,
        **grade_args,
        sql=sql
    )

    # sortimento
    sql=f"""
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
         AND f.NUMERO_CAIXA_ECF = 0
        LEFT JOIN FATU_050 fok -- fatura
          ON fok.PEDIDO_VENDA = ped.PEDIDO_VENDA
         AND fok.SITUACAO_NFISC <> 2  -- cancelada
         AND fok.NUMERO_CAIXA_ECF = 0
        WHERE 1=1
          {filtra_pedido} -- filtra_pedido
          {filtro_modelo} -- filtro_modelo
          {filtra_periodo} -- filtra_periodo
          {filtro_cancelado} -- filtro_cancelado
          {filtro_faturado} -- filtro_faturado
          {filtro_faturavel} -- filtro_faturavel
          {filtro_solicitado} -- filtro_solicitado
        GROUP BY
          {sort_group} -- sort_group
        , i.CD_IT_PE_SUBGRUPO
    """
    grade.value(
        id='QUANTIDADE',
        sql=sql,
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
