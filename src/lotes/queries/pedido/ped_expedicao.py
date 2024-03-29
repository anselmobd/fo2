from pprint import pprint

from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute


def ped_expedicao(
        cursor, embarque_de='', embarque_ate='',
        pedido_tussor='', pedido_cliente='',
        cliente='', deposito='-', detalhe='r',
        emissao_de=None, emissao_ate=None, empresa=1,
        cancelamento='N', faturamento='N', colecao=None):

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
        filtro_faturamento = """--
          AND ( f.NUM_NOTA_FISCAL IS NULL -- não tem NF
              OR fe.SITUACAO_ENTRADA IS NOT NULL -- existente devolução da NF
              )
          AND ( fg.NUM_NOTA_FISCAL IS NULL -- não tem NF Gavi
              OR feg.SITUACAO_ENTRADA IS NOT NULL -- existente devolução da NF da Gavi
              )
        """
    elif faturamento == 'F':
        filtro_faturamento = """--
          AND ( ( f.NUM_NOTA_FISCAL IS NOT NULL -- tem NF
                AND fe.SITUACAO_ENTRADA IS NULL -- não existente devolução da NF
                )
                OR
                ( fg.NUM_NOTA_FISCAL IS NOT NULL -- tem NF Gavi
                AND feg.SITUACAO_ENTRADA IS NULL -- não existente devolução da NF da Gavi
                )
              )
        """

    filtro_cancelamento = ''
    if cancelamento == 'N':
        # filtro_cancelamento = "AND ped.STATUS_PEDIDO <> 5 -- não cancelado"
        filtro_cancelamento = "AND ped.COD_CANCELAMENTO = 0 -- não cancelado"
    elif cancelamento == 'C':
        # filtro_cancelamento = "AND ped.STATUS_PEDIDO = 5 -- cancelado"
        filtro_cancelamento = "AND ped.COD_CANCELAMENTO <> 0 -- cancelado"

    filtro_colecao = ''
    if colecao is not None:
      filtro_colecao = f"AND r.COLECAO = {colecao}"

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
          ped.CODIGO_EMPRESA EMPRESA
        , ped.PEDIDO_VENDA
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
        , sum(i.QTDE_PEDIDA) QTD
        , sum(i.QTDE_PEDIDA * i.VALOR_UNITARIO) VALOR """
    if detalhe == 'p':
        sql += """ --
            , CASE WHEN cg.PEDIDO_VENDA IS NULL THEN 'Não'
              ELSE 'Sim' END GTIN_OK"""
    sql += """ --
        FROM PEDI_100 ped -- pedido de venda
        LEFT JOIN FATU_050 f -- fatura
          ON f.PEDIDO_VENDA = ped.PEDIDO_VENDA
         -- AND f.NUMERO_CAIXA_ECF = 0
         AND f.SITUACAO_NFISC = 1 -- ativa
         AND CAST( COALESCE( '0' || f.COD_STATUS, '0' ) AS INT ) = 100 -- ativa
        LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução de fatura
          ON fe.NOTA_DEV = f.NUM_NOTA_FISCAL
         AND fe.SITUACAO_ENTRADA <> 2 -- não cancelada 
        LEFT JOIN PEDI_100 pedg -- pedido Gavi
          ON pedg.PEDIDO_ORIGEM = ped.PEDIDO_VENDA
         AND pedg.CODIGO_EMPRESA = 4 -- Gavi
         AND pedg.COD_CANCELAMENTO = 0
        LEFT JOIN FATU_050 fg -- fatura Gavi
          ON fg.PEDIDO_VENDA = pedg.PEDIDO_VENDA
         AND fg.SITUACAO_NFISC = 1 -- ativa
         AND CAST( COALESCE( '0' || fg.COD_STATUS, '0' ) AS INT ) = 100 -- ativa
        LEFT JOIN OBRF_010 feg -- nota fiscal de entrada/devolução de fatura Gavi
          ON feg.NOTA_DEV = fg.NUM_NOTA_FISCAL
         AND feg.SITUACAO_ENTRADA <> 2 -- não cancelada 
        JOIN PEDI_110 i -- item de pedido de venda
          ON i.PEDIDO_VENDA = ped.PEDIDO_VENDA
        JOIN BASI_030 r -- ref
          on r.NIVEL_ESTRUTURA = i.CD_IT_PE_NIVEL99
         AND r.REFERENCIA = i.CD_IT_PE_GRUPO
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
    sql += f"""--
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
          {filtro_colecao} -- filtro_colecao
        GROUP BY
          ped.CODIGO_EMPRESA
        , ped.PEDIDO_VENDA
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
          , ( SELECT
                max(i.AGRUPADOR_PRODUCAO)
              FROM PEDI_110 i -- item de pedido de venda
              WHERE i.PEDIDO_VENDA = s.PEDIDO_VENDA
            ) AGRUPADOR
          from sele s
          JOIN PEDI_100 p -- pedido de venda
            ON p.PEDIDO_VENDA = s.PEDIDO_VENDA
        """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
