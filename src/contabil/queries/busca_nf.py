from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def busca_nf(cursor, ref=None, cor=None, modelo=None):
    filtro_ref = ''
    if ref is not None and ref != '':
        filtro_ref = f"AND i.GRUPO_ESTRUTURA = '{ref}'"

    filtro_modelo = ''
    if modelo is not None and modelo != '':
        filtro_modelo = f'''--
            AND TRIM(LEADING '0' FROM
                     (REGEXP_REPLACE(i.GRUPO_ESTRUTURA,
                                     '^[abAB]?([^a-zA-Z]+)[a-zA-Z]*$', '\\1'
                                     ))) = '{modelo}' '''

    filtro_cor = ''
    if cor is not None and cor != '':
        filtro_cor = f"AND i.ITEM_ESTRUTURA = '{cor}'"

    sql = f"""
        SELECT
          i.CH_IT_NF_NUM_NFIS NF
        , i.NIVEL_ESTRUTURA NIVEL
        , i.GRUPO_ESTRUTURA REF
        , i.SUBGRU_ESTRUTURA TAM
        , tam.ORDEM_TAMANHO ORD_TAM
        , i.ITEM_ESTRUTURA COR
        , rtc.NARRATIVA 
        , i.QTDE_ITEM_FATUR QTD
        , i.VALOR_CONTABIL VALOR
        , i.PEDIDO_VENDA PEDIDO
        , f.DATA_EMISSAO DATA
        , c.NOME_CLIENTE
          || ' (' || lpad(c.CGC_9, 8, '0')
          || '/' || lpad(c.CGC_4, 4, '0')
          || '-' || lpad(c.CGC_2, 2, '0')
          || ')' AS CLIENTE
        FROM FATU_050 f -- fatura de saída
        JOIN FATU_060 i -- item de nf de saída
          ON i.ch_it_nf_cd_empr = f.codigo_empresa
         and i.ch_it_nf_num_nfis = f.num_nota_fiscal
         and i.ch_it_nf_ser_nfis = f.serie_nota_fisc
         AND i.NR_CAIXA = 0
        LEFT JOIN BASI_010 rtc
          ON rtc.NIVEL_ESTRUTURA = i.NIVEL_ESTRUTURA
         AND rtc.GRUPO_ESTRUTURA = i.GRUPO_ESTRUTURA
         AND rtc.SUBGRU_ESTRUTURA = i.SUBGRU_ESTRUTURA
         AND rtc.ITEM_ESTRUTURA = i.ITEM_ESTRUTURA
        JOIN BASI_220 tam
          ON tam.TAMANHO_REF = i.SUBGRU_ESTRUTURA
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = f.CGC_9
         AND c.CGC_4 = f.CGC_4
         AND c.CGC_2 = f.CGC_2
        JOIN estq_005 t
          ON t.CODIGO_TRANSACAO = i.TRANSACAO
        WHERE 1=1
          -- Tussor
          AND f.CODIGO_EMPRESA = 1
          -- o faturamento tem uma transação de venda
          AND t.TIPO_TRANSACAO = 'V'
          -- não cancelada
          AND f.COD_CANC_NFISC = 0
          -- produto fabricado
          AND i.NIVEL_ESTRUTURA = '1'
          -- filtros do form
          {filtro_ref} -- filtro_ref
          {filtro_modelo} -- filtro_modelo
          {filtro_cor} -- filtro_cor
        ORDER BY
          i.CH_IT_NF_NUM_NFIS DESC
        , i.GRUPO_ESTRUTURA
        , i.ITEM_ESTRUTURA
        , tam.ORDEM_TAMANHO
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
