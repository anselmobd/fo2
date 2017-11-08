from fo2.models import rows_to_dict_list, GradeQtd

from lotes.models import *
from lotes.models.base import *


def ped_inform(cursor, pedido):
    # Informações sobre Pedido
    sql = """
        SELECT
          ped.PEDIDO_VENDA
        , ped.DATA_EMIS_VENDA DT_EMISSAO
        , ped.DATA_PREV_RECEB DT_RECEBIMENTO
        , c.NOME_CLIENTE
          || ' (' || lpad(c.CGC_9, 8, '0')
          || '/' || lpad(c.CGC_4, 4, '0')
          || '-' || lpad(c.CGC_2, 2, '0')
          || ')' CLIENTE
        , COALESCE(ped.COD_PED_CLIENTE, ' ') PEDIDO_CLIENTE
        , CASE ped.STATUS_PEDIDO
          WHEN 0 THEN '0-Digitado'
          WHEN 1 THEN '1-Financeiro'
          WHEN 2 THEN '2-Liberado Financeiro'
          WHEN 3 THEN '3-Faturamento'
          WHEN 4 THEN '4-A cancelar'
          WHEN 5 THEN '5-Cancelado'
          WHEN 9 THEN '9-Aberto na web'
          END STATUS_PEDIDO
        , CASE ped.SITUACAO_VENDA
          WHEN 0  THEN '0-Pedido liberado'
          WHEN 5  THEN '5-Pedido suspenso'
          WHEN 10 THEN '10-Faturado total'
          WHEN 15 THEN '15-Pedido com NF cancelada'
          END SITUACAO_VENDA
        FROM PEDI_100 ped -- pedido de venda
        LEFT JOIN PEDI_010 c
          ON c.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND c.CGC_4 = ped.CLI_PED_CGC_CLI4
        WHERE ped.PEDIDO_VENDA = %s
    """
    cursor.execute(sql, [pedido])
    return rows_to_dict_list(cursor)


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
        FROM PCPC_020 o -- OP
        WHERE o.PEDIDO_VENDA = %s
          AND o.SITUACAO <> 9
        ORDER BY
          o.ORDEM_PRINCIPAL
        , o.ORDEM_PRODUCAO
    """
    cursor.execute(sql, [pedido])
    return rows_to_dict_list(cursor)
