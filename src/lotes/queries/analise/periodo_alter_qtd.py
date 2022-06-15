from pprint import pprint

from utils.functions.models.dictlist import dictlist
from utils.functions.queries import sql_where_none_if


def periodo_alter_qtd(cursor, periodo_de, periodo_ate, alternativa):
    """
    Calcula produção por periodo e alternativa

    Parameters
    ----------
    cursor :
        cursor de execução em banco de dados conectado
    periodo_de :
        periodo inicial
    periodo_ate :
        periodo final
    alternativa :
        anternativa de produção

    Returns
    -------
    list of dict
        Dados estruturados resultantes da execução da query
    """

    filtro_alternativa = sql_where_none_if(
        'o.ALTERNATIVA_PECA', alternativa, '')

    sql = f"""
        SELECT
          pp.PERIODO_PRODUCAO PERIODO
        , p.DATA_INI_PERIODO PERIODO_INI
        , p.DATA_FIM_PERIODO PERIODO_FIM
        , pp.ALTERNATIVA_PECA || '/' || pp.ROTEIRO_PECA ALT
        , pp.TIPO_ORDEM
        , CASE
          WHEN pp.TIPO_ORDEM = 3 THEN 'MD'
          WHEN pp.TIPO_ORDEM = 1 THEN 'PA'
          ELSE 'PG'
          END TIPO
        , pp.DATA_ENTRADA_CORTE DATA_CORTE
        , CASE WHEN pp.DATA_ENTRADA_CORTE = (CURRENT_DATE - 100000) THEN 1
          ELSE 2
          END ORDEM_TOTAL
        , SUM( l.QTDE_PECAS_PROG ) QTD
        , COUNT(DISTINCT o.ORDEM_PRODUCAO) NUM_OPS
        FROM
        (
        SELECT distinct
          l.PERIODO_PRODUCAO
        , o.ALTERNATIVA_PECA
        , o.ROTEIRO_PECA
        , CASE
          WHEN l.PROCONF_GRUPO <= '99999' THEN 3
          WHEN l.PROCONF_GRUPO > 'B9999' THEN 1
          ELSE 2
          END TIPO_ORDEM
        , CURRENT_DATE - 100000 DATA_ENTRADA_CORTE
        FROM pcpc_040 l
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        WHERE l.PROCONF_NIVEL99 = 1
          AND o.SITUACAO IN (2, 4)
          AND l.PERIODO_PRODUCAO >= '{periodo_de}'
          AND l.PERIODO_PRODUCAO <= '{periodo_ate}'
          {filtro_alternativa} -- filtro_alternativa
        UNION
        SELECT distinct
          l.PERIODO_PRODUCAO
        , o.ALTERNATIVA_PECA
        , o.ROTEIRO_PECA
        , CASE
          WHEN l.PROCONF_GRUPO <= '99999' THEN 3
          WHEN l.PROCONF_GRUPO > 'B9999' THEN 1
          ELSE 2
          END TIPO_ORDEM
        , o.DATA_ENTRADA_CORTE
        FROM pcpc_040 l
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        WHERE l.PROCONF_NIVEL99 = 1
          AND o.SITUACAO IN (2, 4)
          AND l.PERIODO_PRODUCAO >= '{periodo_de}'
          AND l.PERIODO_PRODUCAO <= '{periodo_ate}'
          {filtro_alternativa} -- filtro_alternativa
        ) pp
        JOIN pcpc_040 l
          ON l.PERIODO_PRODUCAO = pp.PERIODO_PRODUCAO
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        JOIN PCPC_010 p
          ON p.AREA_PERIODO = 1
         AND p.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
        WHERE l.PROCONF_NIVEL99 = 1
          AND o.SITUACAO IN (2, 4)
          AND o.ALTERNATIVA_PECA = pp.ALTERNATIVA_PECA
          AND o.ROTEIRO_PECA = pp.ROTEIRO_PECA
          AND (  ( pp.TIPO_ORDEM = 3 AND l.PROCONF_GRUPO <= '99999')
              OR ( pp.TIPO_ORDEM = 1 AND l.PROCONF_GRUPO > 'B9999')
              OR ( pp.TIPO_ORDEM = 2 AND l.PROCONF_GRUPO LIKE 'A%')
              )
          AND ( pp.DATA_ENTRADA_CORTE = (CURRENT_DATE - 100000)
              OR ( pp.DATA_ENTRADA_CORTE IS NULL
                 AND o.DATA_ENTRADA_CORTE IS NULL)
              OR ( pp.DATA_ENTRADA_CORTE <> (CURRENT_DATE - 100000)
                 AND o.DATA_ENTRADA_CORTE = pp.DATA_ENTRADA_CORTE)
              )
        GROUP BY
          pp.PERIODO_PRODUCAO
        , p.DATA_INI_PERIODO
        , p.DATA_FIM_PERIODO
        , pp.ALTERNATIVA_PECA
        , pp.ROTEIRO_PECA
        , pp.TIPO_ORDEM
        , pp.DATA_ENTRADA_CORTE
        ORDER BY
          pp.PERIODO_PRODUCAO
        , pp.ALTERNATIVA_PECA
        , pp.ROTEIRO_PECA
        , pp.TIPO_ORDEM
        , pp.DATA_ENTRADA_CORTE
    """
    cursor.execute(sql)
    return dictlist(cursor)
