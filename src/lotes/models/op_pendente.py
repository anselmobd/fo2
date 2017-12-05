from fo2.models import rows_to_dict_list

from lotes.models import *
from lotes.models.base import *


def op_pendente(cursor, estagio, periodo_de, periodo_ate, data_de, data_ate,
                colecao, situacao):
    # Ordens pendentes por estágio
    sql = """
        SELECT
          pend.*
        , (
          SELECT
            COUNT(*)
          FROM PCPC_040 ll -- lotes
          WHERE ll.ORDEM_PRODUCAO = pend.OP
            AND ll.SEQ_OPERACAO < pend.SEQ
            AND ll.QTDE_EM_PRODUCAO_PACOTE <> 0
          ) LOTES_ANTES
        , (
          SELECT
            COUNT(*)
          FROM PCPC_040 ll -- lotes
          WHERE ll.ORDEM_PRODUCAO = pend.OP
            AND ll.CODIGO_ESTAGIO = pend.CODIGO_ESTAGIO
          ) QTD_LOTES
        , (
          SELECT
            COUNT(*)
          FROM PCPC_040 ll -- lotes
          WHERE ll.ORDEM_PRODUCAO = pend.OP
            AND ll.SEQ_OPERACAO > pend.SEQ
            AND ll.QTDE_EM_PRODUCAO_PACOTE <> 0
          ) LOTES_DEPOIS
        FROM
        (
        SELECT
          e.CODIGO_ESTAGIO
        , e.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
        , l.PERIODO_PRODUCAO PERIODO
        , p.DATA_INI_PERIODO DATA_INI
        , p.DATA_FIM_PERIODO DATA_FIM
        , r.COLECAO || ' - ' || c.DESCR_COLECAO COLECAO
        , l.PROCONF_GRUPO REF
        , l.ORDEM_PRODUCAO OP
        , l.SEQ_OPERACAO SEQ
        , o.DATA_ENTRADA_CORTE DT_CORTE
        , o.SITUACAO
        , SUM( l.QTDE_PECAS_PROG - l.QTDE_PECAS_PROD) QTD
        , COUNT(*) LOTES
        FROM MQOP_005 e
        JOIN PCPC_040 l
          ON l.CODIGO_ESTAGIO = e.CODIGO_ESTAGIO
        JOIN BASI_030 r -- cadastro de produtos
          ON r.NIVEL_ESTRUTURA = l.PROCONF_NIVEL99
         AND r.REFERENCIA = l.PROCONF_GRUPO
        JOIN BASI_140 c -- cadastro de coleções de produtos
          ON c.COLECAO = r.COLECAO
         AND ( %s is NULL or c.COLECAO = %s )
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
        JOIN PCPC_010 p
          ON p.AREA_PERIODO = 1
         AND p.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
        WHERE l.QTDE_EM_PRODUCAO_PACOTE <> 0
          AND o.SITUACAO in (4, 2) -- Ordens em produção, Ordem cofec. gerada
          AND ( %s is NULL or e.CODIGO_ESTAGIO = %s )
          AND l.PERIODO_PRODUCAO >= %s
          AND l.PERIODO_PRODUCAO <= %s
          AND ( %s is NULL or o.DATA_ENTRADA_CORTE >= %s )
          AND ( %s is NULL or o.DATA_ENTRADA_CORTE <= %s )
          AND ( %s is NULL or o.SITUACAO = %s )
        GROUP BY
          e.CODIGO_ESTAGIO
        , e.DESCRICAO
        , l.PERIODO_PRODUCAO
        , p.DATA_INI_PERIODO
        , p.DATA_FIM_PERIODO
        , l.PROCONF_GRUPO
        , r.COLECAO
        , c.DESCR_COLECAO
        , l.ORDEM_PRODUCAO
        , l.SEQ_OPERACAO
        , o.DATA_ENTRADA_CORTE
        , o.SITUACAO
        ORDER BY
          o.SITUACAO
        , e.CODIGO_ESTAGIO
        , l.PERIODO_PRODUCAO
        , r.COLECAO
        , l.PROCONF_GRUPO
        , l.ORDEM_PRODUCAO
        ) pend
    """
    cursor.execute(sql, (colecao, colecao, estagio, estagio,
                   periodo_de, periodo_ate,
                   data_de, data_de, data_ate, data_ate,
                   situacao, situacao))
    return rows_to_dict_list(cursor)
