from pprint import pprint

from utils.functions.models import rows_to_dict_list


def ped_inform(cursor, pedido):
    # Informações sobre Pedido
    sql = """
        SELECT
          ped.PEDIDO_VENDA
        , COALESCE(
            ( SELECT
                LISTAGG(i.CODIGO_DEPOSITO, ', ')
                WITHIN GROUP (ORDER BY i.CODIGO_DEPOSITO)
              FROM (
                SELECT DISTINCT
                  ii.CODIGO_DEPOSITO
                , ii.PEDIDO_VENDA
                FROM PEDI_110 ii
              ) i
              WHERE i.PEDIDO_VENDA = ped.PEDIDO_VENDA
            )
          , ' '
          ) DEPOSITO
        , ped.DATA_EMIS_VENDA DT_EMISSAO
        , ped.DATA_PREV_RECEB DT_RECEBIMENTO
        , ped.DATA_ENTR_VENDA DT_EMBARQUE
        , ped.OBSERVACAO
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
         AND c.CGC_2 = ped.CLI_PED_CGC_CLI2
        WHERE ped.PEDIDO_VENDA = %s
    """
    cursor.execute(sql, [pedido])
    return rows_to_dict_list(cursor)
