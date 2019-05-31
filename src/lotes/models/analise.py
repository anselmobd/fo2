from fo2.models import rows_to_dict_list

from lotes.models import *
from lotes.models.base import *


def an_periodo_alter_qtd(cursor, periodo_de, periodo_ate, alternativa):
    # Produção por periodo e alternativa
    sql = """
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
          AND (o.ALTERNATIVA_PECA = '{alternativa}' OR '{alternativa}' IS NULL)
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
          AND (o.ALTERNATIVA_PECA = '{alternativa}' OR '{alternativa}' IS NULL)
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
    """.format(periodo_de=periodo_de, periodo_ate=periodo_ate,
               alternativa=alternativa)
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def an_dtcorte_alter_qtd(cursor, data_de, data_ate, alternativa):
    # Produção por data de corte/gargalo e alternativa
    sql = """
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
        , CASE WHEN pp.PERIODO_PRODUCAO = -1 THEN 1
          ELSE 2
          END ORDEM_TOTAL
        , SUM( l.QTDE_PECAS_PROG ) QTD
        , COUNT(DISTINCT o.ORDEM_PRODUCAO) NUM_OPS
        , pp.OPS
        FROM
        (
        SELECT distinct
          -1 PERIODO_PRODUCAO
        , o.ALTERNATIVA_PECA
        , o.ROTEIRO_PECA
        , CASE
          WHEN l.PROCONF_GRUPO <= '99999' THEN 3
          WHEN l.PROCONF_GRUPO > 'B9999' THEN 1
          ELSE 2
          END TIPO_ORDEM
        , DATA_ENTRADA_CORTE
        , '' OPS
        FROM pcpc_040 l
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        WHERE l.PROCONF_NIVEL99 = 1
          AND o.SITUACAO IN (2, 4)
          AND o.DATA_ENTRADA_CORTE >= '{data_de}'
          AND o.DATA_ENTRADA_CORTE <= '{data_ate}'
          AND (o.ALTERNATIVA_PECA = '{alternativa}' OR '{alternativa}' IS NULL)
        UNION
        SELECT
          p1.*
        , LISTAGG(o1.ORDEM_PRODUCAO, ', ')
          WITHIN GROUP (ORDER BY o1.ORDEM_PRODUCAO) OPS
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
        , o.DATA_ENTRADA_CORTE
        FROM pcpc_040 l
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        WHERE l.PROCONF_NIVEL99 = 1
          AND o.SITUACAO IN (2, 4)
          AND o.DATA_ENTRADA_CORTE >= '{data_de}'
          AND o.DATA_ENTRADA_CORTE <= '{data_ate}'
          AND (o.ALTERNATIVA_PECA = '{alternativa}' OR '{alternativa}' IS NULL)
        ) p1
        JOIN PCPC_020 o1
          ON o1.DATA_ENTRADA_CORTE = p1.DATA_ENTRADA_CORTE
         AND o1.PERIODO_PRODUCAO = p1.PERIODO_PRODUCAO
         AND o1.SITUACAO IN (2, 4)
         AND o1.ALTERNATIVA_PECA = p1.ALTERNATIVA_PECA
         AND o1.ROTEIRO_PECA = p1.ROTEIRO_PECA
         AND (  ( p1.TIPO_ORDEM = 3 AND o1.REFERENCIA_PECA <= '99999')
             OR ( p1.TIPO_ORDEM = 1 AND o1.REFERENCIA_PECA > 'B9999')
             OR ( p1.TIPO_ORDEM = 2 AND o1.REFERENCIA_PECA LIKE 'A%')
             )
        GROUP BY
          p1.PERIODO_PRODUCAO
        , p1.ALTERNATIVA_PECA
        , p1.ROTEIRO_PECA
        , p1.TIPO_ORDEM
        , p1.DATA_ENTRADA_CORTE
        ) pp
        JOIN PCPC_020 o
          ON o.DATA_ENTRADA_CORTE = pp.DATA_ENTRADA_CORTE
         AND ( pp.PERIODO_PRODUCAO = -1
             OR ( pp.PERIODO_PRODUCAO <> -1
                AND o.PERIODO_PRODUCAO = pp.PERIODO_PRODUCAO)
             )
        JOIN pcpc_040 l
          ON l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
        LEFT JOIN PCPC_010 p
          ON p.AREA_PERIODO = 1
         AND p.PERIODO_PRODUCAO = pp.PERIODO_PRODUCAO
        WHERE l.PROCONF_NIVEL99 = 1
          AND o.SITUACAO IN (2, 4)
          AND o.ALTERNATIVA_PECA = pp.ALTERNATIVA_PECA
          AND o.ROTEIRO_PECA = pp.ROTEIRO_PECA
          AND (  ( pp.TIPO_ORDEM = 3 AND l.PROCONF_GRUPO <= '99999')
              OR ( pp.TIPO_ORDEM = 1 AND l.PROCONF_GRUPO > 'B9999')
              OR ( pp.TIPO_ORDEM = 2 AND l.PROCONF_GRUPO LIKE 'A%')
              )
          AND l.SEQ_OPERACAO = (
            SELECT
              MAX( ls.SEQ_OPERACAO )
            FROM pcpc_040 ls
            WHERE ls.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
          )
        GROUP BY
          pp.DATA_ENTRADA_CORTE
        , pp.ALTERNATIVA_PECA
        , pp.ROTEIRO_PECA
        , pp.TIPO_ORDEM
        , pp.PERIODO_PRODUCAO
        , p.DATA_INI_PERIODO
        , p.DATA_FIM_PERIODO
        , pp.OPS
        ORDER BY
          pp.DATA_ENTRADA_CORTE
        , pp.ALTERNATIVA_PECA
        , pp.ROTEIRO_PECA
        , pp.TIPO_ORDEM
        , pp.PERIODO_PRODUCAO
    """.format(data_de=data_de, data_ate=data_ate, alternativa=alternativa)
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
