from pprint import pprint

from utils.functions.queries import debug_cursor_execute
from utils.functions.models.dictlist import dictlist


def ped_op(cursor, pedido):
    # OPs
    sql = f"""
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
        , CASE
            WHEN EXISTS (
              SELECT
                l.ORDEM_PRODUCAO
              FROM pcpc_040 l
              WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
                AND l.CODIGO_ESTAGIO = 15
            )
            THEN 1
            ELSE 0
          END TEM_15
        , ( SELECT
              count(*)
            FROM PCPT_020 ro -- cadastro de rolos
            LEFT JOIN PCPT_025 rc -- alocação de rolo para OP
              ON rc.CODIGO_ROLO = ro.CODIGO_ROLO
            where rc.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
          ) qtd_rolos_aloc
        FROM PCPC_020 o -- OP
        WHERE o.PEDIDO_VENDA = {pedido}
        ORDER BY
          o.ORDEM_PRINCIPAL
        , o.ORDEM_PRODUCAO
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
