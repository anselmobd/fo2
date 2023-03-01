from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor, data_de=None, data_ate=None):
    """Lista OPs com alguma movimentação no estágio 15
    na data ou período informado
    """

    if not data_ate:
        data_ate = data_de

    data_de_value = (
        f"DATE '{data_de}'"
    ) if data_de else 'NULL'

    data_ate_value = (
        f"DATE '{data_ate}'"
    ) if data_ate else 'NULL'

    sql = f'''
        WITH
          filtro AS 
        (
          SELECT 
            15 EST
          , {data_de_value} DT_DE 
          , {data_ate_value} DT_ATE 
          FROM dual 
          WHERE {data_de_value} IS NOT NULL
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
          GROUP BY 
            l.ORDEM_PRODUCAO
        )
        --SELECT * FROM op_com_15;
        , op_dt_move AS 
        -- Para as OPs selecionas acima, conta quantos lotes tem movimento
        -- na data indicada no filtro e devolve apenas OPs com essa quantidade
        -- diferente de zero, lista também a data em questão
        (
          SELECT DISTINCT 
            MAX(ml.DATA_PRODUCAO) DT_CORTE
          , op15.op
          , op15.lotes
          , filtro.DT_DE
          , filtro.DT_ATE
          , COUNT(DISTINCT ml.PCPC040_PERCONF*100000+ml.PCPC040_ORDCONF) CORTADOS
          FROM filtro, op_com_15 op15, pcpc_045 ml
          WHERE ml.ORDEM_PRODUCAO = op15.OP
            AND ml.PCPC040_ESTCONF = filtro.EST
            AND ml.DATA_PRODUCAO >= filtro.DT_DE
            AND ml.DATA_PRODUCAO <= filtro.DT_ATE
          HAVING
            SUM(COALESCE(ml.QTDE_PRODUZIDA, 0)) > 0
          GROUP BY 
            op15.op
          , op15.lotes
          , filtro.DT_DE
          , filtro.DT_ATE
          ORDER BY 
            1 DESC  -- DT_CORTE
          , op15.op DESC
        )
        SELECT * FROM op_dt_move
    '''
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    return dados
