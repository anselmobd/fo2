from utils.functions.models import (
    rows_to_dict_list,
    rows_to_dict_list_lower,
)

import lotes.queries.lote
import lotes.queries.os


def op_estagios(cursor, op):
    # Lotes ordenados por OS + referência + estágio
    sql = '''
        SELECT
          l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO EST
        , l.CODIGO_ESTAGIO COD_EST
        , cast( SUM( l.QTDE_PECAS_PROD ) / SUM( l.QTDE_PECAS_PROG ) * 100
                AS NUMERIC(10,2) ) PERC
        , SUM( l.QTDE_EM_PRODUCAO_PACOTE ) EMPROD
        , SUM( l.QTDE_PECAS_PROD ) PROD
        , SUM( l.QTDE_PECAS_2A ) Q2
        , SUM( l.QTDE_PERDAS ) PERDA
        , SUM( l.QTDE_CONSERTO ) CONSERTO
        , SUM(
          CASE WHEN l.QTDE_EM_PRODUCAO_PACOTE <> 0 THEN 1 ELSE 0 END
          ) LOTES
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
          ON uu.CODIGO_USUARIO = u.CODIGO_USUARIO
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


def op_ref_estagio(cursor, op):
    # Totais por referência + estágio
    sql = '''
        SELECT
          lote.REF
        , lote.TAM
        , lote.COR
        , lote.EST
        , count(*) LOTES
        , sum(lote.QTD) QTD
        FROM (
          SELECT
            l.PROCONF_GRUPO REF
          , l.PROCONF_SUBGRUPO TAM
          , l.PROCONF_ITEM COR
          , COALESCE(
              ( SELECT
                  LISTAGG(le.CODIGO_ESTAGIO || ' - ' || ed.DESCRICAO, ' & ')
                  WITHIN GROUP (ORDER BY le.CODIGO_ESTAGIO)
                FROM PCPC_040 le
                JOIN MQOP_005 ed
                  ON ed.CODIGO_ESTAGIO = le.CODIGO_ESTAGIO
                WHERE le.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                  AND le.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                  AND le.QTDE_EM_PRODUCAO_PACOTE <> 0
              )
            , 'FINALIZADO'
            ) EST
          , l.QTDE_PECAS_PROG QTD
          FROM (
            SELECT
              os.PROCONF_GRUPO
            , os.PROCONF_SUBGRUPO
            , os.PROCONF_ITEM
            , os.PERIODO_PRODUCAO
            , os.ORDEM_CONFECCAO
            , max( os.NUMERO_ORDEM ) NUMERO_ORDEM
            , max( os.QTDE_PECAS_PROG ) QTDE_PECAS_PROG
            FROM PCPC_040 os
            WHERE os.ORDEM_PRODUCAO = %s
            GROUP BY
              os.PROCONF_GRUPO
            , os.PROCONF_SUBGRUPO
            , os.PROCONF_ITEM
            , os.PERIODO_PRODUCAO
            , os.ORDEM_CONFECCAO
          ) l
        ) lote
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = lote.TAM
        GROUP BY
          lote.REF
        , lote.COR
        , t.ORDEM_TAMANHO
        , lote.TAM
        , lote.EST
        ORDER BY
          lote.REF
        , lote.COR
        , t.ORDEM_TAMANHO
        , lote.EST
    '''
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)


def op_get_os(cursor, op):
    # Informações sobre OS
    return lotes.queries.os.get_os(cursor, op=op)


def op_os_ref(cursor, op):
    # Totais por OS + referência
    sql = """
        SELECT
          l.NUMERO_ORDEM OS
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        , count( l.ORDEM_CONFECCAO ) LOTES
        , SUM (
            ( SELECT
                q.QTDE_PECAS_PROG
              FROM PCPC_040 q
              WHERE q.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                AND q.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                AND q.SEQ_OPERACAO = (
                  SELECT
                    min(o.SEQ_OPERACAO)
                  FROM PCPC_040 o
                  WHERE o.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                    AND o.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                )
            )
          ) QTD
        FROM (
          SELECT DISTINCT
            os.ORDEM_PRODUCAO
          , os.PERIODO_PRODUCAO
          , os.ORDEM_CONFECCAO
          , max( os.NUMERO_ORDEM ) NUMERO_ORDEM
          , os.PROCONF_GRUPO
          , os.PROCONF_SUBGRUPO
          , os.PROCONF_ITEM
          FROM PCPC_040 os
          WHERE os.ORDEM_PRODUCAO = %s
          GROUP BY
            os.ORDEM_PRODUCAO
          , os.PERIODO_PRODUCAO
          , os.ORDEM_CONFECCAO
          , os.PROCONF_GRUPO
          , os.PROCONF_SUBGRUPO
          , os.PROCONF_ITEM
        ) l
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        GROUP BY
          l.ORDEM_PRODUCAO
        , l.NUMERO_ORDEM
        , l.PROCONF_GRUPO
        , l.PROCONF_SUBGRUPO
        , t.ORDEM_TAMANHO
        , l.PROCONF_ITEM
        ORDER BY
          l.ORDEM_PRODUCAO
        , l.NUMERO_ORDEM
        , l.PROCONF_GRUPO
        , l.PROCONF_ITEM
        , t.ORDEM_TAMANHO
    """
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)


def op_tam_cor_qtd(cursor, op):
    sql = """
        SELECT
          lote.PROCONF_SUBGRUPO TAM
        , lote.PROCONF_ITEM COR
        , sum(lote.QTDE_PECAS_PROG ) QTD
        FROM PCPC_040 lote
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
        WHERE lote.ORDEM_PRODUCAO = %s
          AND lote.SEQUENCIA_ESTAGIO
              = COALESCE(
                  (
                    SELECT
                      MIN(ulote.SEQUENCIA_ESTAGIO)
                    FROM PCPC_040 ulote
                    WHERE ulote.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
                      AND ulote.ORDEM_CONFECCAO = lote.ORDEM_CONFECCAO
                    GROUP BY
                      ulote.ORDEM_PRODUCAO
                    , ulote.ORDEM_CONFECCAO
                  )
                , 0)
        GROUP BY
          tam.ORDEM_TAMANHO
        , lote.PROCONF_SUBGRUPO
        , lote.PROCONF_ITEM
        ORDER BY
          tam.ORDEM_TAMANHO
        , lote.PROCONF_ITEM
    """
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)


def op_conserto(cursor):
    sql = """
        SELECT
          lote.PROCONF_GRUPO REF
        , lote.PROCONF_ITEM COR
        , lote.PROCONF_SUBGRUPO TAM
        , lote.ORDEM_PRODUCAO OP
        , sum(lote.QTDE_CONSERTO ) QTD
        FROM PCPC_040 lote
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
        GROUP BY
          lote.PROCONF_GRUPO
        , lote.PROCONF_ITEM
        , tam.ORDEM_TAMANHO
        , lote.PROCONF_SUBGRUPO
        , lote.ORDEM_PRODUCAO
        HAVING
          sum(lote.QTDE_CONSERTO ) > 0
        ORDER BY
          lote.PROCONF_GRUPO
        , lote.PROCONF_ITEM
        , tam.ORDEM_TAMANHO
        , lote.PROCONF_SUBGRUPO
        , lote.ORDEM_PRODUCAO
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def op_perda(cursor, data_de, data_ate, detalhe):
    sql = """
        SELECT
          lote.PROCONF_GRUPO REF
    """
    if detalhe == 'c':
        sql += """
            , lote.PROCONF_ITEM COR
            , lote.PROCONF_SUBGRUPO TAM
        """
    sql += """
        , lote.ORDEM_PRODUCAO OP
        , sum(lote.QTDE_PERDAS ) QTD
        , ( SELECT
              SUM( l.QTDE_PECAS_PROG )
            FROM pcpc_040 l
            WHERE l.ORDEM_PRODUCAO = 9242
              AND l.SEQ_OPERACAO = (
                SELECT
                  MIN( ls.SEQ_OPERACAO )
                FROM pcpc_040 ls
                WHERE ls.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
              )
          ) QTDOP
        FROM PCPC_040 lote
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
        WHERE o.DATA_ENTRADA_CORTE >= %s
          AND o.DATA_ENTRADA_CORTE <= %s
        GROUP BY
          lote.PROCONF_GRUPO
    """
    if detalhe == 'c':
        sql += """
            , lote.PROCONF_ITEM
            , tam.ORDEM_TAMANHO
            , lote.PROCONF_SUBGRUPO
        """
    sql += """
        , lote.ORDEM_PRODUCAO
        HAVING
          sum(lote.QTDE_PERDAS ) > 0
        ORDER BY
          lote.PROCONF_GRUPO
    """
    if detalhe == 'c':
        sql += """
            , lote.PROCONF_ITEM
            , tam.ORDEM_TAMANHO
            , lote.PROCONF_SUBGRUPO
        """
    sql += """
        , lote.ORDEM_PRODUCAO
    """
    cursor.execute(sql, [data_de, data_ate])
    return rows_to_dict_list(cursor)


def busca_ops_info(cursor, ops):
    filtro_op = ''
    sep = '('
    for op in ops:
        filtro_op += "{} '{}'".format(sep, op)
        sep = ','

    sql = """
        SELECT
          op.ORDEM_PRODUCAO OP
        , op.PEDIDO_VENDA PEDIDO
        FROM PCPC_020 op -- OP capa
        WHERE op.ORDEM_PRODUCAO IN
        --( 12345
        --, 12334
        {filtro_op} -- filtro_op
        )
    """.format(
        filtro_op=filtro_op,
    )

    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
