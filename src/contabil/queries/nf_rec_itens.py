from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def query(cursor,
    empresa=None,
    cnpj=None,
    nf=None,
    nf_ser=None,
):       
    filtra_empresa = f"""--
        AND cnfe.LOCAL_ENTREGA = {empresa}
    """ if empresa else ''
    filtra_cnpj9 = f"""--
        AND cnfe.CGC_CLI_FOR_9 = {cnpj[:8]}
    """ if cnpj and len(cnpj) >= 8 else ''
    filtra_cnpj4 = f"""--
        AND cnfe.CGC_CLI_FOR_4 = {cnpj[8:12]}
    """ if cnpj and len(cnpj) >= 12 else ''
    filtra_cnpj2 = f"""--
        AND cnfe.CGC_CLI_FOR_2 = {cnpj[12:14]}
    """ if cnpj and len(cnpj) >= 14 else ''
    filtra_nf = f"""--
        AND cnfe.DOCUMENTO = {nf}
    """ if nf else ''
    filtra_nf_ser = f"""--
        AND cnfe.SERIE = {nf_ser}
    """ if nf_ser else ''
    sql = f"""
        SELECT DISTINCT  
          infe.CODITEM_NIVEL99 niv
        , infe.CODITEM_GRUPO ref
        , infe.CODITEM_SUBGRUPO tam
        , infe.CODITEM_ITEM cor
        , infe.QUANTIDADE qtd
        , infe.VALOR_UNITARIO preco
        , infe.VALOR_TOTAL valor
        FROM OBRF_010 cnfe -- capa de nota de entrada
        LEFT JOIN OBRF_015 infe -- item de nota de entrada
          ON infe.CAPA_ENT_FORCLI9 = cnfe.CGC_CLI_FOR_9
         AND infe.CAPA_ENT_FORCLI4 = cnfe.CGC_CLI_FOR_4
         AND infe.CAPA_ENT_FORCLI2 = cnfe.CGC_CLI_FOR_2
         AND infe.CAPA_ENT_NRDOC = cnfe.DOCUMENTO
         AND infe.CAPA_ENT_SERIE = cnfe.SERIE
        WHERE 1=1
          {filtra_empresa} -- filtra_empresa
          {filtra_cnpj9} -- filtra_cnpj9
          {filtra_cnpj4} -- filtra_cnpj4
          {filtra_cnpj2} -- filtra_cnpj2
          {filtra_nf} -- filtra_nf
          {filtra_nf_ser} -- filtra_nf_ser
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
