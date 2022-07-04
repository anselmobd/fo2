from pprint import pprint

from utils.functions.queries import debug_cursor_execute

__all__ = ['query']


def update(
    cursor,
    empresa=None,
    cnpj=None,
    nf=None,
    nf_ser=None,
    nf_env=None,
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
        UPDATE OBRF_010 cnfe -- capa de nota de entrada
        SET
          cnfe.TUSSOR_ENVIA_NF = {nf_env}
        WHERE 1=1
          {filtra_empresa} -- filtra_empresa
          {filtra_cnpj9} -- filtra_cnpj9
          {filtra_cnpj4} -- filtra_cnpj4
          {filtra_cnpj2} -- filtra_cnpj2
          {filtra_nf} -- filtra_nf
          {filtra_nf_ser} -- filtra_nf_ser
    """
    try:
        debug_cursor_execute(cursor, sql)
        return True
    except Exception:
        return False
