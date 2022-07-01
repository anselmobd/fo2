from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(cursor):
    sql = f"""
        SELECT
          mf.DES_MENSAG_2
        , mf.DES_MENSAG_12
        , mf.NUM_NOTA
        , mf.COD_SERIE_NOTA 
        , f.DATA_EMISSAO 
        , f.VALOR_ITENS_NFIS 
        FROM FATU_052 mf -- mensagem faturamento
        JOIN FATU_050 f -- capa faturamento
          ON f.NUM_NOTA_FISCAL = mf.NUM_NOTA
        WHERE 1=1
        --  AND mf.NUM_NOTA = 98769
          AND mf.COD_EMPRESA = 1 -- Tussor Matriz
          AND mf.DES_MENSAG_1 LIKE '%TRANSFERENCIA%'
          AND mf.DES_MENSAG_1 LIKE '%ROLOS%'
          AND mf.DES_MENSAG_2 LIKE '%FORNECEDOR%'
          AND mf.DES_MENSAG_12 NOT LIKE 'Transf. Matriz-Filial da NF%'
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
