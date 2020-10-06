from pprint import pprint

from utils.functions.models import rows_to_dict_list


def ped_op(cursor, pedido):
    # OPs
    sql = """
        SELECT
          o.PEDIDO_VENDA
        , o.ORDEM_PRODUCAO
        , CASE
          when o.REFERENCIA_PECA <= '99999' then 'PA'
          when o.REFERENCIA_PECA <= 'B9999' then 'PG'
          when o.REFERENCIA_PECA >= 'Z0000' then 'MP'
          else 'MD'
          END TIPO
        , o.REFERENCIA_PECA
        , o.ORDEM_PRINCIPAL
        , ( SELECT
              SUM( l.QTDE_PECAS_PROG )
            FROM pcpc_040 l
            WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
              AND l.SEQ_OPERACAO = (
                SELECT
                  MAX( ls.SEQ_OPERACAO )
                FROM pcpc_040 ls
                WHERE ls.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
              )
          ) QTD
        , o.DATA_PROGRAMACAO DT_DIGITACAO
        , o.DATA_ENTRADA_CORTE DT_CORTE
        , o.SITUACAO
        FROM PCPC_020 o -- OP
        WHERE o.PEDIDO_VENDA = %s
        ORDER BY
          o.ORDEM_PRINCIPAL
        , o.ORDEM_PRODUCAO
    """
    cursor.execute(sql, [pedido])
    return rows_to_dict_list(cursor)
