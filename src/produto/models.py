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
    else:
        sql = sql + '''
            AND p.REFERENCIA > '99999'
            ORDER BY
            p.REFERENCIA
        '''
    cursor.execute(sql)
    data = rows_to_dict_list(cursor)
    return data
