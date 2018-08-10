from django.db import models
from django.db import connections

from fo2.models import rows_to_dict_list


class Colecao(models.Model):
    colecao = models.IntegerField(primary_key=True)
    descr_colecao = models.CharField(
        max_length=100,
        verbose_name='Descrição')

    def __str__(self):
        return self.descr_colecao

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "BASI_140"
        verbose_name = "Coleção"


def produtos_n1_basic(param):
    tipo = param[0:2]
    qualidade = param[3:]
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
        , CASE WHEN r.REFERENCIA <= '99999' THEN 'PA'
          WHEN r.REFERENCIA < 'C0000' THEN 'PG'
          WHEN r.REFERENCIA < 'Z0000' THEN 'MD'
          ELSE 'MP'
          END TIPO
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
                WHERE ec.NIVEL_COMP = r.NIVEL_ESTRUTURA
                  AND ec.GRUPO_COMP = r.REFERENCIA
            )
          END
          , ' ' ) MODELO
          , r.NUMERO_MOLDE
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


def ref_utilizada_em(cursor, ref):
    # Totais por OP
    sql = """
        SELECT DISTINCT
          ec.GRUPO_ITEM REF
        , CASE WHEN ec.GRUPO_ITEM <= '99999' THEN 'PA'
          WHEN ec.GRUPO_ITEM < 'C0000' THEN 'PG'
          WHEN ec.GRUPO_ITEM < 'Z0000' THEN 'MD'
          ELSE 'MP'
          END TIPO
        , ec.ALTERNATIVA_ITEM ALTERNATIVA
        FROM BASI_050 ec
        JOIN BASI_030 r
          ON r.NIVEL_ESTRUTURA = ec.NIVEL_ITEM
         AND r.REFERENCIA = ec.GRUPO_ITEM
        WHERE ec.NIVEL_COMP = 1
          AND r.RESPONSAVEL IS NOT NULL
          AND ec.GRUPO_COMP = %s
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
        ORDER BY
          c.ITEM_ESTRUTURA
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
        , t.DESC_TAM_FICHA COMPL
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
        , r.NUMERO_ALTERNATI || ' (' ||
          COALESCE( al.DESCRICAO, '' ) || ')' ALTERNATIVA
        , r.NUMERO_ROTEIRO || ' (' ||
          COALESCE( ro.DESCRICAO,
            COALESCE( al.DESCRICAO, '' ) ) || ')' ROTEIRO
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


def ref_1roteiro(cursor, ref, alternativa, roteiro):
    # Totais por OP
    sql = """
        SELECT
          r.SEQ_OPERACAO SEQ
        , r.CODIGO_OPERACAO || ' - ' || o.NOME_OPERACAO OPERACAO
        , r.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
        , CASE WHEN r.IND_ESTAGIO_GARGALO = 1
          THEN 'Gargalo'
          ELSE ' '
          END GARGALO
        FROM MQOP_050 r -- roteiro
        JOIN MQOP_005 e -- estagio
          ON e.CODIGO_ESTAGIO = r.CODIGO_ESTAGIO
        JOIN MQOP_040 o -- operacao
          ON o.CODIGO_OPERACAO = r.CODIGO_OPERACAO
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.GRUPO_ESTRUTURA = %s
          AND r.NUMERO_ALTERNATI = %s
          AND r.NUMERO_ROTEIRO = %s
        ORDER BY
          r.SEQ_OPERACAO
    """
    cursor.execute(sql, [ref,  alternativa, roteiro])
    return rows_to_dict_list(cursor)


def ref_estruturas(cursor, ref):
    # Totais por OP
    sql = """
        SELECT DISTINCT
          ia.ALTERNATIVA_ITEM ALTERNATIVA
        , COALESCE( al.DESCRICAO, '' ) DESCR
        , COALESCE(
          ( SELECT
              LISTAGG(COALESCE(ec.GRUPO_COMP, ''), ', ')
              WITHIN GROUP (ORDER BY ec.ALTERNATIVA_ITEM) REF
            FROM BASI_050 ec
            WHERE ec.NIVEL_ITEM = ia.NIVEL_ITEM
              AND ec.GRUPO_ITEM = ia.GRUPO_ITEM
              AND ec.ALTERNATIVA_ITEM = ia.ALTERNATIVA_ITEM
              AND ec.NIVEL_COMP = 1
          ), ' ') REF
        FROM BASI_050 ia -- insumos de alternativa
        LEFT JOIN BASI_070 al -- cadastro de altern. de estrutura e de roteiro
          ON al.ROTEIRO = 0 -- seleciona cadastro de alternativas de estrutura
         AND al.ALTERNATIVA = ia.ALTERNATIVA_ITEM
        WHERE ia.NIVEL_ITEM = 1
          AND ia.GRUPO_ITEM = %s
        ORDER BY
          ia.ALTERNATIVA_ITEM
    """
    cursor.execute(sql, [ref])
    return rows_to_dict_list(cursor)


def ref_estrutura_comp(cursor, ref, alt):
    # Detalhando Estruturas
    sql = """
        SELECT DISTINCT
          e.SEQUENCIA
        , (
          SELECT
            LISTAGG(ee.ITEM_ITEM, ', ')
              WITHIN GROUP (ORDER BY ee.ITEM_ITEM)
          FROM BASI_050 ee
          WHERE ee.SEQUENCIA = e.SEQUENCIA
            AND ee.NIVEL_ITEM = e.NIVEL_ITEM
            AND ee.GRUPO_ITEM = e.GRUPO_ITEM
            AND ee.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
            AND ee.NIVEL_COMP = e.NIVEL_COMP
            AND ee.GRUPO_COMP = e.GRUPO_COMP
            AND ee.SUB_COMP = e.SUB_COMP
            AND ee.ITEM_COMP = e.ITEM_COMP
            AND ee.ALTERNATIVA_COMP = e.ALTERNATIVA_COMP
            AND ee.CONSUMO = e.CONSUMO
            AND ee.ESTAGIO = e.ESTAGIO
          ) COR_REF
        , e.NIVEL_COMP NIVEL
        , e.GRUPO_COMP REF
        , r.DESCR_REFERENCIA DESCR
        , e.SUB_COMP TAM
        , CASE WHEN cocv.SUB_ITEM IS NULL
          THEN
            CASE WHEN e.ITEM_COMP = '000000'
            THEN '= ='
            ELSE e.ITEM_COMP
            END
          ELSE
            CASE WHEN
              ( SELECT
                  count(DISTINCT coc1.ITEM_COMP)
                FROM BASI_040 coc1 -- comb. cor - verifica se é sempre a mesma
                WHERE e.ITEM_COMP = '000000'
                  AND coc1.SUB_ITEM = '000'
                  AND coc1.GRUPO_ITEM = e.GRUPO_ITEM
                  AND coc1.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
                  AND coc1.SEQUENCIA = e.SEQUENCIA
              ) = 1
            THEN '= ' ||
              CASE WHEN coc.ITEM_COMP = '000000'
              THEN '?'
              ELSE coc.ITEM_COMP
              END
            ELSE
              CASE WHEN e.NIVEL_COMP = 1
              THEN coc.ITEM_ITEM
              ELSE
                ( SELECT
                    LISTAGG(coc1.ITEM_ITEM, ', ')
                      WITHIN GROUP (ORDER BY coc1.ITEM_ITEM)
                  FROM BASI_040 coc1 -- comb. cor - com mesma tratucao
                  WHERE e.ITEM_COMP = '000000'
                    AND coc1.SUB_ITEM = '000'
                    AND coc1.GRUPO_ITEM = e.GRUPO_ITEM
                    AND coc1.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
                    AND coc1.SEQUENCIA = e.SEQUENCIA
                    AND coc1.ITEM_COMP = coc.ITEM_COMP
                )
              END
              || ' -> ' ||
              CASE WHEN coc.ITEM_COMP = '000000'
              THEN '?'
              ELSE coc.ITEM_COMP
              END
            END
          END COR
        , e.ALTERNATIVA_COMP ALTERN
        , e.CONSUMO
        , e.ESTAGIO || '-' || es.DESCRICAO ESTAGIO
        FROM BASI_050 e
        LEFT JOIN basi_030 r
          ON r.NIVEL_ESTRUTURA = e.NIVEL_COMP
         AND r.REFERENCIA = e.GRUPO_COMP
        LEFT JOIN BASI_040 cocv -- combinação cor - verifica se todos iguais
          ON e.ITEM_COMP = '000000'
         AND cocv.SUB_ITEM = '000'
         AND cocv.GRUPO_ITEM = e.GRUPO_ITEM
         AND cocv.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
         AND cocv.SEQUENCIA = e.SEQUENCIA
         AND cocv.ITEM_ITEM != cocv.ITEM_COMP
        LEFT JOIN BASI_040 coc -- combinação cor
          ON e.ITEM_COMP = '000000'
         AND cocv.SUB_ITEM IS NOT NULL
         AND coc.SUB_ITEM = '000'
         AND coc.GRUPO_ITEM = e.GRUPO_ITEM
         AND coc.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
         AND coc.SEQUENCIA = e.SEQUENCIA
        LEFT JOIN MQOP_005 es
          ON es.CODIGO_ESTAGIO = e.ESTAGIO
        WHERE e.NIVEL_ITEM = 1
          AND e.GRUPO_ITEM = %s
          AND e.ALTERNATIVA_ITEM = %s
        ORDER BY
          e.SEQUENCIA
        , 2
        , 7
    """
    cursor.execute(sql, [ref, alt])
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
         and cl.CGC_2 = r.CGC_CLIENTE_2
        ORDER BY
          NLSSORT(re.REF,'NLS_SORT=BINARY_AI')
    """
    sql = sql.format(modelo, modelo, modelo, modelo, modelo, modelo)
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def busca(cursor, busca, cor):
    filtro = ''
    for palavra in busca.split(' '):
        filtro += """--
              AND (  r.REFERENCIA LIKE '%{palavra}%'
                  OR r.DESCR_REFERENCIA LIKE '%{palavra}%'
                  OR r.RESPONSAVEL LIKE '%{palavra}%'
                  OR r.CGC_CLIENTE_9 LIKE '%{palavra}%'
                  OR c.NOME_CLIENTE LIKE '%{palavra}%'
                  OR c.FANTASIA_CLIENTE LIKE '%{palavra}%'
                  )
        """.format(palavra=palavra)
    filtro_cor = ''
    get_cor = ''
    if len(cor.strip()) == 0:
        get_cor = """--
            , '' COR
            , '' COR_DESC
        """
    else:
        get_cor = """--
            , cor.ITEM_ESTRUTURA COR
            , cor.DESCRICAO_15 COR_DESC
        """
    for palavra in cor.split(' '):
        filtro_cor += """--
              AND (  cor.ITEM_ESTRUTURA LIKE '%{palavra}%'
                  OR cor.DESCRICAO_15 LIKE '%{palavra}%'
                  )
        """.format(palavra=palavra)
    sql = """
        SELECT
          rownum NUM
        , rr.NIVEL
        , rr.REF
        , rr.COR
        , rr.COR_DESC
        , rr.TIPO
        , rr.DESCR
        , rr.RESP
        , rr.CNPJ9
        , rr.CNPJ4
        , rr.CNPJ2
        , rr.CLIENTE
        FROM (
        SELECT DISTINCT
          r.NIVEL_ESTRUTURA NIVEL
        , r.REFERENCIA REF
        , CASE WHEN r.REFERENCIA <= '99999' THEN 'PA'
          WHEN r.REFERENCIA like 'A%' or r.REFERENCIA like 'B%' THEN 'PG'
          WHEN r.REFERENCIA like 'Z%' THEN 'MP'
          ELSE 'MD'
          END TIPO
        , r.DESCR_REFERENCIA DESCR
        , r.RESPONSAVEL RESP
        , r.CGC_CLIENTE_9 CNPJ9
        , r.CGC_CLIENTE_4 CNPJ4
        , r.CGC_CLIENTE_2 CNPJ2
        , COALESCE(c.FANTASIA_CLIENTE, c.NOME_CLIENTE) CLIENTE
        {get_cor} -- get_cor
        FROM BASI_030 r
        LEFT JOIN BASI_010 cor
          ON cor.NIVEL_ESTRUTURA = r.NIVEL_ESTRUTURA
         AND cor.GRUPO_ESTRUTURA = r.REFERENCIA
        LEFT JOIN PEDI_010 c
          ON c.CGC_9 = r.CGC_CLIENTE_9
         AND c.CGC_4 = r.CGC_CLIENTE_4
         AND c.CGC_2 = r.CGC_CLIENTE_2
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.RESPONSAVEL IS NOT NULL
          {filtro} -- filtro
          {filtro_cor} -- filtro_cor
        ORDER BY
          NLSSORT(r.REFERENCIA,'NLS_SORT=BINARY_AI')
        ) rr
    """.format(
        filtro=filtro,
        filtro_cor=filtro_cor,
        get_cor=get_cor,
        )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def estr_estagio_de_insumo(cursor):
    # bursca problema de estágio de insumo
    sql = """
        SELECT DISTINCT
          e.NIVEL_ITEM NIVEL
        , e.GRUPO_ITEM REF
        , rp.DESCR_REFERENCIA DESCR
        , e.SUB_ITEM TAM
        , e.ITEM_ITEM COR
        , e.ALTERNATIVA_ITEM ALT
        , e.GRUPO_COMP
        , e.NIVEL_COMP || '-' || e.GRUPO_COMP ||
          ' (' || rm.DESCR_REFERENCIA  || ')' MP
        , e.SUB_COMP MP_TAM
        , e.ITEM_COMP MP_COR
        , e.ALTERNATIVA_COMP MP_ALT
        , e.ESTAGIO || ' - ' || es.DESCRICAO ESTAGIO
        , rp.RESPONSAVEL
        FROM (
        SELECT DISTINCT
          ref.NIVEL_ESTRUTURA
        , ref.REFERENCIA
        , ref.RESPONSAVEL
        , ref.DESCR_REFERENCIA
        , rpro.NUMERO_ALTERNATI
        FROM basi_030 REF -- produto
        LEFT JOIN MQOP_050 rpro -- roteiro de produto
          ON rpro.NIVEL_ESTRUTURA = ref.NIVEL_ESTRUTURA
         AND rpro.GRUPO_ESTRUTURA = ref.REFERENCIA
        WHERE ref.NIVEL_ESTRUTURA = 1
        --  AND REF.REFERENCIA = '0679A'
          AND rpro.NUMERO_ROTEIRO IS NOT NULL
          AND ref.RESPONSAVEL IS NOT NULL
        ) rp -- produto com algum roteiro
        JOIN BASI_050 e -- estrutura de produto
          ON e.NIVEL_ITEM = rp.NIVEL_ESTRUTURA
         AND e.GRUPO_ITEM = rp.REFERENCIA
         AND e.ALTERNATIVA_ITEM = rp.NUMERO_ALTERNATI
        LEFT JOIN basi_030 rm -- referencia matéria prima
          ON rm.NIVEL_ESTRUTURA = e.NIVEL_COMP
         AND rm.REFERENCIA = e.GRUPO_COMP
        LEFT JOIN MQOP_050 ri -- roteiro de produto com estágio do insumo
          ON ri.CODIGO_ESTAGIO = e.ESTAGIO
         AND ri.NIVEL_ESTRUTURA = e.NIVEL_ITEM
         AND ri.GRUPO_ESTRUTURA = e.GRUPO_ITEM
         AND ri.NUMERO_ALTERNATI = rp.NUMERO_ALTERNATI
        LEFT JOIN MQOP_005 es -- cadastro de estagios
          ON es.CODIGO_ESTAGIO = e.ESTAGIO
        WHERE e.NIVEL_ITEM = 1
          AND e.GRUPO_COMP not like 'DV%'
        --  AND r.SEQ_OPERACAO IS NOT NULL
          AND ri.SEQ_OPERACAO IS NULL
        ORDER BY
          e.GRUPO_ITEM
        , e.ALTERNATIVA_ITEM
        , e.GRUPO_COMP
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
