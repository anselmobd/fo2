from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def nf_itens(cursor, nf, especiais=False, empresa=1):
    filtra_especial = "" if especiais else "AND i.NR_CAIXA = 0"
    filtra_empresa = f"AND f.CODIGO_EMPRESA = {empresa}"
    sql = f"""
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
        , f.CODIGO_EMPRESA  
        FROM FATU_050 f -- fatura de saída
        JOIN fatu_060 i -- item de nf de saída
          ON i.ch_it_nf_cd_empr = f.codigo_empresa
         and i.ch_it_nf_num_nfis = f.num_nota_fiscal
         and i.ch_it_nf_ser_nfis = f.serie_nota_fisc
         {filtra_especial} -- filtra_especial
        LEFT JOIN basi_010 rtc
          ON rtc.NIVEL_ESTRUTURA = i.NIVEL_ESTRUTURA
         AND rtc.GRUPO_ESTRUTURA = i.GRUPO_ESTRUTURA
         AND rtc.SUBGRU_ESTRUTURA = i.SUBGRU_ESTRUTURA
         AND rtc.ITEM_ESTRUTURA = i.ITEM_ESTRUTURA
        WHERE f.NUM_NOTA_FISCAL = {nf}
        {filtra_empresa} -- filtra_empresa
        ORDER BY
          i.SEQ_ITEM_NFISC
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
