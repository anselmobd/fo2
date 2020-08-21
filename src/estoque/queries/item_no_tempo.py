import datetime

from utils.functions.models import rows_to_dict_list_lower


def item_no_tempo(
        cursor, ref, tam, cor, deposito, apartirde):

    filtro_ref = ''
    if ref is not None and ref != '':
        filtro_ref = "AND t.GRUPO_ESTRUTURA = '{ref}'".format(ref=ref)

    filtro_tam = ''
    if tam is not None and tam != '':
        filtro_tam = "AND t.SUBGRUPO_ESTRUTURA = '{tam}'".format(tam=tam)

    filtro_cor = ''
    if cor is not None and cor != '':
        filtro_cor = "AND t.ITEM_ESTRUTURA = '{cor}'".format(cor=cor)

    filtro_deposito = ''
    if deposito is not None and deposito != '':
        filtro_deposito = "AND t.CODIGO_DEPOSITO = '{deposito}'".format(
            deposito=deposito)

    filtro_apartirde = ''
    if apartirde is not None:
        str_apartirde = apartirde.strftime("TIMESTAMP '%Y-%m-%d 00:00:00'")
        filtro_apartirde = f"AND t.DATA_INSERCAO > {str_apartirde}"

    sql = f'''
        WITH query AS
        (
        SELECT
          t.DATA_INSERCAO DATA
        , CASE WHEN t.ENTRADA_SAIDA = 'S' THEN
            -t.QUANTIDADE
          ELSE t.QUANTIDADE
          END QTD_SINAL
        , t.ENTRADA_SAIDA ES
        , t.QUANTIDADE QTD
        , t.NUMERO_DOCUMENTO DOC
        , t.PROCESSO_SYSTEXTIL PROC
        , t.CODIGO_TRANSACAO TRANS
        , tr.DESCRICAO TRANS_DESCR
        , t.USUARIO_SYSTEXTIL USUARIO
        , CASE WHEN t.CNPJ_9 = 0
            THEN ped.PEDIDO_VENDA
            ELSE
              CASE WHEN f.PEDIDO_VENDA IS NULL
                THEN
                  ( SELECT
                      min(inf.PEDIDO_VENDA)
                    FROM fatu_060 inf -- item de nf de saída
                    WHERE inf.CH_IT_NF_NUM_NFIS = f.NUM_NOTA_FISCAL
                  )
                ELSE f.PEDIDO_VENDA
              END
          END PED
        , CASE WHEN cp.CGC_9 IS NULL
            THEN t.CNPJ_9
            ELSE cp.CGC_9
          END CNPJ_9
        , CASE WHEN cp.CGC_4 IS NULL
            THEN t.CNPJ_4
            ELSE cp.CGC_4
          END CNPJ_4
        , CASE WHEN cp.CGC_2 IS NULL
            THEN t.CNPJ_2
            ELSE cp.CGC_2
          END CNPJ_2
        , CASE WHEN cp.NOME_CLIENTE IS NULL
            THEN c.NOME_CLIENTE
            ELSE cp.NOME_CLIENTE
          END CLIENTE
        , CASE WHEN cp.FANTASIA_CLIENTE IS NULL
            THEN c.FANTASIA_CLIENTE
            ELSE cp.FANTASIA_CLIENTE
          END FANTASIA
        FROM ESTQ_300_ESTQ_310 t
        LEFT JOIN ESTQ_005 tr -- transacao
          ON tr.CODIGO_TRANSACAO = t.CODIGO_TRANSACAO
        LEFT JOIN FATU_050 f -- fatura
          ON t.CNPJ_9 <> 0
         AND f.NUM_NOTA_FISCAL = t.NUMERO_DOCUMENTO
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = t.CNPJ_9
         AND c.CGC_4 = t.CNPJ_4
        LEFT JOIN PCPC_020 op -- OP
          ON t.CNPJ_9 = 0
         AND op.ORDEM_PRODUCAO = t.NUMERO_DOCUMENTO
        LEFT JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = op.PEDIDO_VENDA
        LEFT JOIN PEDI_010 cp -- cliente
          ON cp.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND cp.CGC_4 = ped.CLI_PED_CGC_CLI4
        WHERE t.NIVEL_ESTRUTURA = 1
          {filtro_deposito} -- AND t.CODIGO_DEPOSITO = 101
          {filtro_ref} -- AND t.GRUPO_ESTRUTURA = '02156'
          {filtro_tam} -- AND t.SUBGRUPO_ESTRUTURA = 'P'
          {filtro_cor} -- AND t.ITEM_ESTRUTURA = '0000BR'
          {filtro_apartirde} -- filtro_apartirde
        )
        SELECT
          q.*
        , ped.STATUS_PEDIDO STAT_PED
        , CASE ped.STATUS_PEDIDO
          WHEN 0 THEN '0-Digitado'
          WHEN 1 THEN '1-Financeiro'
          WHEN 2 THEN '2-Liberado Financeiro'
          WHEN 3 THEN '3-Faturamento'
          WHEN 4 THEN '4-A cancelar'
          WHEN 5 THEN '5-Cancelado'
          WHEN 9 THEN '9-Aberto na web'
          ELSE ''
          END DESCR_STAT_PED
        FROM query q
        LEFT JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = q.PED
        ORDER BY
          q.DATA DESC
    '''
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
