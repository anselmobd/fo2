from utils.functions.models import rows_to_dict_list


def op_movi_estagios(cursor, op):
    # Lotes ordenados por OS + referência + estágio
    sql = '''
        SELECT
          ll.EST
        , uu.USUARIO USU
        , count(*) LOTES
        , CASE WHEN u.QTDE_PRODUZIDA + u.QTDE_PECAS_2A +
                    u.QTDE_PERDAS + u.QTDE_CONSERTO < 0
          THEN 'ESTORNO'
          ELSE 'BAIXA'
          END MOV
        , MIN(u.DATA_PRODUCAO) DT_MIN
        , ROUND( TO_DATE('01/01/2001','DD/MM/YYYY')
               + AVG(u.DATA_PRODUCAO - TO_DATE('01/01/2001','DD/MM/YYYY'))
               - MIN(u.DATA_PRODUCAO)
               ) DIA_INI
        , TO_DATE('01/01/2001','DD/MM/YYYY')
        + AVG(u.DATA_PRODUCAO - TO_DATE('01/01/2001','DD/MM/YYYY')) DT_AVG
        , ROUND( MAX(u.DATA_PRODUCAO)
               - ( TO_DATE('01/01/2001','DD/MM/YYYY')
                 + AVG(u.DATA_PRODUCAO - TO_DATE('01/01/2001','DD/MM/YYYY'))
                 )
               ) DIA_FIM
        , MAX(u.DATA_PRODUCAO) DT_MAX
        FROM (
          SELECT DISTINCT
            l.SEQ_OPERACAO
          , l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO EST
          , l.CODIGO_ESTAGIO
          , l.ORDEM_PRODUCAO
          FROM pcpc_040 l
          JOIN MQOP_005 e
            ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
          WHERE l.ORDEM_PRODUCAO = %s
        ) ll
        JOIN pcpc_045 u
          ON u.ORDEM_PRODUCAO = ll.ORDEM_PRODUCAO
         AND u.PCPC040_ESTCONF = ll.CODIGO_ESTAGIO
         --AND u.QTDE_PRODUZIDA + u.QTDE_PECAS_2A +
         --  u.QTDE_PERDAS + u.QTDE_CONSERTO <> 0
        LEFT JOIN HDOC_030 uu
          ON uu.EMRPESA = 1
         AND uu.CODIGO_USUARIO = u.CODIGO_USUARIO
        GROUP BY
          ll.SEQ_OPERACAO
        , ll.EST
        , CASE WHEN u.QTDE_PRODUZIDA + u.QTDE_PECAS_2A +
                    u.QTDE_PERDAS + u.QTDE_CONSERTO < 0
          THEN 'ESTORNO'
          ELSE 'BAIXA'
          END
        , u.PCPC040_ESTCONF
        , uu.USUARIO
        ORDER BY
          ll.SEQ_OPERACAO
        , 5 -- DT_MIN
        , 4 -- MOVIMENTO
        , 3 DESC -- LOTES
        , uu.USUARIO
    '''
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)
