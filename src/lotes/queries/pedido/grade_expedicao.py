from utils.functions.models.dictlist import dictlist


def grade_expedicao(
        cursor, embarque_de='', embarque_ate='',
        pedido_tussor='', pedido_cliente='',
        cliente='', deposito='-',
        emissao_de=None, emissao_ate=None, empresa=1,
        cancelamento='N', faturamento='N', colecao=None):

    filtro_embarque_de = ''
    if embarque_de is not None:
        filtro_embarque_de = f'''--
            AND ped.DATA_ENTR_VENDA >= '{embarque_de}' '''

    filtro_embarque_ate = ''
    if embarque_ate is not None:
        filtro_embarque_ate = f'''--
            AND ped.DATA_ENTR_VENDA <= '{embarque_ate}' '''

    filtro_emissao_de = ''
    if emissao_de is not None and emissao_de != '':
        filtro_emissao_de = f''' --
            AND ped.DATA_EMIS_VENDA >= '{emissao_de}' '''

    filtro_emissao_ate = ''
    if emissao_ate is not None and emissao_ate != '':
        filtro_emissao_ate = f''' --
            AND ped.DATA_EMIS_VENDA <= '{emissao_ate}' '''

    filtro_pedido_tussor = ''
    if pedido_tussor != '':
        filtro_pedido_tussor = f'''--
            AND ped.PEDIDO_VENDA = '{pedido_tussor}' '''

    filtro_pedido_cliente = ''
    if pedido_cliente != '':
        filtro_pedido_cliente = f'''--
            AND ped.COD_PED_CLIENTE like '%{pedido_cliente}%' '''

    filtro_cliente = ''
    if cliente != '':
        filtro_cliente = f'''--
            AND c.NOME_CLIENTE
              || ' (' || lpad(c.CGC_9, 8, '0')
              || '/' || lpad(c.CGC_4, 4, '0')
              || '-' || lpad(c.CGC_2, 2, '0')
              || ')' like '%{cliente}%' '''

    filtro_deposito = ''
    if deposito != '-':
        filtro_deposito = f'''--
            AND i.CODIGO_DEPOSITO = '{deposito}'
            '''

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
        filtro_cancelamento = "AND ped.STATUS_PEDIDO <> 5 -- não cancelado"
    elif cancelamento == 'C':
        filtro_cancelamento = "AND ped.STATUS_PEDIDO = 5 -- cancelado"

    filtro_colecao = ''
    if colecao is not None:
      filtro_colecao = f"AND r.COLECAO = {colecao}"

    sql = f"""
        SELECT
          i.CD_IT_PE_GRUPO REF
        , i.CD_IT_PE_ITEM COR
        , i.CD_IT_PE_SUBGRUPO TAM
        , sum(i.QTDE_PEDIDA) QTD
        FROM PEDI_100 ped -- pedido de venda
        LEFT JOIN FATU_050 f -- fatura
          ON f.PEDIDO_VENDA = ped.PEDIDO_VENDA
         AND f.NUMERO_CAIXA_ECF = 0
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
          i.CD_IT_PE_GRUPO
        , t.ORDEM_TAMANHO
        , i.CD_IT_PE_SUBGRUPO
        , i.CD_IT_PE_ITEM
        ORDER BY
          i.CD_IT_PE_GRUPO
        , t.ORDEM_TAMANHO
        , i.CD_IT_PE_ITEM
    """
    cursor.execute(sql)
    return dictlist(cursor)
