from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute


def get_nfs_especiais(cursor):
    sql = f"""
        SELECT
          nfc.CODIGO_EMPRESA empr
        , nfc.NUM_NOTA_FISCAL nf
        , nfc.SERIE_NOTA_FISC serie
        , nfi.NIVEL_ESTRUTURA nivel
        , nfi.GRUPO_ESTRUTURA ref
        , nfi.SUBGRU_ESTRUTURA tam
        , nfi.ITEM_ESTRUTURA cor
        FROM FATU_050 nfc
        JOIN FATU_060 nfi
          ON nfi.CH_IT_NF_CD_EMPR = nfc.CODIGO_EMPRESA
         AND nfi.CH_IT_NF_NUM_NFIS = nfc.NUM_NOTA_FISCAL
         AND nfi.CH_IT_NF_SER_NFIS = nfc.SERIE_NOTA_FISC
        WHERE nfc.CODIGO_EMPRESA = 1
          AND nfi.NR_CAIXA = 1
          AND nfc.NUMERO_CAIXA_ECF = 1
        ORDER BY 
          nfc.NUM_NOTA_FISCAL
        , nfc.SERIE_NOTA_FISC
        , nfi.SEQ_ITEM_NFISC 
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
