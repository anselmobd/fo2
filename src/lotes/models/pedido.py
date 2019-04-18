from fo2.models import rows_to_dict_list, GradeQtd

from lotes.models import *
from lotes.models.base import *


def ped_inform(cursor, pedido):
    # Informações sobre Pedido
    sql = """
        SELECT
          ped.PEDIDO_VENDA
        , COALESCE(
            ( SELECT
                LISTAGG(i.CODIGO_DEPOSITO, ', ')
                WITHIN GROUP (ORDER BY i.CODIGO_DEPOSITO)
              FROM (
                SELECT DISTINCT
                  ii.CODIGO_DEPOSITO
                , ii.PEDIDO_VENDA
                FROM PEDI_110 ii
              ) i
              WHERE i.PEDIDO_VENDA = ped.PEDIDO_VENDA
            )
          , ' '
          ) DEPOSITO
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
        cursor, embarque_de='', embarque_ate='',
        pedido_tussor='', pedido_cliente='',
        cliente='', deposito='-', detalhe='r'):

    filtro_embarque_de = ''
    if embarque_de is not None:
        filtro_embarque_de = '''--
            AND ped.DATA_ENTR_VENDA >= '{}' '''.format(embarque_de)

    filtro_embarque_ate = ''
    if embarque_ate is not None:
        filtro_embarque_ate = '''--
            AND ped.DATA_ENTR_VENDA <= '{}' '''.format(embarque_ate)

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

    filtro_deposito = ''
    if deposito != '-':
        filtro_deposito = '''--
            AND i.CODIGO_DEPOSITO = '{}'
            '''.format(deposito)

    sql = ""
    if detalhe == 'p':
        sql += """
            WITH conta_gtin AS
            (
            SELECT
              p.PEDIDO_VENDA
            , MIN(
              CASE WHEN rtc.CODIGO_BARRAS IS NULL
                     OR rtc.CODIGO_BARRAS = 'SEM GTIN'
              THEN 0
              ELSE (
                SELECT count(*)
                FROM BASI_010 gtin
                WHERE gtin.CODIGO_BARRAS = rtc.CODIGO_BARRAS
              )
              END
              ) MIN_GTIN
            , MAX(
              CASE WHEN rtc.CODIGO_BARRAS IS NULL
                     OR rtc.CODIGO_BARRAS = 'SEM GTIN'
              THEN 0
              ELSE (
                SELECT count(*)
                FROM BASI_010 gtin
                WHERE gtin.CODIGO_BARRAS = rtc.CODIGO_BARRAS
              )
              END
              ) MAX_GTIN
            FROM PEDI_100 p -- pedido de venda
            JOIN PEDI_110 i -- item de pedido de venda
              ON i.PEDIDO_VENDA = p.PEDIDO_VENDA
            JOIN BASI_010 rtc -- item (ref+tam+cor)
              on rtc.NIVEL_ESTRUTURA = i.CD_IT_PE_NIVEL99
             AND rtc.GRUPO_ESTRUTURA = i.CD_IT_PE_GRUPO
             AND rtc.SUBGRU_ESTRUTURA = i.CD_IT_PE_SUBGRUPO
             AND rtc.ITEM_ESTRUTURA = i.CD_IT_PE_ITEM
            GROUP BY
              p.PEDIDO_VENDA
            )
        """
    sql += """
        SELECT
          ped.PEDIDO_VENDA
        , ped.DATA_EMIS_VENDA DT_EMISSAO
        , ped.DATA_PREV_RECEB DT_RECEBIMENTO
        , ped.DATA_ENTR_VENDA DT_EMBARQUE
        , c.NOME_CLIENTE
          || ' (' || lpad(c.CGC_9, 8, '0')
          || '/' || lpad(c.CGC_4, 4, '0')
          || '-' || lpad(c.CGC_2, 2, '0')
          || ')' CLIENTE
        , COALESCE(ped.COD_PED_CLIENTE, ' ') PEDIDO_CLIENTE
        , i.CODIGO_DEPOSITO DEPOSITO
    """
    if detalhe in ('r', 'c'):
        sql += """
            , i.CD_IT_PE_GRUPO REF
        """
    if detalhe == 'c':
        sql += """
            , i.CD_IT_PE_ITEM COR
            , i.CD_IT_PE_SUBGRUPO TAM
        """
    sql += """
        , sum(i.QTDE_PEDIDA) QTD
    """
    if detalhe == 'p':
        sql += """
            , CASE WHEN cg.PEDIDO_VENDA IS NULL THEN 'N'
              ELSE 'S' END GTIN_OK
        """
    sql += """
        FROM PEDI_100 ped -- pedido de venda
        LEFT JOIN FATU_050 f -- fatura
          ON f.PEDIDO_VENDA = ped.PEDIDO_VENDA
        JOIN PEDI_110 i -- item de pedido de venda
          ON i.PEDIDO_VENDA = ped.PEDIDO_VENDA
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = i.CD_IT_PE_SUBGRUPO
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND c.CGC_4 = ped.CLI_PED_CGC_CLI4
        """
    if detalhe == 'p':
        sql += """
            LEFT JOIN conta_gtin cg
              ON cg.PEDIDO_VENDA = ped.PEDIDO_VENDA
             AND cg.MIN_GTIN = 1
             AND cg.MAX_GTIN = 1
        """
    sql += """
        WHERE ped.STATUS_PEDIDO <> 5 -- não cancelado
          AND f.NUM_NOTA_FISCAL IS NULL
          {filtro_embarque_de} -- filtro_embarque_de
          {filtro_embarque_ate} -- filtro_embarque_ate
          {filtro_pedido_tussor} -- filtro_pedido_tussor
          {filtro_pedido_cliente} -- filtro_pedido_cliente
          {filtro_cliente} -- filtro_cliente
          {filtro_deposito} -- filtro_deposito
        GROUP BY
          ped.PEDIDO_VENDA
        , ped.DATA_EMIS_VENDA
        , ped.DATA_PREV_RECEB
        , ped.DATA_ENTR_VENDA
        , c.NOME_CLIENTE
        , c.CGC_9
        , c.CGC_4
        , c.CGC_2
        , ped.COD_PED_CLIENTE
        , i.CODIGO_DEPOSITO
    """
    if detalhe in ('r', 'c'):
        sql += """
            , i.CD_IT_PE_GRUPO
        """
    if detalhe == 'c':
        sql += """
            , i.CD_IT_PE_ITEM
            , t.ORDEM_TAMANHO
            , i.CD_IT_PE_SUBGRUPO
        """
    if detalhe == 'p':
        sql += """
            , cg.PEDIDO_VENDA
        """
    sql += """
        ORDER BY
          ped.DATA_ENTR_VENDA DESC
        , ped.PEDIDO_VENDA DESC
    """
    if detalhe in ('r', 'c'):
        sql += """
            , i.CD_IT_PE_GRUPO
        """
    if detalhe == 'c':
        sql += """
            , i.CD_IT_PE_ITEM
            , t.ORDEM_TAMANHO
        """
    sql = sql.format(
        filtro_embarque_de=filtro_embarque_de,
        filtro_embarque_ate=filtro_embarque_ate,
        filtro_pedido_tussor=filtro_pedido_tussor,
        filtro_pedido_cliente=filtro_pedido_cliente,
        filtro_cliente=filtro_cliente,
        filtro_deposito=filtro_deposito,
    )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def ped_dep_qtd(cursor, pedido):
    # quantidade por depósito
    sql = """
        SELECT
          i.CODIGO_DEPOSITO DEPOSITO
        , sum(i.QTDE_PEDIDA) QTD
        FROM PEDI_110 i
        WHERE i.PEDIDO_VENDA = %s
        GROUP BY
          i.CODIGO_DEPOSITO
        ORDER BY
          i.CODIGO_DEPOSITO
    """
    cursor.execute(sql, [pedido])
    return rows_to_dict_list(cursor)


def grade_expedicao(
        cursor, embarque_de='', embarque_ate='',
        pedido_tussor='', pedido_cliente='',
        cliente='', deposito='-'):

    filtro_embarque_de = ''
    if embarque_de is not None:
        filtro_embarque_de = '''--
            AND ped.DATA_ENTR_VENDA >= '{}' '''.format(embarque_de)

    filtro_embarque_ate = ''
    if embarque_ate is not None:
        filtro_embarque_ate = '''--
            AND ped.DATA_ENTR_VENDA <= '{}' '''.format(embarque_ate)

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

    filtro_deposito = ''
    if deposito != '-':
        filtro_deposito = '''--
            AND i.CODIGO_DEPOSITO = '{}'
            '''.format(deposito)

    sql = """
        SELECT
          i.CD_IT_PE_GRUPO REF
        , i.CD_IT_PE_ITEM COR
        , i.CD_IT_PE_SUBGRUPO TAM
        , sum(i.QTDE_PEDIDA) QTD
        FROM PEDI_100 ped -- pedido de venda
        LEFT JOIN FATU_050 f -- fatura
          ON f.PEDIDO_VENDA = ped.PEDIDO_VENDA
        JOIN PEDI_110 i -- item de pedido de venda
          ON i.PEDIDO_VENDA = ped.PEDIDO_VENDA
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = i.CD_IT_PE_SUBGRUPO
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND c.CGC_4 = ped.CLI_PED_CGC_CLI4
        WHERE ped.STATUS_PEDIDO <> 5 -- não cancelado
          AND f.NUM_NOTA_FISCAL IS NULL
          {filtro_embarque_de} -- filtro_embarque_de
          {filtro_embarque_ate} -- filtro_embarque_ate
          {filtro_pedido_tussor} -- filtro_pedido_tussor
          {filtro_pedido_cliente} -- filtro_pedido_cliente
          {filtro_cliente} -- filtro_cliente
          {filtro_deposito} -- filtro_deposito
        GROUP BY
          i.CD_IT_PE_GRUPO
        , t.ORDEM_TAMANHO
        , i.CD_IT_PE_SUBGRUPO
        , i.CD_IT_PE_ITEM
        ORDER BY
          i.CD_IT_PE_GRUPO
        , t.ORDEM_TAMANHO
        , i.CD_IT_PE_ITEM
    """
    sql = sql.format(
        filtro_embarque_de=filtro_embarque_de,
        filtro_embarque_ate=filtro_embarque_ate,
        filtro_pedido_tussor=filtro_pedido_tussor,
        filtro_pedido_cliente=filtro_pedido_cliente,
        filtro_cliente=filtro_cliente,
        filtro_deposito=filtro_deposito,
    )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
