from pprint import pprint

from utils.models import rows_to_dict_list


def nf_itens(cursor, nf):
    sql = """
        SELECT
          i.SEQ_ITEM_NFISC
        , i.NIVEL_ESTRUTURA
        , i.GRUPO_ESTRUTURA
        , i.SUBGRU_ESTRUTURA
        , i.ITEM_ESTRUTURA
        , i.QTDE_ITEM_FATUR
        , i.VALOR_CONTABIL
        , i.PEDIDO_VENDA
        , rtc.NARRATIVA
        FROM FATU_050 f -- fatura de saída
        JOIN fatu_060 i -- item de nf de saída
          ON i.CH_IT_NF_NUM_NFIS = f.NUM_NOTA_FISCAL
        LEFT JOIN basi_010 rtc
          ON rtc.NIVEL_ESTRUTURA = i.NIVEL_ESTRUTURA
         AND rtc.GRUPO_ESTRUTURA = i.GRUPO_ESTRUTURA
         AND rtc.SUBGRU_ESTRUTURA = i.SUBGRU_ESTRUTURA
         AND rtc.ITEM_ESTRUTURA = i.ITEM_ESTRUTURA
        WHERE f.NUM_NOTA_FISCAL = %s
        ORDER BY
          i.SEQ_ITEM_NFISC
    """
    cursor.execute(sql, [nf])
    return rows_to_dict_list(cursor)
