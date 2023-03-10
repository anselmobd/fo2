from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor, data_de=None, data_ate=None, op1=None):
    """Lista OPs com alguma movimentação no estágio 15
    na data ou período informado
    """

    if not any([data_de, data_ate, op1]):
        return []

    if not data_ate:
        data_ate = data_de

    data_de_value = (
        f"DATE '{data_de}'"
    ) if data_de else 'NULL'

    data_ate_value = (
        f"DATE '{data_ate}'"
    ) if data_ate else 'NULL'

    op1_value = (
        f"{op1}"
    ) if op1 else 'NULL'

    sql = f'''
        WITH
          filtro AS
        (
          SELECT
            15 EST
          , {data_de_value} DT_DE
          , {data_ate_value} DT_ATE
          , {op1_value} OP1
          FROM dual
        )
        , op_com_15 AS
        -- seleciona OPs com estágio indicado no filtro e
        -- conta o total de lotes por OP
        (
          SELECT DISTINCT
            l.ORDEM_PRODUCAO OP
          , COUNT(*) lotes
          FROM filtro, pcpc_040 l
          WHERE l.CODIGO_ESTAGIO = filtro.EST
            AND (filtro.OP1 IS NULL OR l.ORDEM_PRODUCAO = filtro.OP1)
          GROUP BY
            l.ORDEM_PRODUCAO
        )
        --SELECT * FROM op_com_15;
        , op_corte_dt AS
        -- Para as OPs selecionas acima, conta quantos lotes tem corte
        -- no período de datas indicado no filtro e devolve apenas OPs com
        -- essa quantidade diferente de zero, lista também as datas em questão
        (
          SELECT DISTINCT
            MAX(ml.DATA_PRODUCAO) DT_CORTE
          , op15.op
          , op15.lotes
          , fi.DT_DE
          , fi.DT_ATE
          , COUNT(DISTINCT ml.PCPC040_PERCONF*100000+ml.PCPC040_ORDCONF) cortados_periodo
          FROM op_com_15 op15
          JOIN filtro fi
            ON 1=1
          JOIN pcpc_045 ml
            ON ml.ORDEM_PRODUCAO = op15.OP
           AND ml.PCPC040_ESTCONF = fi.EST
           AND (fi.DT_DE IS NULL OR ml.DATA_PRODUCAO >= fi.DT_DE)
           AND (fi.DT_ATE IS NULL OR ml.DATA_PRODUCAO <= fi.DT_ATE)
          HAVING
            SUM(COALESCE(ml.QTDE_PRODUZIDA, 0)) > 0
          GROUP BY
            op15.op
          , op15.lotes
          , fi.DT_DE
          , fi.DT_ATE
          ORDER BY
            1 DESC  -- DT_CORTE
          , op15.op DESC
        )
        SELECT
          ocdt.*
        , ( SELECT
              COUNT(*)
            FROM filtro fi
            JOIN pcpc_040 l
              ON l.ORDEM_PRODUCAO = ocdt.OP
             AND l.CODIGO_ESTAGIO = fi.EST
            WHERE l.QTDE_PECAS_PROD > 0
          ) cortados
        , op.REFERENCIA_PECA REF
        , op.PEDIDO_VENDA ped
        , ped.COD_PED_CLIENTE PED_CLI
        , CASE WHEN c.NOME_CLIENTE IS NULL THEN
            NULL
          ELSE
            c.NOME_CLIENTE
            || ' (' || lpad(c.CGC_9, 8, '0')
            || '/' || lpad(c.CGC_4, 4, '0')
            || '-' || lpad(c.CGC_2, 2, '0')
            || ')'
          END CLI
        FROM op_corte_dt ocdt
        JOIN pcpc_020 op
          ON op.ORDEM_PRODUCAO = ocdt.OP
        LEFT JOIN PEDI_100 ped -- pedido de venda
          ON op.PEDIDO_VENDA > 0
         AND ped.PEDIDO_VENDA = op.PEDIDO_VENDA
        LEFT JOIN PEDI_010 c -- cliente - do pedido de venda
          ON op.PEDIDO_VENDA > 0
         AND c.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND c.CGC_4 = ped.CLI_PED_CGC_CLI4
         AND c.CGC_2 = ped.CLI_PED_CGC_CLI2
        ORDER BY
            ocdt.DT_CORTE DESC
          , ocdt.op DESC
    '''
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    return dados
