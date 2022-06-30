from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(cursor, nf, empresa):       
    sql = f"""
        SELECT DISTINCT  
          infe.CODITEM_NIVEL99 niv
        , infe.CODITEM_GRUPO ref
        , infe.CODITEM_SUBGRUPO tam
        , infe.CODITEM_ITEM cor
        , infe.QUANTIDADE qtd
        FROM OBRF_010 cnfe -- capa de nota de entrada
        LEFT JOIN OBRF_015 infe -- item de nota de entrada
          ON infe.CAPA_ENT_FORCLI9 = cnfe.CGC_CLI_FOR_9
         AND infe.CAPA_ENT_FORCLI4 = cnfe.CGC_CLI_FOR_4
         AND infe.CAPA_ENT_FORCLI2 = cnfe.CGC_CLI_FOR_2
         AND infe.CAPA_ENT_NRDOC = cnfe.DOCUMENTO
         AND infe.CAPA_ENT_SERIE = cnfe.SERIE
        WHERE 1=1
          AND cnfe.LOCAL_ENTREGA = {empresa} -- empresa 1: matriz
          AND cnfe.DOCUMENTO = {nf}
        ORDER BY 
          infe.CODITEM_NIVEL99
        , infe.CODITEM_GRUPO
        , infe.CODITEM_SUBGRUPO
        , infe.CODITEM_ITEM
    """
    debug_cursor_execute(cursor, sql)
    data = dictlist_lower(cursor)
    for row in data:
        row['item'] = f"{row['niv']}.{row['ref']}.{row['tam']}.{row['cor']}"
    return data
