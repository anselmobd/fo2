from fo2.models import rows_to_dict_list, GradeQtd

from lotes.models import *
from lotes.models.base import *


def ped_inform(cursor, pedido):
    # Informações sobre Pedido
    sql = """
        SELECT
          ped.PEDIDO_VENDA
        , ped.DATA_EMIS_VENDA DT_EMISSAO
        , ped.DATA_PREV_RECEB DT_RECEBIMENTO
        , ped.DATA_ENTR_VENDA DT_EMBARQUE
        , ped.OBSERVACAO
        , c.NOME_CLIENTE
          || ' (' || lpad(c.CGC_9, 8, '0')
          || '/' || lpad(c.CGC_4, 4, '0')
          || '-' || lpad(c.CGC_2, 2, '0')
          || ')' CLIENTE
        , COALESCE(ped.COD_PED_CLIENTE, ' ') PEDIDO_CLIENTE
        , CASE ped.STATUS_PEDIDO
          WHEN 0 THEN '0-Digitado'
          WHEN 1 THEN '1-Financeiro'
          WHEN 2 THEN '2-Liberado Financeiro'
          WHEN 3 THEN '3-Faturamento'
          WHEN 4 THEN '4-A cancelar'
          WHEN 5 THEN '5-Cancelado'
          WHEN 9 THEN '9-Aberto na web'
          END STATUS_PEDIDO
        , CASE ped.SITUACAO_VENDA
          WHEN 0  THEN '0-Pedido liberado'
          WHEN 5  THEN '5-Pedido suspenso'
          WHEN 10 THEN '10-Faturado total'
          WHEN 15 THEN '15-Pedido com NF cancelada'
          END SITUACAO_VENDA
        FROM PEDI_100 ped -- pedido de venda
        LEFT JOIN PEDI_010 c
          ON c.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND c.CGC_4 = ped.CLI_PED_CGC_CLI4
        WHERE ped.PEDIDO_VENDA = %s
    """
    cursor.execute(sql, [pedido])
    return rows_to_dict_list(cursor)


def ped_op(cursor, pedido):
    # OPs
    sql = """
        SELECT
          o.PEDIDO_VENDA
        , o.ORDEM_PRODUCAO
        , CASE
          when o.REFERENCIA_PECA <= '99999' then 'PA'
          when o.REFERENCIA_PECA <= 'B9999' then 'PG'
          when o.REFERENCIA_PECA >= 'Z0000' then 'MP'
          else 'MD'
          END TIPO
        , o.REFERENCIA_PECA
        , o.ORDEM_PRINCIPAL
        , ( SELECT
              SUM( l.QTDE_PECAS_PROG )
            FROM pcpc_040 l
            WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
              AND l.SEQ_OPERACAO = (
                SELECT
                  MAX( ls.SEQ_OPERACAO )
                FROM pcpc_040 ls
                WHERE ls.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
              )
          ) QTD
        , o.DATA_PROGRAMACAO DT_DIGITACAO
        , o.DATA_ENTRADA_CORTE DT_CORTE
        FROM PCPC_020 o -- OP
        WHERE o.PEDIDO_VENDA = %s
          AND o.SITUACAO <> 9
        ORDER BY
          o.ORDEM_PRINCIPAL
        , o.ORDEM_PRODUCAO
    """
    cursor.execute(sql, [pedido])
    return rows_to_dict_list(cursor)


def ped_sortimento(cursor, pedido):
    # Grade de pedido
    grade = GradeQtd(cursor, [pedido])

    # tamanhos
    grade.col(
        id='TAMANHO',
        name='Tamanho',
        sql='''
            SELECT DISTINCT
              i.CD_IT_PE_SUBGRUPO TAMANHO
            , t.ORDEM_TAMANHO
            FROM PEDI_110 i -- item de pedido de venda
            LEFT JOIN BASI_220 t -- tamanhos
              ON t.TAMANHO_REF = i.CD_IT_PE_SUBGRUPO
            WHERE i.PEDIDO_VENDA = %s
            ORDER BY
              t.ORDEM_TAMANHO
        '''
        )

    # cores
    grade.row(
        id='SORTIMENTO',
        facade='DESCR',
        name='Produto-Cor',
        name_plural='Produtos-Cores',
        sql='''
            SELECT
              i.CD_IT_PE_GRUPO || ' - ' || i.CD_IT_PE_ITEM SORTIMENTO
            , i.CD_IT_PE_GRUPO || ' - ' || i.CD_IT_PE_ITEM || ' - ' ||
              max( rtc.DESCRICAO_15 ) DESCR
            FROM PEDI_110 i -- item de pedido de venda
            JOIN BASI_010 rtc -- item (ref+tam+cor)
              on rtc.NIVEL_ESTRUTURA = i.CD_IT_PE_NIVEL99
             AND rtc.GRUPO_ESTRUTURA = i.CD_IT_PE_GRUPO
             AND rtc.SUBGRU_ESTRUTURA = i.CD_IT_PE_SUBGRUPO
             AND rtc.ITEM_ESTRUTURA = i.CD_IT_PE_ITEM
            WHERE i.PEDIDO_VENDA = %s
            GROUP BY
              i.CD_IT_PE_GRUPO
            , i.CD_IT_PE_ITEM
            ORDER BY
              2
        '''
        )

    # sortimento
    grade.value(
        id='QUANTIDADE',
        sql='''
            SELECT
              i.CD_IT_PE_GRUPO || ' - ' || i.CD_IT_PE_ITEM SORTIMENTO
            , i.CD_IT_PE_SUBGRUPO TAMANHO
            , i.QTDE_PEDIDA QUANTIDADE
            FROM PEDI_110 i -- item de pedido de venda
            WHERE i.PEDIDO_VENDA = %s
        '''
        )

    return (grade.table_data['header'], grade.table_data['fields'],
            grade.table_data['data'])


def ped_expedicao(
        cursor, dt_embarque='', pedido_tussor='', pedido_cliente='',
        cliente=''):

    filtro_dt_embarque = ''
    if dt_embarque is not None:
        filtro_dt_embarque = '''--
            AND ped.DATA_ENTR_VENDA = '{}' '''.format(dt_embarque)

    filtro_pedido_tussor = ''
    if pedido_tussor != '':
        filtro_pedido_tussor = '''--
            AND ped.PEDIDO_VENDA = '{}' '''.format(pedido_tussor)

    filtro_pedido_cliente = ''
    if pedido_cliente != '':
        filtro_pedido_cliente = '''--
            AND ped.COD_PED_CLIENTE = '{}' '''.format(pedido_cliente)

    filtro_cliente = ''
    if cliente != '':
        filtro_cliente = '''--
            AND c.NOME_CLIENTE
              || ' (' || lpad(c.CGC_9, 8, '0')
              || '/' || lpad(c.CGC_4, 4, '0')
              || '-' || lpad(c.CGC_2, 2, '0')
              || ')' like '%{}%' '''.format(cliente)

    sql = """
        SELECT
          ped.PEDIDO_VENDA
        , ped.DATA_EMIS_VENDA DT_EMISSAO
        , ped.DATA_PREV_RECEB DT_RECEBIMENTO
        , ped.DATA_ENTR_VENDA DT_EMBARQUE
        , ped.OBSERVACAO
        , c.NOME_CLIENTE
          || ' (' || lpad(c.CGC_9, 8, '0')
          || '/' || lpad(c.CGC_4, 4, '0')
          || '-' || lpad(c.CGC_2, 2, '0')
          || ')' CLIENTE
        , COALESCE(ped.COD_PED_CLIENTE, ' ') PEDIDO_CLIENTE
        , CASE ped.STATUS_PEDIDO
          WHEN 0 THEN '0-Digitado'
          WHEN 1 THEN '1-Financeiro'
          WHEN 2 THEN '2-Liberado Financeiro'
          WHEN 3 THEN '3-Faturamento'
          WHEN 4 THEN '4-A cancelar'
          WHEN 5 THEN '5-Cancelado'
          WHEN 9 THEN '9-Aberto na web'
          END STATUS_PEDIDO
        , CASE ped.SITUACAO_VENDA
          WHEN 0  THEN '0-Pedido liberado'
          WHEN 5  THEN '5-Pedido suspenso'
          WHEN 10 THEN '10-Faturado total'
          WHEN 15 THEN '15-Pedido com NF cancelada'
          END SITUACAO_VENDA
        , i.CD_IT_PE_GRUPO REF
        , i.CD_IT_PE_ITEM COR
        , i.CD_IT_PE_SUBGRUPO TAM
        , i.QTDE_PEDIDA QTD
        FROM PEDI_100 ped -- pedido de venda
        JOIN PEDI_110 i -- item de pedido de venda
          ON i.PEDIDO_VENDA = ped.PEDIDO_VENDA
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = i.CD_IT_PE_SUBGRUPO
        LEFT JOIN PEDI_010 c
          ON c.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND c.CGC_4 = ped.CLI_PED_CGC_CLI4
        WHERE 1=1
          {filtro_dt_embarque} -- filtro_dt_embarque
          {filtro_pedido_tussor} -- filtro_pedido_tussor
          {filtro_pedido_cliente} -- filtro_pedido_cliente
          {filtro_cliente} -- filtro_cliente
        ORDER BY
          ped.PEDIDO_VENDA DESC
        , i.CD_IT_PE_GRUPO
        , i.CD_IT_PE_ITEM
        , t.ORDEM_TAMANHO
    """.format(
        filtro_dt_embarque=filtro_dt_embarque,
        filtro_pedido_tussor=filtro_pedido_tussor,
        filtro_pedido_cliente=filtro_pedido_cliente,
        filtro_cliente=filtro_cliente,
    )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
