from utils.functions.models import rows_to_dict_list


def ped_nf(cursor, pedido):
    sql = """
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
        FROM FATU_050 f
        LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
          ON fe.NOTA_DEV = f.NUM_NOTA_FISCAL
         AND fe.SITUACAO_ENTRADA <> 2 -- não cancelada
        WHERE f.PEDIDO_VENDA = %s
        ORDER BY
          f.NUM_NOTA_FISCAL
    """
    cursor.execute(sql, [pedido])
    return rows_to_dict_list(cursor)
