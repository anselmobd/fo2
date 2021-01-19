from utils.functions.models import rows_to_dict_list


def grade_expedicao(
        cursor, embarque_de='', embarque_ate='',
        pedido_tussor='', pedido_cliente='',
        cliente='', deposito='-',
        emissao_de=None, emissao_ate=None, empresa=1):

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

    sql = f"""
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
         AND c.CGC_2 = ped.CLI_PED_CGC_CLI2
        WHERE ped.STATUS_PEDIDO <> 5 -- não cancelado
          AND ped.CODIGO_EMPRESA = {empresa}
          AND f.NUM_NOTA_FISCAL IS NULL
          {filtro_embarque_de} -- filtro_embarque_de
          {filtro_embarque_ate} -- filtro_embarque_ate
          {filtro_emissao_de} -- filtro_emissao_de
          {filtro_emissao_ate} -- filtro_emissao_ate
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
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
