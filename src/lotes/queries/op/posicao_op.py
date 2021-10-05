from utils.functions.models import rows_to_dict_list


def posicao_op(cursor, op):
    sql = '''
        WITH ops AS (
          SELECT
            ms.ORDEM_PRODUCAO OP
          , max(ms.SEQUENCIA_ESTAGIO) MAXSEQ
          FROM PCPC_040 ms
          WHERE ms.ORDEM_PRODUCAO = %s
          GROUP BY
            ms.ORDEM_PRODUCAO
        )
        (
        SELECT
          0 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , sum(l.QTDE_PECAS_PROD) QTD
        , 'FINALIZADO 1A.' TIPO
        , l.CODIGO_ESTAGIO || '-' || e.DESCRICAO ESTAGIO
        FROM ops o
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = o.op
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE (l.QTDE_PECAS_PROD) <> 0
          AND l.SEQUENCIA_ESTAGIO = o.MAXSEQ
        GROUP BY
          l.SEQUENCIA_ESTAGIO
        , l.CODIGO_ESTAGIO
        , e.DESCRICAO
        --
        UNION
        --
        SELECT
          1000 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , sum(QTDE_PECAS_2A) QTD
        , 'FINALIZADO 2A.' TIPO
        , l.CODIGO_ESTAGIO || '-' || e.DESCRICAO ESTAGIO
        FROM ops o
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = o.op
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE (QTDE_PECAS_2A) <> 0
          AND l.SEQUENCIA_ESTAGIO = o.MAXSEQ
        GROUP BY
          l.SEQUENCIA_ESTAGIO
        , l.CODIGO_ESTAGIO
        , e.DESCRICAO
        --
        UNION
        --
        SELECT
          2000 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , sum(l.QTDE_EM_PRODUCAO_PACOTE - l.QTDE_CONSERTO) QTD
        , 'A PRODUZIR' TIPO
        , l.CODIGO_ESTAGIO || '-' || e.DESCRICAO ESTAGIO
        FROM ops o
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = o.op
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE (l.QTDE_EM_PRODUCAO_PACOTE - l.QTDE_CONSERTO) > 0
        GROUP BY
          l.SEQUENCIA_ESTAGIO
        , l.CODIGO_ESTAGIO
        , e.DESCRICAO
        --
        UNION
        --
        SELECT
          3000 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , sum(l.QTDE_CONSERTO) QTD
        , 'ENDEREÇADO' TIPO
        , l.CODIGO_ESTAGIO || '-' || e.DESCRICAO ESTAGIO
        FROM ops o
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = o.op
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.QTDE_CONSERTO > 0
          AND l.CODIGO_ESTAGIO = 63
        GROUP BY
          l.SEQUENCIA_ESTAGIO
        , l.CODIGO_ESTAGIO
        , e.DESCRICAO
        --
        UNION
        --
        --
        SELECT
          3000 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , sum(l.QTDE_CONSERTO) QTD
        , 'EM CONSERTO' TIPO
        , l.CODIGO_ESTAGIO || '-' || e.DESCRICAO ESTAGIO
        FROM ops o
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = o.op
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.QTDE_CONSERTO > 0
          AND l.CODIGO_ESTAGIO <> 63
        GROUP BY
          l.SEQUENCIA_ESTAGIO
        , l.CODIGO_ESTAGIO
        , e.DESCRICAO
        --
        UNION
        --
        SELECT
          4000 + l.SEQUENCIA_ESTAGIO SEQUENCIA
        , sum(l.QTDE_PERDAS) QTD
        , 'PERDAS' TIPO
        , l.CODIGO_ESTAGIO || '-' || e.DESCRICAO ESTAGIO
        FROM ops o
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = o.op
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.QTDE_PERDAS > 0
        GROUP BY
          l.SEQUENCIA_ESTAGIO
        , l.CODIGO_ESTAGIO
        , e.DESCRICAO
        )
    '''
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)
