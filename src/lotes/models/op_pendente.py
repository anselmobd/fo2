from fo2.models import rows_to_dict_list

from lotes.models import *
from lotes.models.base import *


def op_pendente(cursor, estagio):
    # Ordens pendentes por estágio
    sql = """
        SELECT
          e.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
        , l.PERIODO_PRODUCAO PERIODO
        , l.PROCONF_GRUPO REF
        , l.ORDEM_PRODUCAO OP
        , SUM( l.QTDE_PECAS_PROG - l.QTDE_PECAS_PROD) QTD
        , COUNT(*) LOTES
        FROM MQOP_005 e
        JOIN PCPC_040 l
          ON l.CODIGO_ESTAGIO = e.CODIGO_ESTAGIO
        WHERE l.QTDE_EM_PRODUCAO_PACOTE <> 0
          AND ( %s is NULL or e.CODIGO_ESTAGIO = %s )
        GROUP BY
          e.CODIGO_ESTAGIO
        , e.DESCRICAO
        , l.ORDEM_PRODUCAO
        , l.PROCONF_GRUPO
        , l.PERIODO_PRODUCAO
        ORDER BY
          e.CODIGO_ESTAGIO
        , l.PERIODO_PRODUCAO
        , l.PROCONF_GRUPO
        , l.ORDEM_PRODUCAO
    """
    cursor.execute(sql, (estagio, estagio))
    return rows_to_dict_list(cursor)
