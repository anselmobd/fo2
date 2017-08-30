from django.db import models
from django.db import connections


def rows_to_dict_list(cursor):
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def produtos_n1_basic(param):
    tipo = param[0:2]
    qualidade = param[3:5]
    cursor = connections['so'].cursor()
    sql = '''
        SELECT
          ROWNUM
        , p.REFERENCIA
        , p.DESCR_REFERENCIA
        , ttt.TAMANHOS
        , ccc.CORES
        , eee.ESTRUTURAS
        , rrr.ROTEIROS
        FROM BASI_030 p
        LEFT JOIN
          ( SELECT
              tt.BASI030_NIVEL030
            , tt.BASI030_REFERENC
            , LISTAGG(tt.TAMANHO_REF, ', ')
              WITHIN GROUP (ORDER BY tt.ORDEM_TAMANHO) tamanhos
          FROM
          ( SELECT DISTINCT
              t.BASI030_NIVEL030
            , t.BASI030_REFERENC
            , t.TAMANHO_REF
            , tam.ORDEM_TAMANHO
            FROM basi_020 t
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = t.TAMANHO_REF
          )  tt
          GROUP BY
            tt.BASI030_NIVEL030
          , tt.BASI030_REFERENC
          ) ttt
        ON ttt.BASI030_NIVEL030 = p.NIVEL_ESTRUTURA
        AND ttt.BASI030_REFERENC = p.REFERENCIA
        LEFT JOIN
          ( SELECT
              cc.NIVEL_ESTRUTURA
            , cc.GRUPO_ESTRUTURA
            , LISTAGG(cc.ITEM_ESTRUTURA, ', ')
              WITHIN GROUP (ORDER BY cc.ITEM_ESTRUTURA) cores
          FROM
          ( SELECT DISTINCT
              c.NIVEL_ESTRUTURA
            , c.GRUPO_ESTRUTURA
            , c.ITEM_ESTRUTURA
            FROM basi_010 c
          )  cc
          GROUP BY
            cc.NIVEL_ESTRUTURA
          , cc.GRUPO_ESTRUTURA
          ) ccc
         ON ccc.NIVEL_ESTRUTURA = p.NIVEL_ESTRUTURA
        AND ccc.GRUPO_ESTRUTURA = p.REFERENCIA
        LEFT JOIN
          ( SELECT
              ee.NIVEL_ITEM
            , ee.GRUPO_ITEM
            , LISTAGG(ee.alternativa, ', ')
              WITHIN GROUP (ORDER BY ee.alternativa) estruturas
          FROM
          ( SELECT DISTINCT
              e.NIVEL_ITEM
            , e.GRUPO_ITEM
            , ( cast(e.ALTERNATIVA_ITEM AS VARCHAR2(2)) ||
                ( SELECT DISTINCT
                    '/' || md.GRUPO_COMP
                  FROM basi_050 md
                  WHERE md.NIVEL_ITEM = e.NIVEL_ITEM
                    AND md.GRUPO_ITEM = e.GRUPO_ITEM
                    AND md.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
                    AND md.NIVEL_COMP = 1
                    AND rownum = 1
                ) ||
                ( SELECT DISTINCT
                    '+' || md.GRUPO_COMP
                  FROM basi_050 md
                  WHERE md.NIVEL_ITEM = e.NIVEL_ITEM
                    AND md.GRUPO_ITEM = e.GRUPO_ITEM
                    AND md.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
                    AND md.NIVEL_COMP = 1
                    AND rownum = 1
                    AND md.GRUPO_COMP <>
                      ( SELECT DISTINCT
                          mdt.GRUPO_COMP
                        FROM basi_050 mdt
                        WHERE mdt.NIVEL_ITEM = e.NIVEL_ITEM
                          AND mdt.GRUPO_ITEM = e.GRUPO_ITEM
                          AND mdt.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
                          AND mdt.NIVEL_COMP = 1
                          AND rownum = 1
                      )
                )
              ) alternativa
            FROM basi_050 e
          )  ee
          GROUP BY
            ee.NIVEL_ITEM
          , ee.GRUPO_ITEM
          ) eee
         ON eee.NIVEL_ITEM = p.NIVEL_ESTRUTURA
        AND eee.GRUPO_ITEM = p.REFERENCIA
        LEFT JOIN
          ( SELECT
              rr.NIVEL_ESTRUTURA
            , rr.GRUPO_ESTRUTURA
            , LISTAGG(rr.roteiro, ', ')
            WITHIN GROUP (ORDER BY rr.roteiro) roteiros
          FROM
          ( SELECT DISTINCT
              r.NIVEL_ESTRUTURA
            , r.GRUPO_ESTRUTURA
            , r.NUMERO_ALTERNATI || '/' || r.NUMERO_ROTEIRO roteiro
            FROM mqop_050 r
          )  rr
          GROUP BY
            rr.NIVEL_ESTRUTURA
          , rr.GRUPO_ESTRUTURA
          ) rrr
        ON rrr.NIVEL_ESTRUTURA = p.NIVEL_ESTRUTURA
        AND rrr.GRUPO_ESTRUTURA = p.REFERENCIA
        WHERE p.NIVEL_ESTRUTURA = 1
    '''
    if qualidade == '':
        sql = sql + '''
            AND p.RESPONSAVEL is null
        '''
    else:
        sql = sql + '''
            AND p.RESPONSAVEL = '{}'
        '''.format(qualidade)
    if tipo == 'PA':
        sql = sql + '''
            AND p.REFERENCIA <= '99999'
            ORDER BY
            p.REFERENCIA
        '''
    elif tipo == 'PG':
        sql = sql + '''
            AND (p.REFERENCIA like 'A%' or p.REFERENCIA like 'B%')
            ORDER BY
            p.REFERENCIA
        '''
    elif tipo == 'MP':
        sql = sql + '''
            AND p.REFERENCIA like 'Z%'
            ORDER BY
            p.REFERENCIA
        '''
    else:
        sql = sql + '''
            AND p.REFERENCIA > 'A9999'
            ORDER BY
            p.REFERENCIA
        '''
    cursor.execute(sql)
    data = rows_to_dict_list(cursor)
    return data


def ref_inform(cursor, ref):
    # Totais por OP
    sql = """
        SELECT
          r.REFERENCIA REF
        , r.DESCR_REFERENCIA DESCR
        , ce.DESCR_CT_ESTOQUE
          || ' (' || r.CONTA_ESTOQUE || ')' CONTA_ESTOQUE
        , lin.DESCRICAO_LINHA
          || ' (' || r.LINHA_PRODUTO || ')' LINHA
        , col.DESCR_COLECAO
          || ' (' || r.COLECAO || ')' COLECAO
        , ac.DESCR_ARTIGO
          || ' (' || r.ARTIGO || ')' ARTIGO
        , r.CLASSIFIC_FISCAL || ' - ' || cf.DESCR_CLASS_FISC NCM
        , r.COLECAO_CLIENTE
        , r.CGC_CLIENTE_9 CNPJ9
        , r.CGC_CLIENTE_4 CNPJ4
        , r.CGC_CLIENTE_2 CNPJ2
        , cl.NOME_CLIENTE NOME
        , r.RESPONSAVEL STATUS
        , COALESCE(
          CASE WHEN r.REFERENCIA < 'C0000' THEN
            CAST( CAST( regexp_replace(r.REFERENCIA, '[^0-9]', '')
                        AS INTEGER ) AS VARCHAR2(5) )
          ELSE
            ( SELECT
                  CASE WHEN ec.GRUPO_ITEM IS NULL THEN ' '
                  ELSE CAST( CAST( regexp_replace(ec.GRUPO_ITEM, '[^0-9]', '')
                                   AS INTEGER ) AS VARCHAR2(5) )
                  END
                FROM BASI_050 ec
                WHERE ec.NIVEL_COMP = r.NIVEL_ESTRUTURA
                  AND ec.GRUPO_COMP = r.REFERENCIA
                  AND rownum = 1
            )
          END
          , ' ' ) MODELO
        FROM basi_030 r
        JOIN BASI_150 ce
          ON ce.CONTA_ESTOQUE = r.CONTA_ESTOQUE
        JOIN BASI_120 lin
          ON lin.NIVEL_ESTRUTURA = 1
         AND lin.LINHA_PRODUTO = r.LINHA_PRODUTO
        JOIN BASI_140 col
          ON col.COLECAO = r.COLECAO
        JOIN BASI_290 ac
          ON ac.NIVEL_ESTRUTURA = 1
         AND ac.ARTIGO = r.ARTIGO
        JOIN BASI_240 cf
          ON cf.CLASSIFIC_FISCAL = r.CLASSIFIC_FISCAL
        JOIN PEDI_010 cl
          ON cl.CGC_9 = r.CGC_CLIENTE_9
         and cl.CGC_4 = r.CGC_CLIENTE_4
        WHERE r.REFERENCIA = %s
    """
    cursor.execute(sql, [ref])
    return rows_to_dict_list(cursor)


def ref_cores(cursor, ref):
    return prod_cores(cursor, 1, ref)


def prod_cores(cursor, nivel, grupo):
    # Cores de produto
    sql = """
        SELECT DISTINCT
          c.ITEM_ESTRUTURA COR
        , c.DESCRICAO_15 DESCR
        FROM basi_010 c
        WHERE c.NIVEL_ESTRUTURA = %s
          AND c.GRUPO_ESTRUTURA = %s
    """
    cursor.execute(sql, [nivel, grupo])
    return rows_to_dict_list(cursor)


def ref_tamanhos(cursor, ref):
    return prod_tamanhos(cursor, 1, ref)


def prod_tamanhos(cursor, nivel, grupo):
    # Tamanhos de produto
    sql = """
        SELECT DISTINCT
          t.TAMANHO_REF TAM
        , t.DESCR_TAM_REFER DESCR
        , tam.ORDEM_TAMANHO ORD
        FROM basi_020 t
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = t.TAMANHO_REF
        WHERE t.BASI030_NIVEL030 = %s
          AND t.BASI030_REFERENC = %s
        ORDER BY
          tam.ORDEM_TAMANHO
    """
    cursor.execute(sql, [nivel, grupo])
    return rows_to_dict_list(cursor)


def ref_roteiros(cursor, ref):
    # Totais por OP
    sql = """
        SELECT DISTINCT
          r.NUMERO_ALTERNATI
        , r.NUMERO_ROTEIRO
        , r.NUMERO_ALTERNATI || '/' || r.NUMERO_ROTEIRO ROTEIRO
        , r.NUMERO_ALTERNATI || ' (' ||
          COALESCE( al.DESCRICAO, '' ) || ')' ALTERNATIVA
        , r.NUMERO_ROTEIRO || ' (' ||
          COALESCE( ro.DESCRICAO,
            COALESCE( al.DESCRICAO, '' ) ) || ')' OPERACOES
        FROM MQOP_050 r
        LEFT JOIN BASI_070 ro
          ON ro.ALTERNATIVA = r.NUMERO_ALTERNATI
         AND ro.ROTEIRO = r.NUMERO_ROTEIRO
         AND ro.NIVEL = r.NIVEL_ESTRUTURA
         AND ro.GRUPO = r.GRUPO_ESTRUTURA
        LEFT JOIN BASI_070 al
          ON al.ALTERNATIVA = r.NUMERO_ALTERNATI
         AND al.ROTEIRO = 0
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.GRUPO_ESTRUTURA = %s
        ORDER BY
          r.NUMERO_ALTERNATI
        , r.NUMERO_ROTEIRO
    """
    cursor.execute(sql, [ref])
    return rows_to_dict_list(cursor)


def ref_estruturas(cursor, ref):
    # Totais por OP
    sql = """
        SELECT DISTINCT
          e.ALTERNATIVA_ITEM ALTERNATIVA
        , COALESCE( al.DESCRICAO, '' ) DESCR
        , COALESCE(
          ( SELECT
              ec.GRUPO_COMP
            FROM BASI_050 ec
            WHERE ec.NIVEL_ITEM = e.NIVEL_ITEM
              AND ec.GRUPO_ITEM = e.GRUPO_ITEM
              AND ec.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
              AND ec.NIVEL_COMP = 1
              AND rownum = 1
          ), ' ') REF
        FROM BASI_050 e
        LEFT JOIN BASI_070 al
          ON al.ALTERNATIVA = e.ALTERNATIVA_ITEM
         AND al.ROTEIRO = 0
        WHERE e.NIVEL_ITEM = 1
          AND e.GRUPO_ITEM = %s
        ORDER BY
          e.ALTERNATIVA_ITEM
    """
    cursor.execute(sql, [ref])
    return rows_to_dict_list(cursor)


def modelo_inform(cursor, modelo):
    # Totais por OP
    sql = """
        SELECT
          re.REF
        , COALESCE( r.DESCR_REFERENCIA, ' ' ) DESCR
        , CASE WHEN r.REFERENCIA <= '99999' THEN 'PA'
          WHEN r.REFERENCIA like 'A%' or r.REFERENCIA like 'B%' THEN 'PG'
          WHEN r.REFERENCIA like 'Z%' THEN 'MP'
          ELSE 'MD'
          END TIPO
        , COALESCE( r.COLECAO_CLIENTE, ' ' ) COLECAO_CLIENTE
        , r.CGC_CLIENTE_9 CNPJ9
        , r.CGC_CLIENTE_4 CNPJ4
        , r.CGC_CLIENTE_2 CNPJ2
        , cl.NOME_CLIENTE NOME
        , COALESCE( r.RESPONSAVEL, ' ' ) STATUS
        FROM
        (
        SELECT
          r.REFERENCIA REF
        FROM basi_030 r
        WHERE regexp_replace(r.REFERENCIA, '[^0-9]', '')
              IN ('{}', '0{}', '00{}')
          AND r.REFERENCIA < 'C0000'
          AND r.NIVEL_ESTRUTURA = 1
        UNION
        SELECT DISTINCT
          ec.GRUPO_COMP REF
        FROM BASI_050 ec
        WHERE ec.NIVEL_ITEM = 1
          AND ec.NIVEL_COMP = 1
          AND regexp_replace(ec.GRUPO_ITEM, '[^0-9]', '')
              IN ('{}', '0{}', '00{}')
          AND ec.GRUPO_ITEM < 'C0000'
        ) re
        JOIN basi_030 r
          ON r.REFERENCIA = re.REF
         AND r.NIVEL_ESTRUTURA = 1
        JOIN PEDI_010 cl
          ON cl.CGC_9 = r.CGC_CLIENTE_9
         and cl.CGC_4 = r.CGC_CLIENTE_4
        ORDER BY
          NLSSORT(re.REF,'NLS_SORT=BINARY_AI')
    """
    sql = sql.format(modelo, modelo, modelo, modelo, modelo, modelo)
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
