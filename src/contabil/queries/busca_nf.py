from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def busca_nf(cursor, ref):
    sql = f"""
        SELECT
          i.CH_IT_NF_NUM_NFIS NF
        , i.NIVEL_ESTRUTURA NIVEL
        , i.GRUPO_ESTRUTURA REF
        , i.SUBGRU_ESTRUTURA TAM
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
          ON i.CH_IT_NF_NUM_NFIS = f.NUM_NOTA_FISCAL
        LEFT JOIN BASI_010 rtc
          ON rtc.NIVEL_ESTRUTURA = i.NIVEL_ESTRUTURA
         AND rtc.GRUPO_ESTRUTURA = i.GRUPO_ESTRUTURA
         AND rtc.SUBGRU_ESTRUTURA = i.SUBGRU_ESTRUTURA
         AND rtc.ITEM_ESTRUTURA = i.ITEM_ESTRUTURA
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = f.CGC_9
         AND c.CGC_4 = f.CGC_4
         AND c.CGC_2 = f.CGC_2
        WHERE 1=1
          AND i.GRUPO_ESTRUTURA = '{ref}'
        ORDER BY
          i.CH_IT_NF_NUM_NFIS DESC
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
