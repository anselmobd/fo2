from utils.functions.models import rows_to_dict_list


def op_estagios(cursor, op):
    # Lotes ordenados por OS + referência + estágio
    sql = '''
        SELECT
          l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO EST
        , l.CODIGO_ESTAGIO COD_EST
        , cast( SUM( l.QTDE_PECAS_PROD ) / SUM( l.QTDE_PECAS_PROG ) * 100
                AS NUMERIC(10,2) ) PERC
        -- , SUM( l.QTDE_EM_PRODUCAO_PACOTE ) EMPROD
        , SUM( l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO ) EMPROD
        , SUM( l.QTDE_PECAS_PROD ) PROD
        , SUM( l.QTDE_PECAS_2A ) Q2
        , SUM( l.QTDE_PERDAS ) PERDA
        , SUM(
            CASE WHEN l.CODIGO_ESTAGIO = 63
            THEN 0
            ELSE l.QTDE_CONSERTO
            END
          ) CONSERTO
        , SUM(
            CASE WHEN l.CODIGO_ESTAGIO = 63
            THEN l.QTDE_CONSERTO
            ELSE 0
            END
          ) ENDERECADO
        , SUM(
            CASE WHEN l.CODIGO_ESTAGIO = 63
            THEN l.QTDE_DISPONIVEL_BAIXA
            ELSE 0
            END
          ) DESENDERECADO
        , SUM(
          -- CASE WHEN l.QTDE_EM_PRODUCAO_PACOTE <> 0
          CASE WHEN l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO <> 0
          THEN 1 ELSE 0 END
          ) LOTES
        , LISTAGG(DISTINCT l.SEQ_OPERACAO, ', ')
          WITHIN GROUP (ORDER BY l.SEQ_OPERACAO) SEQ_OPER
        , LISTAGG(DISTINCT l.SEQUENCIA_ESTAGIO, ', ')
          WITHIN GROUP (ORDER BY l.SEQ_OPERACAO) SEQ_EST
        , LISTAGG(DISTINCT l.ESTAGIO_ANTERIOR, ', ')
          WITHIN GROUP (ORDER BY l.SEQ_OPERACAO) EST_ANT
        FROM pcpc_040 l
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.ORDEM_PRODUCAO = %s
        GROUP BY
          l.SEQ_OPERACAO
        , l.CODIGO_ESTAGIO
        , e.DESCRICAO
        , l.ORDEM_PRODUCAO
        ORDER BY
          l.SEQ_OPERACAO
    '''
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)
