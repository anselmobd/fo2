from utils.functions.models import rows_to_dict_list


def os_op(cursor, os):
    # Totais por OP
    sql = """
        SELECT
          l.ORDEM_PRODUCAO OP
        , count(l.ORDEM_CONFECCAO) LOTES
        , sum(
            CASE WHEN l.QTDE_A_PRODUZIR_PACOTE <> 0
            THEN l.QTDE_A_PRODUZIR_PACOTE
            ELSE --l.QTDE_PECAS_PROG
              QTDE_PECAS_PROD
            + QTDE_CONSERTO
            + QTDE_PECAS_2A
            + QTDE_PERDAS
            END
          ) QTD
        , o.PEDIDO_VENDA PEDIDO
        , COALESCE(ped.COD_PED_CLIENTE, '') PED_CLIENTE
        FROM pcpc_040 l -- lotes
        JOIN PCPC_020 o -- OP
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        LEFT JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = o.PEDIDO_VENDA
        WHERE l.NUMERO_ORDEM = %s
        GROUP BY
          l.ORDEM_PRODUCAO
        , o.PEDIDO_VENDA
        , ped.COD_PED_CLIENTE
    """
    cursor.execute(sql, [os])
    return rows_to_dict_list(cursor)
