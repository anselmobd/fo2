from pprint import pprint

from django.db import models

from fo2.models import rows_to_dict_list


def infadprod_pro_pedido(cursor, pedido):
    sql = '''
        SELECT
          p.PEDIDO_VENDA PEDIDO
        , c.NOME_CLIENTE
          || ' (' || lpad(c.CGC_9, 8, '0')
          || '/' || lpad(c.CGC_4, 4, '0')
          || '-' || lpad(c.CGC_2, 2, '0')
          || ')' CLIENTE
        , i.CD_IT_PE_NIVEL99 NIVEL
        , i.CD_IT_PE_GRUPO REF
        , i.CD_IT_PE_ITEM COR
        , i.CD_IT_PE_SUBGRUPO TAM
        , i.QTDE_PEDIDA QTD
        , i.VALOR_UNITARIO VALOR
        , coalesce( ip.REF_CLIENTE, '-') INFADPROD
        , coalesce( ip.DESCR_REF_CLIENTE, '-') DESCRCLI
        , coalesce( rtc.CODIGO_BARRAS, ' ') EAN
        , rtc.NARRATIVA
        FROM PEDI_100 p -- pedido de venda
        LEFT JOIN PEDI_010 c
          ON c.CGC_9 = p.CLI_PED_CGC_CLI9
         AND c.CGC_4 = p.CLI_PED_CGC_CLI4
        JOIN PEDI_110 i -- item de pedido de venda
          ON i.PEDIDO_VENDA = p.PEDIDO_VENDA
        JOIN BASI_010 rtc -- item (ref+tam+cor)
          on rtc.NIVEL_ESTRUTURA = i.CD_IT_PE_NIVEL99
         AND rtc.GRUPO_ESTRUTURA = i.CD_IT_PE_GRUPO
         AND rtc.SUBGRU_ESTRUTURA = i.CD_IT_PE_SUBGRUPO
         AND rtc.ITEM_ESTRUTURA = i.CD_IT_PE_ITEM
        LEFT JOIN ESTQ_400 ip -- item - informações por cliente
          ON ip.CLIENTE9 = CLI_PED_CGC_CLI9
         AND ip.CLIENTE4 = CLI_PED_CGC_CLI4
         AND ip.NIVEL_ESTRUTURA = i.CD_IT_PE_NIVEL99
         AND ip.GRUPO_ESTRUTURA = i.CD_IT_PE_GRUPO
         AND ip.SUBGRUPO_ESTRUTURA = i.CD_IT_PE_SUBGRUPO
         AND ip.ITEM_ESTRUTURA = i.CD_IT_PE_ITEM
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = i.CD_IT_PE_SUBGRUPO
        WHERE p.PEDIDO_VENDA = %s
        ORDER BY
          p.PEDIDO_VENDA
        , p.CLI_PED_CGC_CLI9
        , p.CLI_PED_CGC_CLI4
        , i.CD_IT_PE_NIVEL99
        , i.CD_IT_PE_GRUPO
        , i.CD_IT_PE_ITEM
        , t.ORDEM_TAMANHO
        , i.CD_IT_PE_SUBGRUPO
    '''
    cursor.execute(sql, [pedido])
    return rows_to_dict_list(cursor)


def reme_indu(
        cursor, op=None, os=None,
        dt_saida_de=None, dt_saida_ate=None, nf_saida=None,
        dt_entrada_de=None, dt_entrada_ate=None, nf_entrada=None,
        faccao=None, pedido=None, pedido_cliente=None, cliente=None,
        retorno=None, detalhe=None):

    op_filter = ''
    if op:
        op_filter = 'AND op.ordem_producao = {}'.format(op)

    os_filter = ''
    if os:
        os_filter = 'AND os.NUMERO_ORDEM = {}'.format(os)

    dt_saida_filter = ''
    pprint(dt_saida_de)
    if dt_saida_de:
        dt_saida_filter += """ --
            AND nf.DATA_EMISSAO >= '{}'
        """.format(dt_saida_de)
    if dt_saida_ate:
        dt_saida_filter += """ --
            AND nf.DATA_EMISSAO <= '{}'
        """.format(dt_saida_ate)

    nf_saida_filter = ''
    if nf_saida:
        nf_saida_filter = 'AND nf.NUM_NOTA_FISCAL = {}'.format(nf_saida)

    dt_entrada_filter = ''
    if dt_entrada_de:
        dt_entrada_filter += """ --
            AND nfec.DATA_EMISSAO >= '{}'
        """.format(dt_entrada_de)
    if dt_entrada_ate:
        dt_entrada_filter += """ --
            AND nfec.DATA_EMISSAO <= '{}'
        """.format(dt_entrada_ate)

    nf_entrada_filter = ''
    if nf_entrada:
        nf_entrada_filter = 'AND nfec.DOCUMENTO = {}'.format(nf_entrada)

    faccao_filter = ''
    if faccao:
        faccao_filter = """ --
            AND cind.NOME_CLIENTE
                || ' (' || lpad(cind.CGC_9, 8, '0')
                || '/' || lpad(cind.CGC_4, 4, '0')
                || '-' || lpad(cind.CGC_2, 2, '0')
                || ')' LIKE '%{}%'
        """.format(faccao)

    pedido_filter = ''
    if pedido:
        pedido_filter = 'AND op.PEDIDO_VENDA = {}'.format(pedido)

    pedido_cliente_filter = ''
    if pedido_cliente:
        pedido_cliente_filter = "AND ped.COD_PED_CLIENTE like '{}' ".format(
            pedido_cliente)

    cliente_filter = ''
    if cliente:
        cliente_filter = """ --
            AND c.NOME_CLIENTE
                || ' (' || lpad(c.CGC_9, 8, '0')
                || '/' || lpad(c.CGC_4, 4, '0')
                || '-' || lpad(c.CGC_2, 2, '0')
                || ')' LIKE '%{}%'
        """.format(cliente)

    retorno_filter = ''
    if retorno == 'S':
        retorno_filter = "AND nfec.DOCUMENTO is NULL"
    elif retorno == 'C':
        retorno_filter = "AND nfec.DOCUMENTO is NOT NULL"

    detalhe_select = ', NULL TAM'
    detalhe_join = ''
    detalhe_group = ''
    detalhe_order = ''
    if detalhe == 'T':
        detalhe_select = ', oo.PROCONF_SUBGRUPO TAM'
        detalhe_join = ''' --
            LEFT JOIN BASI_220 t -- tamanhos
              ON t.TAMANHO_REF = oo.PROCONF_SUBGRUPO
        '''
        detalhe_group = ''' --
            , t.ORDEM_TAMANHO
            , oo.PROCONF_SUBGRUPO
        '''
        detalhe_order = ', t.ORDEM_TAMANHO -- tam'

    sql = '''
        WITH op_os AS
        ( SELECT DISTINCT
            l.ORDEM_PRODUCAO
          , l.PROCONF_GRUPO
          , l.PROCONF_SUBGRUPO
          , l.PROCONF_ITEM
          , l.NUMERO_ORDEM
          FROM PCPC_040 l -- lote
        )
        SELECT
          oo.ORDEM_PRODUCAO OP
        , oo.PROCONF_GRUPO REF
        , oo.PROCONF_ITEM COR
        {detalhe_select} -- , oo.PROCONF_SUBGRUPO TAM
        , os.NUMERO_ORDEM OS
        , SUM(osi.QTDE_ENVIADA) QTD
        , nf.DATA_EMISSAO DT
        , nf.NUM_NOTA_FISCAL NF
        , cind.NOME_CLIENTE
          || ' (' || lpad(cind.CGC_9, 8, '0')
          || '/' || lpad(cind.CGC_4, 4, '0')
          || '-' || lpad(cind.CGC_2, 2, '0')
          || ')' FACCAO
        , nfec.DATA_EMISSAO DT_RET
        , nfec.DOCUMENTO NF_RET
        , sum(nfei.QUANTIDADE) QTD_RET
        , op.PEDIDO_VENDA PED
        , ped.COD_PED_CLIENTE PED_CLI
        , c.NOME_CLIENTE
          || ' (' || lpad(c.CGC_9, 8, '0')
          || '/' || lpad(c.CGC_4, 4, '0')
          || '-' || lpad(c.CGC_2, 2, '0')
          || ')' CLI
        FROM OBRF_080 os -- OS - capa
        JOIN op_os oo -- relação de OP com OS
          ON oo.NUMERO_ORDEM = os.NUMERO_ORDEM
        JOIN PCPC_020 op -- OP - capa
          ON op.ordem_producao = oo.ORDEM_PRODUCAO
        LEFT JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = op.PEDIDO_VENDA
        LEFT JOIN PEDI_010 c -- cliente - do pedido de venda
          ON c.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND c.CGC_4 = ped.CLI_PED_CGC_CLI4
        JOIN OBRF_082 osi -- OS - item de nota
          ON osi.NUMERO_ORDEM = os.NUMERO_ORDEM
         AND osi.PRODSAI_GRUPO = oo.PROCONF_GRUPO
         AND osi.PRODSAI_SUBGRUPO = oo.PROCONF_SUBGRUPO
         AND osi.PRODSAI_ITEM = oo.PROCONF_ITEM
        JOIN FATU_050 nf -- nota fiscal da Tussor - capa
          ON nf.NUM_NOTA_FISCAL = osi.NUM_NF_SAI
        LEFT JOIN PEDI_010 cind -- cliente - industrializador
          ON cind.CGC_9 = nf.CGC_9
         AND cind.CGC_4 = nf.CGC_4
        LEFT JOIN OBRF_015 nfei -- nota fiscal de entrada - item
          ON osi.NUM_NF_SAI <> 0
         AND nfei.NUM_NOTA_ORIG = osi.NUM_NF_SAI
         AND nfei.CODITEM_NIVEL99 = osi.PRODSAI_NIVEL99
         AND nfei.CODITEM_GRUPO = osi.PRODSAI_GRUPO
         AND nfei.CODITEM_SUBGRUPO = osi.PRODSAI_SUBGRUPO
         AND nfei.CODITEM_ITEM = osi.PRODSAI_ITEM
        LEFT JOIN OBRF_010 nfec -- nota fiscal de entrada - capa
          ON nfec.DOCUMENTO = nfei.CAPA_ENT_NRDOC
         AND nfec.CGC_CLI_FOR_9 = nfei.CAPA_ENT_FORCLI9
         AND nfec.CGC_CLI_FOR_4 = nfei.CAPA_ENT_FORCLI4
        --LEFT JOIN BASI_220 t -- tamanhos
        --  ON t.TAMANHO_REF = oo.PROCONF_SUBGRUPO
        {detalhe_join} -- detalhe_join
        WHERE 1=1
        --  AND op.ordem_producao = 3480 -- op
        {op_filter} -- op_filter
        --  AND os.NUMERO_ORDEM = 2170 -- os
        {os_filter} -- os_filter
        --  AND nf.DATA_EMISSAO = TO_DATE('19/03/2018','DD/MM/YYYY')
                                                         -- dt_saida
        {dt_saida_filter} -- dt_saida_filter
        --  AND nf.NUM_NOTA_FISCAL = 63422 -- nf_saida
        {nf_saida_filter} -- nf_saida_filter
        --  AND nfec.DATA_EMISSAO = TO_DATE('26/03/2018','DD/MM/YYYY')
                                                         -- dt_entrada
        {dt_entrada_filter} -- dt_entrada_filter
        --  AND nfec.DOCUMENTO = 54603 -- nf_entrada
        {nf_entrada_filter} -- nf_entrada_filter
        --  AND cind.NOME_CLIENTE
        --      || ' (' || lpad(cind.CGC_9, 8, '0')
        --      || '/' || lpad(cind.CGC_4, 4, '0')
        --      || '-' || lpad(cind.CGC_2, 2, '0')
        --      || ')' LIKE '%LAU%'  -- faccao
        {faccao_filter} -- faccao_filter
        --  AND op.PEDIDO_VENDA = 3472 -- pedido
        {pedido_filter} -- pedido_filter
        --  AND ped.COD_PED_CLIENTE like '2341494' -- pedido_cliente
        {pedido_cliente_filter} -- pedido_cliente_filter
        --  AND c.NOME_CLIENTE
        --      || ' (' || lpad(c.CGC_9, 8, '0')
        --      || '/' || lpad(c.CGC_4, 4, '0')
        --      || '-' || lpad(c.CGC_2, 2, '0')
        --      || ')' LIKE '%RENN%'  -- cliente
        {cliente_filter} -- cliente_filter
        {retorno_filter} -- retorno_filter
        GROUP BY
          oo.ORDEM_PRODUCAO
        , oo.PROCONF_GRUPO
        , oo.PROCONF_ITEM
        -- , t.ORDEM_TAMANHO
        -- , oo.PROCONF_SUBGRUPO
        {detalhe_group} -- detalhe_group
        , os.NUMERO_ORDEM
        , nf.DATA_EMISSAO
        , nf.NUM_NOTA_FISCAL
        , cind.NOME_CLIENTE
        , cind.CGC_9
        , cind.CGC_4
        , cind.CGC_2
        , nfec.DATA_EMISSAO
        , nfec.DOCUMENTO
        , op.PEDIDO_VENDA
        , ped.COD_PED_CLIENTE
        , c.NOME_CLIENTE
        , c.CGC_9
        , c.CGC_4
        , c.CGC_2
        ORDER BY
          oo.ORDEM_PRODUCAO -- op
        , os.NUMERO_ORDEM -- os
        , oo.PROCONF_GRUPO -- ref
        , oo.PROCONF_ITEM -- cor
        {detalhe_order} -- , t.ORDEM_TAMANHO -- tam
        , nf.DATA_EMISSAO -- data remessa
        , nf.NUM_NOTA_FISCAL -- nf remessa
        , nfec.DATA_EMISSAO -- data retorno
        , nfec.DOCUMENTO -- nf retorno
    '''.format(
        op_filter=op_filter,
        os_filter=os_filter,
        dt_saida_filter=dt_saida_filter,
        nf_saida_filter=nf_saida_filter,
        dt_entrada_filter=dt_entrada_filter,
        nf_entrada_filter=nf_entrada_filter,
        faccao_filter=faccao_filter,
        pedido_filter=pedido_filter,
        pedido_cliente_filter=pedido_cliente_filter,
        cliente_filter=cliente_filter,
        retorno_filter=retorno_filter,
        detalhe_select=detalhe_select,
        detalhe_join=detalhe_join,
        detalhe_group=detalhe_group,
        detalhe_order=detalhe_order,
        )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
