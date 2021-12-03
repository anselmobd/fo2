from utils.functions.models import rows_to_dict_list


def ped_expedicao(
        cursor, embarque_de='', embarque_ate='',
        pedido_tussor='', pedido_cliente='',
        cliente='', deposito='-', detalhe='r',
        emissao_de=None, emissao_ate=None, empresa=1,
        cancelamento='N', faturamento='N'):

    filtro_embarque_de = ''
    if embarque_de is not None:
        filtro_embarque_de = ''' --
            AND ped.DATA_ENTR_VENDA >= DATE '{}' '''.format(embarque_de)

    filtro_embarque_ate = ''
    if embarque_ate is not None:
        filtro_embarque_ate = ''' --
            AND ped.DATA_ENTR_VENDA <= DATE '{}' '''.format(embarque_ate)

    filtro_emissao_de = ''
    if emissao_de is not None and emissao_de != '':
        filtro_emissao_de = ''' --
            AND ped.DATA_EMIS_VENDA >= DATE '{}' '''.format(emissao_de)

    filtro_emissao_ate = ''
    if emissao_ate is not None and emissao_ate != '':
        filtro_emissao_ate = ''' --
            AND ped.DATA_EMIS_VENDA <= DATE '{}' '''.format(emissao_ate)

    filtro_pedido_tussor = ''
    if pedido_tussor != '':
        filtro_pedido_tussor = ''' --
            AND ped.PEDIDO_VENDA = '{}' '''.format(pedido_tussor)

    filtro_pedido_cliente = ''
    if pedido_cliente != '':
        filtro_pedido_cliente = ''' --
            AND ped.COD_PED_CLIENTE like '%{}%' '''.format(pedido_cliente)

    filtro_cliente = ''
    if cliente != '':
        filtro_cliente = ''' --
            AND c.NOME_CLIENTE
              || ' (' || lpad(c.CGC_9, 8, '0')
              || '/' || lpad(c.CGC_4, 4, '0')
              || '-' || lpad(c.CGC_2, 2, '0')
              || ')' like '%{}%' '''.format(cliente)

    filtro_deposito = ''
    if deposito != '-':
        filtro_deposito = ''' --
            AND i.CODIGO_DEPOSITO = '{}'
            '''.format(deposito)

    filtro_faturamento = ''
    if faturamento == 'N':
        filtro_faturamento = "AND f.NUM_NOTA_FISCAL IS NULL"
    elif faturamento == 'F':
        filtro_faturamento = "AND f.NUM_NOTA_FISCAL IS NOT NULL"

    filtro_cancelamento = ''
    if cancelamento == 'N':
        filtro_cancelamento = "AND ped.STATUS_PEDIDO <> 5 -- não cancelado"
    elif cancelamento == 'C':
        filtro_cancelamento = "AND ped.STATUS_PEDIDO = 5 -- cancelado"

    sql = ""
    if detalhe == 'p':
        sql += f""" --
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
            WHERE p.CODIGO_EMPRESA = {empresa}
            GROUP BY
              p.PEDIDO_VENDA
            )"""
    sql += """ --
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
        , i.CODIGO_DEPOSITO DEPOSITO"""
    if detalhe in ('r', 'c'):
        sql += """ --
            , i.CD_IT_PE_GRUPO REF """
    if detalhe == 'c':
        sql += """ --
            , i.CD_IT_PE_ITEM COR
            , i.CD_IT_PE_SUBGRUPO TAM"""
    sql += """ --
        , sum(i.QTDE_PEDIDA) QTD"""
    if detalhe == 'p':
        sql += """ --
            , CASE WHEN cg.PEDIDO_VENDA IS NULL THEN 'N'
              ELSE 'S' END GTIN_OK"""
    sql += """ --
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
         AND c.CGC_2 = ped.CLI_PED_CGC_CLI2
    """
    if detalhe == 'p':
        sql += """ --
            LEFT JOIN conta_gtin cg
              ON cg.PEDIDO_VENDA = ped.PEDIDO_VENDA
             AND cg.MIN_GTIN = 1
             AND cg.MAX_GTIN = 1"""
    sql += f"""
        WHERE 1=1
          AND ped.CODIGO_EMPRESA = {empresa}
          {filtro_embarque_de} -- filtro_embarque_de
          {filtro_embarque_ate} -- filtro_embarque_ate
          {filtro_emissao_de} -- filtro_emissao_de
          {filtro_emissao_ate} -- filtro_emissao_ate
          {filtro_pedido_tussor} -- filtro_pedido_tussor
          {filtro_pedido_cliente} -- filtro_pedido_cliente
          {filtro_cliente} -- filtro_cliente
          {filtro_deposito} -- filtro_deposito
          {filtro_faturamento} -- filtro_faturamento
          {filtro_cancelamento} -- filtro_cancelamento
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
        , i.CODIGO_DEPOSITO"""
    if detalhe in ('r', 'c'):
        sql += """ --
            , i.CD_IT_PE_GRUPO"""
    if detalhe == 'c':
        sql += """ --
            , i.CD_IT_PE_ITEM
            , t.ORDEM_TAMANHO
            , i.CD_IT_PE_SUBGRUPO"""
    if detalhe == 'p':
        sql += """ --
            , cg.PEDIDO_VENDA"""
    sql += """ --
        ORDER BY
          ped.DATA_ENTR_VENDA DESC
        , ped.PEDIDO_VENDA DESC"""
    if detalhe in ('r', 'c'):
        sql += """ --
            , i.CD_IT_PE_GRUPO"""
    if detalhe == 'c':
        sql += """ --
            , i.CD_IT_PE_ITEM
            , t.ORDEM_TAMANHO"""
    if detalhe == 'o':
        sql = f"""
          WITH sele AS
          ( {sql}
          )
          select
            s.*
          , p.OBSERVACAO
          from sele s
          JOIN PEDI_100 p -- pedido de venda
            ON p.PEDIDO_VENDA = s.PEDIDO_VENDA
        """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
