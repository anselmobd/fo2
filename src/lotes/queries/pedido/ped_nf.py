from pprint import pprint

from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute


def ped_nf(cursor, pedido, especiais=False, empresa=1):
    filtra_especial = "" if especiais else "AND f.NUMERO_CAIXA_ECF = 0"
    filtra_empresa = f"AND f.CODIGO_EMPRESA = {empresa}"
    sql = f"""
        SELECT
          f.NUM_NOTA_FISCAL NF
        , f.BASE_ICMS VALOR
        , f.QTDE_EMBALAGENS VOLUMES
        , f.DATA_AUTORIZACAO_NFE DATA
        , CAST( COALESCE( '0' || f.COD_STATUS, '0' ) AS INT )
          COD_STATUS
        , COALESCE( f.MSG_STATUS, ' ' ) MSG_STATUS
        , f.SITUACAO_NFISC SITUACAO
        , f.NATOP_NF_NAT_OPER NAT
        , f.NATOP_NF_EST_OPER UF
        , fe.DOCUMENTO NF_DEVOLUCAO
        , f.CODIGO_EMPRESA
        FROM FATU_050 f
        LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
          ON fe.NOTA_DEV = f.NUM_NOTA_FISCAL
         AND fe.SITUACAO_ENTRADA <> 2 -- não cancelada
        WHERE f.PEDIDO_VENDA = {pedido}
          {filtra_empresa} -- filtra_empresa
          {filtra_especial} -- filtra_especial
        ORDER BY
          f.NUM_NOTA_FISCAL
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
