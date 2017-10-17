from fo2.models import rows_to_dict_list

from lotes.models import *
from lotes.models.base import *


def op_pendente(cursor, estagio, periodo_de, periodo_ate):
    # Ordens pendentes por estágio
    sql = """
        SELECT
          e.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
        , l.PERIODO_PRODUCAO PERIODO
        , p.DATA_INI_PERIODO DATA_INI
        , p.DATA_FIM_PERIODO DATA_FIM
        , l.PROCONF_GRUPO REF
        , l.ORDEM_PRODUCAO OP
        , SUM( l.QTDE_PECAS_PROG - l.QTDE_PECAS_PROD) QTD
        , COUNT(*) LOTES
        FROM MQOP_005 e
        JOIN PCPC_040 l
          ON l.CODIGO_ESTAGIO = e.CODIGO_ESTAGIO
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        JOIN PCPC_010 p
          ON p.AREA_PERIODO = 1
         AND p.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
        WHERE l.QTDE_EM_PRODUCAO_PACOTE <> 0
          AND o.SITUACAO = 4 -- Ordens em produção
          AND ( %s is NULL or e.CODIGO_ESTAGIO = %s )
          AND l.PERIODO_PRODUCAO >= %s
          AND l.PERIODO_PRODUCAO <= %s
        GROUP BY
          e.CODIGO_ESTAGIO
        , e.DESCRICAO
        , l.PERIODO_PRODUCAO
        , p.DATA_INI_PERIODO
        , p.DATA_FIM_PERIODO
        , l.PROCONF_GRUPO
        , l.ORDEM_PRODUCAO
        ORDER BY
          e.CODIGO_ESTAGIO
        , l.PERIODO_PRODUCAO
        , l.PROCONF_GRUPO
        , l.ORDEM_PRODUCAO
    """
    cursor.execute(sql, (estagio, estagio, periodo_de, periodo_ate))
    return rows_to_dict_list(cursor)
