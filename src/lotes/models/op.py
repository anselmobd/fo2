from fo2.models import rows_to_dict_list, GradeQtd

from lotes.models import *
from lotes.models.base import *


def op_inform(cursor, op):
    # informações gerais de 1 OP
    return(busca_op(cursor, op=op))


def busca_op(
        cursor, op=None, ref=None, deposito=None, tipo=None, situacao=None,
        posicao=None):
    filtra_op = ""
    if op is not None and op != '':
        filtra_op = """
            AND o.ORDEM_PRODUCAO = '{}'
            AND rownum = 1
        """.format(op)

    filtra_ref = ""
    if ref is not None and ref != '':
        if '%' in ref:
            filtra_ref = """
                AND o.REFERENCIA_PECA like '{}'
            """.format(ref)
        else:
            filtra_ref = """
                AND o.REFERENCIA_PECA = '{}'
            """.format(ref)

    filtra_deposito = ""
    if deposito is not None and deposito != '':
        filtra_deposito = """
            AND o.DEPOSITO_ENTRADA = '{}'
        """.format(deposito)

    filtra_posicao = ""
    if posicao == 'p':
        filtra_posicao = """--
            AND
            ( SELECT
                sum(l.QTDE_EM_PRODUCAO_PACOTE) QTD
              FROM PCPC_040 l
              WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
                AND (l.QTDE_EM_PRODUCAO_PACOTE) > 0
            ) > 0"""
    elif posicao == 'p63':
        filtra_posicao = """--
            AND
            ( SELECT
                sum(l.QTDE_EM_PRODUCAO_PACOTE) QTD
              FROM PCPC_040 l
              WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
                AND (l.QTDE_EM_PRODUCAO_PACOTE) > 0
                AND l.CODIGO_ESTAGIO <> 63
            ) > 0"""
    elif posicao == 'f':
        filtra_posicao = """--
            AND
            ( SELECT
                sum(l.QTDE_EM_PRODUCAO_PACOTE) QTD
              FROM PCPC_040 l
              WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
                AND (l.QTDE_EM_PRODUCAO_PACOTE) > 0
            ) = 0"""
    elif posicao == 'f63':
        filtra_posicao = """--
            AND
            ( SELECT
                sum(l.QTDE_EM_PRODUCAO_PACOTE) QTD
              FROM PCPC_040 l
              WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
                AND (l.QTDE_EM_PRODUCAO_PACOTE) > 0
                AND l.CODIGO_ESTAGIO <> 63
            ) = 0"""

    filtra_situacao = ""
    if situacao == 'a':
        filtra_situacao = "AND o.SITUACAO != 9"
    elif situacao == 'c':
        filtra_situacao = "AND o.SITUACAO = 9"

    filtro_tipo = ''
    if tipo == 'a':
        filtro_tipo = "AND o.REFERENCIA_PECA < 'A0000'"
    elif tipo == 'g':
        filtro_tipo = "AND o.REFERENCIA_PECA like 'A%'"
    elif tipo == 'b':
        filtro_tipo = "AND o.REFERENCIA_PECA like 'B%'"
    elif tipo == 'p':
        filtro_tipo = \
            "AND (o.REFERENCIA_PECA like 'A%' OR o.REFERENCIA_PECA like 'B%')"
    elif tipo == 'v':
        filtro_tipo = "AND o.REFERENCIA_PECA < 'C0000'"
    elif tipo == 'm':
        filtro_tipo = "AND o.REFERENCIA_PECA >= 'C0000'"

    sql = '''
        SELECT
          o.ORDEM_PRODUCAO OP
        , case
          when o.REFERENCIA_PECA <= '99999' then 'PA'
          when o.REFERENCIA_PECA <= 'B9999' then 'PG'
          else 'MD'
          end TIPO_REF
        , CASE
          WHEN o.ORDEM_PRINCIPAL <> 0
            OR ofi.ORDEM_PRODUCAO IS NOT NULL
            OR ome.ORDEM_PRODUCAO IS NOT NULL
            OR ose.ORDEM_PRODUCAO IS NOT NULL
          THEN 'Relacionada'
          ELSE 'Avulsa'
          END TIPO_OP
        , CASE
          WHEN o.ORDEM_PRINCIPAL <> 0 THEN 'Filha de'
          WHEN ofi.ORDEM_PRODUCAO IS NOT NULL THEN 'Mãe de'
          ELSE 'Avulsa'
          END TIPO_FM_OP
        , coalesce( ofi.ORDEM_PRODUCAO, o.ORDEM_PRINCIPAL ) OP_REL
        , o.SITUACAO ||
          CASE
          WHEN o.SITUACAO = 2 THEN '-Ordem conf. gerada'
          WHEN o.SITUACAO = 4 THEN '-Ordens em produção'
          WHEN o.SITUACAO = 9 THEN '-Ordem cancelada'
          ELSE ' '
          END SITUACAO
        , o.COD_CANCELAMENTO ||
          CASE
          WHEN o.COD_CANCELAMENTO = 0 THEN ''
          ELSE '-' || COALESCE(c.DESCRICAO, '')
          END CANCELAMENTO
        , o.ALTERNATIVA_PECA ALTERNATIVA
        , o.ROTEIRO_PECA ROTEIRO
        , o.REFERENCIA_PECA REF
        , COALESCE(
          CASE WHEN o.REFERENCIA_PECA < 'C0000' THEN
            CAST( CAST( regexp_replace(o.REFERENCIA_PECA, '[^0-9]', '')
                        AS INTEGER ) AS VARCHAR2(5) )
          ELSE
            ( SELECT
                CAST( MAX(
                  CASE WHEN ec.GRUPO_ITEM IS NULL THEN 0
                  ELSE CAST( regexp_replace(ec.GRUPO_ITEM, '[^0-9]', '')
                             AS INTEGER )
                  END
                ) AS VARCHAR2(5) )
                FROM BASI_050 ec
                JOIN BASI_030 rr
                  ON rr.NIVEL_ESTRUTURA = ec.NIVEL_ITEM
                 AND rr.REFERENCIA = ec.GRUPO_ITEM
                 AND rr.RESPONSAVEL IS NOT NULL
                WHERE ec.NIVEL_COMP = 1
                  AND ec.GRUPO_COMP = o.REFERENCIA_PECA
            )
          END
          , ' ' ) MODELO
        , ( SELECT
              COUNT( DISTINCT l.ORDEM_CONFECCAO )
            FROM pcpc_040 l
            WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
          ) LOTES
        , COALESCE(
          ( SELECT
              SUM( l.QTDE_PECAS_PROG )
            FROM pcpc_040 l
            WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
              AND l.SEQ_OPERACAO = (
                SELECT
                  MAX( ls.SEQ_OPERACAO )
                FROM pcpc_040 ls
                WHERE ls.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
              )
          )
          , 0 ) QTD
        , o.DATA_PROGRAMACAO DT_DIGITACAO
        , o.DATA_ENTRADA_CORTE DT_CORTE
        , o.PERIODO_PRODUCAO PERIODO
        , p.DATA_INI_PERIODO PERIODO_INI
        , p.DATA_FIM_PERIODO PERIODO_FIM
        , o.DEPOSITO_ENTRADA DEPOSITO_CODIGO
        , o.DEPOSITO_ENTRADA || ' - ' || d.DESCRICAO DEPOSITO
        , o.PEDIDO_VENDA PEDIDO
        , COALESCE(ped.COD_PED_CLIENTE, ' ') PED_CLIENTE
        , COALESCE(r.NUMERO_MOLDE, '-') MOLDE
        , r.DESCR_REFERENCIA DESCR_REF
        , o.OBSERVACAO
        , o.OBSERVACAO2
        , ( SELECT
              coalesce( max( l.CODIGO_FAMILIA || '-' || div.DESCRICAO ), ' ' )
            FROM pcpc_040 l
            LEFT JOIN BASI_180 div
              ON div.DIVISAO_PRODUCAO = l.CODIGO_FAMILIA
            WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
              AND l.CODIGO_FAMILIA > 1
              AND l.CODIGO_FAMILIA < 1000
          ) UNIDADE
        FROM PCPC_020 o
        JOIN PCPC_010 p
          ON p.AREA_PERIODO = 1
         AND p.PERIODO_PRODUCAO = o.PERIODO_PRODUCAO
        LEFT JOIN pcpt_050 c
          ON c.COD_CANCELAMENTO = o.COD_CANCELAMENTO
        LEFT JOIN PCPC_020 ofi
          ON ofi.ORDEM_PRINCIPAL = o.ORDEM_PRODUCAO
        LEFT JOIN PCPC_020 ome
          ON ome.ORDEM_PRODUCAO = o.ORDEM_MESTRE
         AND o.ORDEM_MESTRE <> 0
         AND o.ORDEM_MESTRE IS NOT NULL
        LEFT JOIN PCPC_020 ose
          ON ose.ORDEM_MESTRE = o.ORDEM_PRODUCAO
        JOIN BASI_205 d
          ON d.CODIGO_DEPOSITO = o.DEPOSITO_ENTRADA
        LEFT JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = o.PEDIDO_VENDA
        JOIN basi_030 r
          ON r.NIVEL_ESTRUTURA = 1
         AND r.REFERENCIA = o.REFERENCIA_PECA
        WHERE 1=1
          {filtra_op} -- filtra_op
          {filtra_ref} -- filtra_ref
          {filtra_deposito} -- filtra_deposito
          {filtro_tipo} -- filtro_tipo
          {filtra_situacao} -- filtra_situacao
          {filtra_posicao} -- filtra_posicao
        ORDER BY
           o.ORDEM_PRODUCAO DESC
    '''.format(
        filtra_op=filtra_op,
        filtra_ref=filtra_ref,
        filtra_deposito=filtra_deposito,
        filtro_tipo=filtro_tipo,
        filtra_situacao=filtra_situacao,
        filtra_posicao=filtra_posicao,
    )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


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
        , 'EM CONSERTO' TIPO
        , l.CODIGO_ESTAGIO || '-' || e.DESCRICAO ESTAGIO
        FROM ops o
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = o.op
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        WHERE l.QTDE_CONSERTO > 0
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


def op_relacionamentos(cursor, op):
    sql = '''
        WITH ordemp AS
        (
          SELECT
            o.ORDEM_PRODUCAO OP
          , o.ORDEM_PRINCIPAL
          , o.ORDEM_MESTRE
          FROM PCPC_020 o
          WHERE o.ORDEM_PRODUCAO  = %s
        )
        SELECT
          o.OP
        , 10
        , CAST('é Mãe de' AS varchar2(50)) REL
        , coalesce(ofi.ORDEM_PRODUCAO, 0) OP_REL
        FROM ordemp o
        JOIN PCPC_020 ofi
          ON ofi.ORDEM_PRINCIPAL = o.OP
        --
        UNION
        --
        SELECT
          o.OP
        , 15
        , CAST('é Avó de' AS varchar2(50)) REL
        , coalesce(one.ORDEM_PRODUCAO, 0) OP_REL
        FROM ordemp o
        JOIN PCPC_020 ofi
          ON ofi.ORDEM_PRINCIPAL = o.OP
        JOIN PCPC_020 one
          ON one.ORDEM_PRINCIPAL = ofi.ORDEM_PRODUCAO
        --
        UNION
        --
        SELECT
          o.OP
        , 20
        , CAST('é Filha de' AS varchar2(50)) REL
        , o.ORDEM_PRINCIPAL OP_REL
        FROM ordemp o
        WHERE o.ORDEM_PRINCIPAL <> 0
        --
        UNION
        --
        SELECT
          o.OP
        , 25
        , CAST('é Neta de' AS varchar2(50)) REL
        , one.ORDEM_PRINCIPAL OP_REL
        FROM ordemp o
        JOIN PCPC_020 one
          ON one.ORDEM_PRODUCAO = o.ORDEM_PRINCIPAL
        WHERE o.ORDEM_PRINCIPAL <> 0
          AND one.ORDEM_PRINCIPAL <> 0
        --
        UNION
        --
        SELECT
          o.OP
        , 30
        , CAST('é Mestra de' AS varchar2(50)) REL
        , ose.ORDEM_PRODUCAO OP_REL
        FROM ordemp o
        JOIN PCPC_020 ose
          ON ose.ORDEM_MESTRE = o.OP
        --
        UNION
        --
        SELECT
          o.OP
        , 40
        , CAST('é Seguidora de' AS varchar2(50)) REL
        , o.ORDEM_MESTRE OP_REL
        FROM ordemp o
        WHERE o.ORDEM_MESTRE <> 0
        --
        ORDER BY
          1
        , 2
    '''
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)


def op_estagios(cursor, op):
    # Lotes ordenados por OS + referência + estágio
    sql = '''
        SELECT
          l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO EST
        , l.CODIGO_ESTAGIO COD_EST
        , cast( SUM( l.QTDE_PECAS_PROD ) / SUM( l.QTDE_PECAS_PROG ) * 100
                AS NUMERIC(10,2) ) PERC
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
        , u.USUARIO_SYSTEXTIL
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
        GROUP BY
          ll.SEQ_OPERACAO
        , ll.EST
        , CASE WHEN u.QTDE_PRODUZIDA + u.QTDE_PECAS_2A +
                    u.QTDE_PERDAS + u.QTDE_CONSERTO < 0
          THEN 'ESTORNO'
          ELSE 'BAIXA'
          END
        , u.PCPC040_ESTCONF
        , u.USUARIO_SYSTEXTIL
        ORDER BY
          ll.SEQ_OPERACAO
        , 5 -- DT_MIN
        , 4 -- MOVIMENTO
        , 3 DESC -- LOTES
        , u.USUARIO_SYSTEXTIL
    '''
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)


def op_sortimento(cursor, op):
    header, fields, data, total = op_sortimentos(cursor, op, 't')
    return header, fields, data


def op_sortimentos(cursor, op, tipo):
    # Grade de OP
    grade = GradeQtd(cursor, [op])

    # tamanhos
    grade.col(
        id='TAMANHO',
        name='Tamanho',
        sql='''
            SELECT DISTINCT
              lote.PROCONF_SUBGRUPO TAMANHO
            , tam.ORDEM_TAMANHO SEQUENCIA_TAMANHO
            FROM PCPC_040 lote
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
            WHERE lote.ORDEM_PRODUCAO = %s
            ORDER BY
              2
        '''
        )

    # cores
    grade.row(
        id='SORTIMENTO',
        facade='DESCR',
        name='Cor',
        name_plural='Cores',
        sql='''
            SELECT
              lote.PROCONF_ITEM SORTIMENTO
            , lote.PROCONF_ITEM || ' - ' || max( p.DESCRICAO_15 ) DESCR
            FROM PCPC_040 lote
            LEFT JOIN basi_010 p
              ON p.NIVEL_ESTRUTURA = 1
             AND p.GRUPO_ESTRUTURA = lote.PROCONF_GRUPO
             AND p.ITEM_ESTRUTURA = lote.PROCONF_ITEM
            WHERE lote.ORDEM_PRODUCAO = %s
            GROUP BY
              lote.PROCONF_ITEM
            ORDER BY
              2
        '''
        )

    if tipo == 't':  # Total a produzir
        # sortimento
        grade.value(
            id='QUANTIDADE',
            sql='''
                SELECT
                  lote.PROCONF_SUBGRUPO TAMANHO
                , lote.PROCONF_ITEM SORTIMENTO
                , sum(lote.QTDE_PECAS_PROG ) QUANTIDADE
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
            '''
            )

    elif tipo == 'p':  # Perda
        # sortimento
        grade.value(
            id='QUANTIDADE',
            sql='''
                SELECT
                  lote.PROCONF_SUBGRUPO TAMANHO
                , lote.PROCONF_ITEM SORTIMENTO
                , sum(lote.QTDE_PERDAS ) QUANTIDADE
                FROM PCPC_040 lote
                LEFT JOIN BASI_220 tam
                  ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
                WHERE lote.ORDEM_PRODUCAO = %s
                GROUP BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_SUBGRUPO
                , lote.PROCONF_ITEM
                ORDER BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_ITEM
            '''
            )

    elif tipo == 'c':  # Conserto
        # sortimento
        grade.value(
            id='QUANTIDADE',
            sql='''
                SELECT
                  lote.PROCONF_SUBGRUPO TAMANHO
                , lote.PROCONF_ITEM SORTIMENTO
                , sum(lote.QTDE_CONSERTO ) QUANTIDADE
                FROM PCPC_040 lote
                LEFT JOIN BASI_220 tam
                  ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
                WHERE lote.ORDEM_PRODUCAO = %s
                GROUP BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_SUBGRUPO
                , lote.PROCONF_ITEM
                ORDER BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_ITEM
            '''
            )

    elif tipo == 's':  # Segunda qualidade
        # sortimento
        grade.value(
            id='QUANTIDADE',
            sql='''
                SELECT
                  lote.PROCONF_SUBGRUPO TAMANHO
                , lote.PROCONF_ITEM SORTIMENTO
                , sum(lote.QTDE_PECAS_2A ) QUANTIDADE
                FROM PCPC_040 lote
                LEFT JOIN BASI_220 tam
                  ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
                WHERE lote.ORDEM_PRODUCAO = %s
                  AND lote.SEQUENCIA_ESTAGIO
                      = COALESCE(
                          (
                            SELECT
                              MAX(ulote.SEQUENCIA_ESTAGIO)
                            FROM PCPC_040 ulote
                            WHERE ulote.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
                              AND ulote.ORDEM_CONFECCAO = lote.ORDEM_CONFECCAO
                              AND ulote.QTDE_PECAS_2A > 0
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
            '''
            )

    return (grade.table_data['header'], grade.table_data['fields'],
            grade.table_data['data'], grade.total)


def op_lotes(cursor, op):
    # Lotes ordenados por OS + referência + estágio
    return get_lotes(cursor, op=op, order='e')


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
    return get_os(cursor, op=op)


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
