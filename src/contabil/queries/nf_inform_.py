from pprint import pprint

from utils.functions.models import rows_to_dict_list


def nf_inform(cursor, nf):
    sql = """
        SELECT
          f.BASE_ICMS VALOR
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
        FROM FATU_050 f -- fatura
        JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = f.CGC_9
         AND c.CGC_4 = f.CGC_4
        LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
          ON fe.NOTA_DEV = f.NUM_NOTA_FISCAL
         AND fe.SITUACAO_ENTRADA <> 2 -- não cancelada
        WHERE f.NUM_NOTA_FISCAL = %s
    """
    cursor.execute(sql, [nf])
    return rows_to_dict_list(cursor)
