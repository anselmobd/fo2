from pprint import pprint

from utils.functions.models import rows_to_dict_list


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
          ON i.ch_it_nf_cd_empr = f.codigo_empresa
         and i.ch_it_nf_num_nfis = f.num_nota_fiscal
         and i.ch_it_nf_ser_nfis = f.serie_nota_fisc
         AND i.NR_CAIXA = 0
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
