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
          nfc.NUM_NOTA_FISCAL DESC
        , nfc.SERIE_NOTA_FISC DESC
        , nfi.SEQ_ITEM_NFISC
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def set_nf_especial(cursor, nf):
    """Marca NF e itens como especiais
    Recebe: cursor e número da NF
    Retorna: Se sucesso, None, senão, mensagem de erro
    """

    sql = f"""
        UPDATE FATU_050 nfc
        SET
          nfc.NUMERO_CAIXA_ECF = 1
        WHERE nfc.CODIGO_EMPRESA = 1
          AND nfc.NUM_NOTA_FISCAL = {nf}
          AND nfc.SERIE_NOTA_FISC = 1
          AND nfc.NUMERO_CAIXA_ECF <> 1
    """
    try:
        debug_cursor_execute(cursor, sql)
    except Exception as e:
        return repr(e)

    sql = f"""
        UPDATE FATU_060 nfi
        SET
          nfi.NR_CAIXA = 1
        WHERE nfi.CH_IT_NF_CD_EMPR = 1
          AND nfi.CH_IT_NF_NUM_NFIS = {nf}
          AND nfi.CH_IT_NF_SER_NFIS = 1
          AND nfi.NR_CAIXA <> 1
    """
    try:
        debug_cursor_execute(cursor, sql)
    except Exception as e:
        return repr(e)
