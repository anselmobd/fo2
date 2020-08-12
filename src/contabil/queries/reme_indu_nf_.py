from pprint import pprint

from utils.functions.models import rows_to_dict_list


def reme_indu_nf(
        cursor, op=None, os=None,
        dt_saida_de=None, dt_saida_ate=None, nf_saida=None,
        dt_entrada_de=None, dt_entrada_ate=None, nf_entrada=None,
        faccao=None, pedido=None, pedido_cliente=None, cliente=None,
        retorno=None, detalhe=None, situacao=None):

    op_filter = ''
    if op:
        op_filter = 'AND op.ordem_producao = {}'.format(op)

    os_filter = ''
    if os:
        os_filter = 'AND osi.NUMERO_ORDEM = {}'.format(os)

    dt_saida_filter = ''
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

    situacao_filter = ''
    if situacao == 'A':
        situacao_filter += """ --
            AND nf.SITUACAO_NFISC = 1
            AND fe.DOCUMENTO IS NULL
        """
    elif situacao == 'C':
        situacao_filter += """ --
            AND nf.SITUACAO_NFISC != 1
        """
    elif situacao == 'D':
        situacao_filter += """ --
            AND fe.DOCUMENTO IS NOT NULL
        """

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
                || '; ' || cind.FANTASIA_CLIENTE
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
                || '; ' || c.FANTASIA_CLIENTE
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

    sql = '''
        WITH remessa AS
        (
        SELECT
          nf.NUM_NOTA_FISCAL NF
        , nf.SITUACAO_NFISC SITUACAO
        , nf.DATA_EMISSAO DT
        , fe.DOCUMENTO NF_DEVOLUCAO
        , cind.FANTASIA_CLIENTE FACCAO'''
    if detalhe == 'I':
        sql += '''
            , inf.SEQ_ITEM_NFISC SEQ
            , inf.NIVEL_ESTRUTURA NIVEL
            , inf.GRUPO_ESTRUTURA REF
            , inf.SUBGRU_ESTRUTURA TAM
            , inf.ITEM_ESTRUTURA COR
            , sum(inf.QTDE_ITEM_FATUR) QTD'''
    sql += '''
        , min(osi.NUMERO_ORDEM) OS
        , min(l.ORDEM_PRODUCAO) OP
        , nfec.DOCUMENTO NF_RET
        , nfec.DATA_EMISSAO DT_RET'''
    if detalhe == 'I':
        sql += '''
            , sum(nfei.QUANTIDADE) QTD_RET'''
    sql += '''
        FROM FATU_050 nf -- nota fiscal da Tussor - capa
        LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
          ON fe.NOTA_DEV = nf.NUM_NOTA_FISCAL
         AND fe.SITUACAO_ENTRADA = 1 -- ativa
        JOIN PEDI_080 nop -- natureza da operação
          ON nop.NATUR_OPERACAO = nf.NATOP_NF_NAT_OPER
         AND nop.ESTADO_NATOPER = nf.NATOP_NF_EST_OPER
        JOIN PEDI_010 cind -- cliente - industrializador
          ON cind.CGC_9 = nf.CGC_9
         AND cind.CGC_4 = nf.CGC_4
        JOIN FATU_060 inf -- nota fiscal da Tussor - capa
          ON inf.CH_IT_NF_NUM_NFIS = nf.NUM_NOTA_FISCAL
        LEFT JOIN OBRF_082 osi -- OS - item de OS
          ON osi.NUM_NF_SAI = nf.NUM_NOTA_FISCAL
         AND osi.PRODSAI_GRUPO = inf.GRUPO_ESTRUTURA
         AND osi.PRODSAI_SUBGRUPO = inf.SUBGRU_ESTRUTURA
         AND osi.PRODSAI_ITEM = inf.ITEM_ESTRUTURA
        LEFT JOIN PCPC_040 l -- lote
          ON l.NUMERO_ORDEM = osi.NUMERO_ORDEM
         AND (l.PERIODO_PRODUCAO, l.ORDEM_CONFECCAO) IN
          ( SELECT
              ll.PERIODO_PRODUCAO
            , ll.ORDEM_CONFECCAO
            FROM PCPC_040 ll
            WHERE ll.NUMERO_ORDEM = osi.NUMERO_ORDEM
              AND rownum = 1
          )
        LEFT JOIN OBRF_015 nfei -- nota fiscal de entrada - item
          ON nfei.NUM_NOTA_ORIG = nf.NUM_NOTA_FISCAL
         AND nfei.CODITEM_NIVEL99 = inf.NIVEL_ESTRUTURA
         AND nfei.CODITEM_GRUPO = inf.GRUPO_ESTRUTURA
         AND nfei.CODITEM_SUBGRUPO = inf.SUBGRU_ESTRUTURA
         AND nfei.CODITEM_ITEM = inf.ITEM_ESTRUTURA
        LEFT JOIN OBRF_010 nfec -- nota fiscal de entrada - capa
          ON nfec.DOCUMENTO = nfei.CAPA_ENT_NRDOC
         AND nfec.CGC_CLI_FOR_9 = nfei.CAPA_ENT_FORCLI9
         AND nfec.CGC_CLI_FOR_4 = nfei.CAPA_ENT_FORCLI4
         AND nfec.CGC_CLI_FOR_2 = nfei.CAPA_ENT_FORCLI2
        WHERE 1=1
          AND nop.COD_NATUREZA in ('5.90', '6.90')
          AND nop.DIVISAO_NATUR = 1
          {nf_saida_filter} -- nf_saida_filter
          --AND nf.DATA_EMISSAO >= TO_DATE('2018-10-08','YYYY-MM-DD')
          --AND nf.DATA_EMISSAO <= TO_DATE('2018-10-08','YYYY-MM-DD')
          {dt_saida_filter} -- dt_saida_filter
          -- AND cind.FANTASIA_CLIENTE LIKE '%LUIMAR%'
          {faccao_filter} -- faccao_filter
          {os_filter} -- os_filter
          {retorno_filter} -- retorno_filter
          {situacao_filter} -- situacao_filter
          {dt_entrada_filter} -- dt_entrada_filter
          {nf_entrada_filter} -- nf_entrada_filter
        GROUP BY
          nf.NUM_NOTA_FISCAL
        , nf.SITUACAO_NFISC
        , nf.DATA_EMISSAO
        , fe.DOCUMENTO
        , cind.FANTASIA_CLIENTE'''
    if detalhe == 'I':
        sql += '''
            , inf.SEQ_ITEM_NFISC
            , inf.NIVEL_ESTRUTURA
            , inf.GRUPO_ESTRUTURA
            , inf.SUBGRU_ESTRUTURA
            , inf.ITEM_ESTRUTURA'''
    sql += '''
        , nfec.DOCUMENTO
        , nfec.DATA_EMISSAO
        )
        SELECT
          r.*
        , CASE WHEN op.PEDIDO_VENDA = 0 THEN NULL
          ELSE op.PEDIDO_VENDA END PED
        , ped.COD_PED_CLIENTE PED_CLI
        , c.FANTASIA_CLIENTE CLI
        FROM remessa r
        LEFT JOIN PCPC_020 op -- OP - capa
          ON op.ordem_producao = r.OP
        LEFT JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = op.PEDIDO_VENDA
        LEFT JOIN PEDI_010 c -- cliente - do pedido de venda
          ON c.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND c.CGC_4 = ped.CLI_PED_CGC_CLI4
        WHERE 1=1
          {op_filter} -- op_filter
          {pedido_filter} -- pedido_filter
          {pedido_cliente_filter} -- pedido_cliente_filter
          {cliente_filter} -- cliente_filter
        ORDER BY
          r.NF'''
    if detalhe == 'I':
        sql += '''
            , r.SEQ'''
    sql += '''
        , r.NF_RET
    '''
    sql = sql.format(
        op_filter=op_filter,
        os_filter=os_filter,
        dt_saida_filter=dt_saida_filter,
        nf_saida_filter=nf_saida_filter,
        situacao_filter=situacao_filter,
        dt_entrada_filter=dt_entrada_filter,
        nf_entrada_filter=nf_entrada_filter,
        faccao_filter=faccao_filter,
        pedido_filter=pedido_filter,
        pedido_cliente_filter=pedido_cliente_filter,
        cliente_filter=cliente_filter,
        retorno_filter=retorno_filter,
        )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
