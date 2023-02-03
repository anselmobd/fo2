from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor, data=None):
    data_value = (
        f"DATE '{data}'"
    ) if data else 'NULL'

    sql = f'''
        WITH
          filtro AS 
        (
          SELECT 
            15 EST
          , {data_value} DT 
          FROM dual 
          WHERE {data_value} IS NOT NULL
        )
        , op_com_15 AS 
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
        (
          SELECT DISTINCT 
            op15.op
          , op15.lotes
          , filtro.dt
          , COUNT(DISTINCT ml.PCPC040_PERCONF*100000+ml.PCPC040_ORDCONF) move_LOTES
          FROM filtro, op_com_15 op15, pcpc_045 ml
          WHERE ml.ORDEM_PRODUCAO = op15.OP
            AND ml.PCPC040_ESTCONF = filtro.EST
            AND ml.DATA_PRODUCAO = filtro.DT
          HAVING
            SUM(COALESCE(ml.QTDE_PRODUZIDA, 0)) > 0
          GROUP BY 
            op15.op
          , op15.lotes
          , filtro.dt
        )
        SELECT * FROM op_dt_move
    '''
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    return dados
