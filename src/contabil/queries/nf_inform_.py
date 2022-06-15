from pprint import pprint

from utils.functions.models import custom_dictlist
from utils.functions.queries import debug_cursor_execute


def nf_inform(cursor, nf, especiais=False, empresa=1):
    filtra_especial = "" if especiais else "AND f.NUMERO_CAIXA_ECF = 0"
    filtra_empresa = f"AND f.CODIGO_EMPRESA = {empresa}"
    sql = f"""
        SELECT
          f.BASE_ICMS VALOR
        , f.CODIGO_EMPRESA  
        , f.QTDE_EMBALAGENS VOLUMES
        , f.DATA_AUTORIZACAO_NFE DATA
        , CAST( COALESCE( '0' || f.COD_STATUS, '0' ) AS INT )
          COD_STATUS
        , COALESCE( f.MSG_STATUS, ' ' ) MSG_STATUS
        , f.SITUACAO_NFISC SITUACAO
        , f.NATOP_NF_NAT_OPER NAT
        , f.NATOP_NF_EST_OPER UF
        , fe.DOCUMENTO NF_DEVOLUCAO
        , c.NOME_CLIENTE
          || ' (' || lpad(c.CGC_9, 8, '0')
          || '/' || lpad(c.CGC_4, 4, '0')
          || '-' || lpad(c.CGC_2, 2, '0')
          || ')' CLIENTE
        , f.NUMERO_CAIXA_ECF especial
        FROM FATU_050 f -- fatura
        JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = f.CGC_9
         AND c.CGC_4 = f.CGC_4
        LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
          ON fe.NOTA_DEV = f.NUM_NOTA_FISCAL
         AND fe.SITUACAO_ENTRADA <> 2 -- não cancelada
        WHERE f.NUM_NOTA_FISCAL = {nf}
          {filtra_empresa} -- filtra_empresa
          {filtra_especial} -- filtra_especial
    """
    debug_cursor_execute(cursor, sql)
    return custom_dictlist(cursor)
