from pprint import pprint

from utils.functions.models import rows_to_dict_list


def posicoes_lote(cursor, periodo, ordem_confeccao):
    sql = '''
        WITH lotes AS (
        SELECT
          %s PERIODO_PRODUCAO
        , %s ORDEM_CONFECCAO
        FROM SYS.DUAL
        )
        (
        SELECT
          0 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , l.QTDE_PECAS_PROD QTD
        , 'FINALIZADO 1A.' TIPO
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO || ' (ULTIMO)' ESTAGIO
        FROM lotes sel
        JOIN PCPC_040 l
          ON l.PERIODO_PRODUCAO = sel.PERIODO_PRODUCAO
         AND l.ORDEM_CONFECCAO = sel.ORDEM_CONFECCAO
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.QTDE_PECAS_PROD <> 0
          AND l.SEQUENCIA_ESTAGIO
              = (
                SELECT
                  max(ms.SEQUENCIA_ESTAGIO)
                FROM PCPC_040 ms
                WHERE ms.PERIODO_PRODUCAO = sel.PERIODO_PRODUCAO
                  AND ms.ORDEM_CONFECCAO = sel.ORDEM_CONFECCAO
              )
        --
        UNION
        --
        SELECT
          1000 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , l.QTDE_PECAS_2A QTD
        , 'FINALIZADO 2A.' TIPO
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO || ' (ULTIMO)' ESTAGIO
        FROM lotes sel
        JOIN PCPC_040 l
          ON l.PERIODO_PRODUCAO = sel.PERIODO_PRODUCAO
         AND l.ORDEM_CONFECCAO = sel.ORDEM_CONFECCAO
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.QTDE_PECAS_2A <> 0
          AND l.SEQUENCIA_ESTAGIO
              = (
                SELECT
                  max(ms.SEQUENCIA_ESTAGIO)
                FROM PCPC_040 ms
                WHERE ms.PERIODO_PRODUCAO = sel.PERIODO_PRODUCAO
                  AND ms.ORDEM_CONFECCAO = sel.ORDEM_CONFECCAO
              )
        --
        UNION
        --
        SELECT
          2000 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , l.QTDE_DISPONIVEL_BAIXA QTD
        , 'A PRODUZIR' TIPO
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
        FROM lotes sel
        JOIN PCPC_040 l
          ON l.PERIODO_PRODUCAO = sel.PERIODO_PRODUCAO
         AND l.ORDEM_CONFECCAO = sel.ORDEM_CONFECCAO
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.QTDE_DISPONIVEL_BAIXA > 0
        --
        UNION
        --
        SELECT
          3000 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , l.QTDE_CONSERTO QTD
        , CASE WHEN l.CODIGO_ESTAGIO = 63 THEN 'ENDEREÇADO'
          ELSE 'EM CONSERTO' END TIPO
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
        FROM lotes sel
        JOIN PCPC_040 l
          ON l.PERIODO_PRODUCAO = sel.PERIODO_PRODUCAO
         AND l.ORDEM_CONFECCAO = sel.ORDEM_CONFECCAO
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.QTDE_CONSERTO <> 0
        --
        UNION
        --
        SELECT
          4000 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , l.QTDE_PERDAS QTD
        , 'PERDAS' TIPO
        , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
        FROM lotes sel
        JOIN PCPC_040 l
          ON l.PERIODO_PRODUCAO = sel.PERIODO_PRODUCAO
         AND l.ORDEM_CONFECCAO = sel.ORDEM_CONFECCAO
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.QTDE_PERDAS <> 0
        )
    '''
    cursor.execute(sql, [periodo, ordem_confeccao])
    return rows_to_dict_list(cursor)
