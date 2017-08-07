from fo2.models import rows_to_dict_list

from lotes.models import *
from lotes.models.base import *


def por_alter_qtd(cursor, periodo):
    # Produção por alternativa
    print('periodo=', periodo)
    sql = """
        SELECT
          l.PERIODO_PRODUCAO PERIODO
        , p.DATA_INI_PERIODO PERIODO_INI
        , p.DATA_FIM_PERIODO PERIODO_FIM
        , o.ALTERNATIVA_PECA || '/' || o.ROTEIRO_PECA ALT
        , CASE
          WHEN l.PROCONF_GRUPO <= '99999' THEN 'MD'
          WHEN l.PROCONF_GRUPO > 'A9999' THEN 'PA'
          ELSE 'PG'
          END TIPO
        , CASE
          WHEN l.PROCONF_GRUPO <= '99999' THEN 3
          WHEN l.PROCONF_GRUPO > 'A9999' THEN 1
          ELSE 2
          END TIPO_ORDEM
        , SUM( l.QTDE_PECAS_PROG ) QTD
        FROM pcpc_040 l
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        JOIN PCPC_010 p
          ON p.AREA_PERIODO = 1
         AND p.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
        WHERE l.PROCONF_NIVEL99 = 1
    """
    if periodo == '0':
        sql += """
            AND p.DATA_INI_PERIODO <= CURRENT_DATE
            AND p.DATA_FIM_PERIODO >= CURRENT_DATE
        """
    else:
        sql += """
            AND l.PERIODO_PRODUCAO = %s
        """
    sql += """
          AND l.SEQ_OPERACAO = (
            SELECT
              MAX( ls.SEQ_OPERACAO )
            FROM pcpc_040 ls
            WHERE ls.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
          )
        GROUP BY
          l.PERIODO_PRODUCAO
        , p.DATA_INI_PERIODO
        , p.DATA_FIM_PERIODO
        , o.ALTERNATIVA_PECA
        , o.ROTEIRO_PECA
        , CASE
          WHEN l.PROCONF_GRUPO <= '99999' THEN 'MD'
          WHEN l.PROCONF_GRUPO > 'A9999' THEN 'PA'
          ELSE 'PG'
          END
        , CASE
          WHEN l.PROCONF_GRUPO <= '99999' THEN 3
          WHEN l.PROCONF_GRUPO > 'A9999' THEN 1
          ELSE 2
          END
        ORDER BY
          l.PERIODO_PRODUCAO
        , o.ALTERNATIVA_PECA
        , o.ROTEIRO_PECA
        , 6
    """
    if periodo == '0':
        cursor.execute(sql)
    else:
        cursor.execute(sql, [periodo])
    return rows_to_dict_list(cursor)
