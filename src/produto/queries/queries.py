import pandas as pd
from pprint import pprint

from django.core.cache import cache

from systextil.queries.produto.modelo import sql_modelostr_ref, sql_modeloint_ref
from utils.cache import timeout
from utils.functions import my_make_key_cache, fo2logger
from utils.functions.models.dictlist import dictlist, dictlist_lower
from utils.functions.queries import debug_cursor_execute


def produtos_n1_basic(cursor, param):
    tipo = param[0:2]
    qualidade = param[3:]
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
            AND (p.REFERENCIA like 'A%')
            ORDER BY
            p.REFERENCIA
        '''
    elif tipo == 'PB':
        sql = sql + '''
            AND (p.REFERENCIA like 'B%')
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
    debug_cursor_execute(cursor, sql)
    data = dictlist(cursor)
    return data


def ref_inform(cursor, ref):
    return nivel_ref_inform(cursor, 1, ref)


def ref_linha(cursor, ref):
    info = nivel_ref_inform(cursor, 1, ref, upper=False)
    df = pd.DataFrame(info)
    df = df.loc[:, ['ref', 'linha_produto']]
    return df.to_dict('records')


def dict_ref_val(cursor, ref, valor):
    info = nivel_ref_inform(cursor, 1, ref, upper=False)
    if len(info) == 0:
      return {}
    df = pd.DataFrame(info)
    return df.set_index('ref')[valor].to_dict()


def dict_ref_linha(cursor, ref):
    return dict_ref_val(cursor, ref, 'linha_produto')


def nivel_ref_inform(cursor, nivel, ref, upper=True):
    if isinstance(ref, tuple):
        refs = map(repr, ref)
        refs_join = ', '.join(refs)
    else:
        refs_join = repr(ref)

    sql = f"""
        WITH referencias AS
        ( SELECT
            sr.*
          FROM basi_030 sr
          WHERE sr.NIVEL_ESTRUTURA = {nivel}
            AND sr.REFERENCIA IN ({refs_join})
        )
        SELECT
          r.REFERENCIA REF
        , CASE WHEN r.REFERENCIA <= '99999' THEN 'PA'
          WHEN r.REFERENCIA < 'B0000' THEN 'PG'
          WHEN r.REFERENCIA < 'C0000' THEN 'PB'
          WHEN r.REFERENCIA < 'Z0000' THEN 'MD'
          ELSE 'MP'
          END TIPO
        , r.DESCR_REFERENCIA DESCR
        , ce.DESCR_CT_ESTOQUE
          || ' (' || r.CONTA_ESTOQUE || ')' CONTA_ESTOQUE
        , r.LINHA_PRODUTO
        , lin.DESCRICAO_LINHA
          || ' (' || r.LINHA_PRODUTO || ')' LINHA
        , r.COLECAO CODIGO_COLECAO
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
        , cl.FANTASIA_CLIENTE
          || ' (' || lpad(r.CGC_CLIENTE_9, 8, '0')
          || '/' || lpad(r.CGC_CLIENTE_4, 4, '0')
          || '-' || lpad(r.CGC_CLIENTE_2, 2, '0')
          || ') ' || cl.NOME_CLIENTE CLIENTE
        , r.RESPONSAVEL STATUS
        , COALESCE(
          CASE WHEN r.REFERENCIA < 'C0000' THEN
            CAST(
              {sql_modeloint_ref('r.REFERENCIA')}
              AS VARCHAR2(5) )
          ELSE
            ( SELECT
                CAST( MAX(
                  {sql_modeloint_ref('ec.GRUPO_ITEM')}
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
        , CASE WHEN EXISTS
          ( SELECT 
              rot.CODIGO_ESTAGIO
            FROM MQOP_050 rot
            JOIN obrf_070 serv
              ON serv.CODIGO_ESTAGIO = rot.CODIGO_ESTAGIO
            WHERE rot.GRUPO_ESTRUTURA = r.REFERENCIA
          ) THEN 'S' ELSE 'N' END TEM_OS
        FROM referencias r
        JOIN BASI_150 ce
          ON ce.CONTA_ESTOQUE = r.CONTA_ESTOQUE
        LEFT JOIN BASI_120 lin
          ON lin.NIVEL_ESTRUTURA = r.NIVEL_ESTRUTURA
         AND lin.LINHA_PRODUTO = r.LINHA_PRODUTO
        JOIN BASI_140 col
          ON col.COLECAO = r.COLECAO
        LEFT JOIN BASI_290 ac
          ON ac.NIVEL_ESTRUTURA = r.NIVEL_ESTRUTURA
         AND ac.ARTIGO = r.ARTIGO
        LEFT JOIN BASI_240 cf
          ON cf.CLASSIFIC_FISCAL = r.CLASSIFIC_FISCAL
        LEFT JOIN PEDI_010 cl
          ON cl.CGC_9 = r.CGC_CLIENTE_9
         and cl.CGC_4 = r.CGC_CLIENTE_4
         and cl.CGC_2 = r.CGC_CLIENTE_2
    """
    debug_cursor_execute(cursor, sql)
    if upper:
        return dictlist(cursor)
    else:
        return dictlist_lower(cursor)


def ref_utilizada_em(cursor, ref):
    # Totais por OP
    sql = f"""
        SELECT DISTINCT
          ec.GRUPO_ITEM REF
        , CASE WHEN ec.GRUPO_ITEM <= '99999' THEN 'PA'
          WHEN ec.GRUPO_ITEM < 'B0000' THEN 'PG'
          WHEN ec.GRUPO_ITEM < 'C0000' THEN 'PB'
          WHEN ec.GRUPO_ITEM < 'Z0000' THEN 'MD'
          ELSE 'MP'
          END TIPO
        , ec.ALTERNATIVA_ITEM ALTERNATIVA
        , r.RESPONSAVEL
        FROM BASI_050 ec
        JOIN BASI_030 r
          ON r.NIVEL_ESTRUTURA = ec.NIVEL_ITEM
         AND r.REFERENCIA = ec.GRUPO_ITEM
        WHERE ec.NIVEL_COMP = 1
          AND ec.GRUPO_COMP = '{ref}'
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def ref_cores(cursor, ref):
    return prod_cores(cursor, 1, ref)


def prod_cores(cursor, nivel, grupo):
    # Cores de produto
    sql = f"""
        SELECT DISTINCT
          c.ITEM_ESTRUTURA COR
        , c.DESCRICAO_15 DESCR
        FROM basi_010 c
        WHERE c.NIVEL_ESTRUTURA = {nivel}
          AND c.GRUPO_ESTRUTURA = '{grupo}'
        ORDER BY
          c.ITEM_ESTRUTURA
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def ref_tamanhos(cursor, ref):
    return prod_tamanhos(cursor, 1, ref)


def prod_tamanhos(cursor, nivel, grupo):
    # Tamanhos de produto
    sql = f"""
        SELECT DISTINCT
          t.TAMANHO_REF TAM
        , t.DESCR_TAM_REFER DESCR
        , tam.ORDEM_TAMANHO ORD
        , t.DESC_TAM_FICHA COMPL
        , t.LOTE_FABR_PECAS LOTE_PECAS
        FROM basi_020 t
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = t.TAMANHO_REF
        WHERE t.BASI030_NIVEL030 = {nivel}
          AND t.BASI030_REFERENC = '{grupo}'
        ORDER BY
          tam.ORDEM_TAMANHO
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def ref_roteiros(cursor, ref):
    # Totais por OP
    sql = f"""
        SELECT DISTINCT
          r.NUMERO_ALTERNATI
        , r.NUMERO_ROTEIRO
        , r.NUMERO_ALTERNATI || ' (' ||
          COALESCE( al.DESCRICAO, COALESCE( alg.DESCRICAO, '' ) ) || ')'
          ALTERNATIVA
        , r.NUMERO_ROTEIRO || ' (' ||
          COALESCE( ro.DESCRICAO,
            COALESCE( alg.DESCRICAO, '' ) ) || ')' ROTEIRO
        , r.SUBGRU_ESTRUTURA TAM
        , r.ITEM_ESTRUTURA COR
        FROM MQOP_050 r
        LEFT JOIN BASI_070 ro
          ON ro.ALTERNATIVA = r.NUMERO_ALTERNATI
         AND ro.ROTEIRO = r.NUMERO_ROTEIRO
         AND ro.NIVEL = r.NIVEL_ESTRUTURA
         AND ro.GRUPO = r.GRUPO_ESTRUTURA
         AND ro.SUBGRUPO = r.SUBGRU_ESTRUTURA
         AND ro.ITEM = r.ITEM_ESTRUTURA
        -- específico
        LEFT JOIN BASI_070 al -- cadastro de altern. de estrutura e de roteiro
          ON al.ROTEIRO = 0 -- seleciona cadastro de alternativas de estrutura
         AND al.ALTERNATIVA = r.NUMERO_ALTERNATI
         AND al.GRUPO = r.GRUPO_ESTRUTURA -- seleciona nome esclusivo da ref
        -- genérico
        LEFT JOIN BASI_070 alg -- cadastro de altern. de estrutura e de roteiro
          ON alg.ROTEIRO = 0 -- seleciona cadastro de alternativas de estrutura
         AND alg.ALTERNATIVA = r.NUMERO_ALTERNATI
         AND alg.DESCRICAO IS NOT NULL
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.GRUPO_ESTRUTURA = '{ref}'
        ORDER BY
          r.NUMERO_ALTERNATI
        , r.NUMERO_ROTEIRO
        , r.SUBGRU_ESTRUTURA
        , r.ITEM_ESTRUTURA
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def ref_1roteiro(cursor, ref, alternativa, roteiro, tamanho, cor):
    # Totais por OP
    sql = f"""
        SELECT
          r.SEQ_OPERACAO SEQ
        , r.CODIGO_OPERACAO || ' - ' || o.NOME_OPERACAO OPERACAO
        , r.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
        , CASE WHEN r.IND_ESTAGIO_GARGALO = 1
          THEN 'Gargalo'
          ELSE ' '
          END GARGALO
        , r.SEQUENCIA_ESTAGIO SEQ_EST
        FROM MQOP_050 r -- roteiro
        JOIN MQOP_005 e -- estagio
          ON e.CODIGO_ESTAGIO = r.CODIGO_ESTAGIO
        JOIN MQOP_040 o -- operacao
          ON o.CODIGO_OPERACAO = r.CODIGO_OPERACAO
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.GRUPO_ESTRUTURA = '{ref}'
          AND r.NUMERO_ALTERNATI = {alternativa}
          AND r.NUMERO_ROTEIRO = {roteiro}
          AND r.SUBGRU_ESTRUTURA = '{tamanho}'
          AND r.ITEM_ESTRUTURA = '{cor}'
        ORDER BY
          r.SEQ_OPERACAO
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def ref_estruturas(cursor, ref):
    return nivel_ref_estruturas(cursor, 1, ref)


def nivel_ref_estruturas(cursor, nivel, ref):
    # Totais por OP
    sql = f"""
        SELECT DISTINCT
          ia.ALTERNATIVA_ITEM ALTERNATIVA
        , ia.SUB_ITEM TAM
        , ia.ITEM_ITEM COR
        , COALESCE( al.DESCRICAO, COALESCE( alg.DESCRICAO, '' ) ) DESCR
        , COALESCE(
          ( SELECT
              LISTAGG(COALESCE(ec.GRUPO_COMP, ''), ', ')
              WITHIN GROUP (ORDER BY ec.ALTERNATIVA_ITEM) REF
            FROM BASI_050 ec -- componente de mesmo nivel
            WHERE ec.NIVEL_ITEM = ia.NIVEL_ITEM
              AND ec.GRUPO_ITEM = ia.GRUPO_ITEM
              AND ec.ALTERNATIVA_ITEM = ia.ALTERNATIVA_ITEM
              AND ec.SUB_ITEM = ia.SUB_ITEM
              AND ec.ITEM_ITEM = ia.ITEM_ITEM
              AND ec.NIVEL_COMP = ia.NIVEL_ITEM
          ), '-') REF
        , COALESCE(
          ( SELECT
              sum(
                CASE WHEN ep.GRUPO_ESTRUTURA IS NULL THEN 1 ELSE 0 END 
              )
            FROM BASI_050 e -- estrutura
            LEFT JOIN BASI_060 ep -- estrutura parte
              ON ep.GRUPO_ESTRUTURA = e.GRUPO_ITEM
            AND ep.SUBGRU_ESTRUTURA = e.SUB_ITEM
            AND ep.ITEM_ESTRUTURA = e.ITEM_ITEM
            AND ep.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
            AND ep.SEQUENCIA = e.SEQUENCIA
            WHERE 1=1
              AND e.NIVEL_ITEM = ia.NIVEL_ITEM
              AND e.GRUPO_ITEM = ia.GRUPO_ITEM
              AND e.SUB_ITEM = ia.SUB_ITEM
              AND e.ITEM_ITEM = ia.ITEM_ITEM  
              AND e.ALTERNATIVA_ITEM = ia.ALTERNATIVA_ITEM
              AND e.NIVEL_COMP = 2
          ), 0) FALTA_PARTE 
        , COALESCE(
          ( SELECT
              count(*)
            FROM BASI_050 e -- estrutura
            WHERE 1=1
              AND e.NIVEL_ITEM = ia.NIVEL_ITEM
              AND e.GRUPO_ITEM = ia.GRUPO_ITEM
              AND e.SUB_ITEM = ia.SUB_ITEM
              AND e.ITEM_ITEM = ia.ITEM_ITEM  
              AND e.ALTERNATIVA_ITEM = ia.ALTERNATIVA_ITEM
              AND e.NIVEL_COMP = 2
          ), 0) TECIDOS 
        FROM BASI_050 ia -- insumos de alternativa
        -- específico
        LEFT JOIN BASI_070 al -- cadastro de altern. de estrutura e de roteiro
          ON al.ROTEIRO = 0 -- seleciona cadastro de alternativas de estrutura
         AND al.ALTERNATIVA = ia.ALTERNATIVA_ITEM
         AND al.GRUPO = ia.GRUPO_ITEM -- seleciona nome esclusivo da referência
        -- genérico
        LEFT JOIN BASI_070 alg -- cadastro de altern. de estrutura e de roteiro
          ON alg.ROTEIRO = 0 -- seleciona cadastro de alternativas de estrutura
         AND alg.ALTERNATIVA = ia.ALTERNATIVA_ITEM
        WHERE ia.NIVEL_ITEM = {nivel}
          AND ia.GRUPO_ITEM = '{ref}'
        ORDER BY
          ia.ALTERNATIVA_ITEM
        , ia.SUB_ITEM
        , ia.ITEM_ITEM
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def refs_de_modelo(cursor, modelo, tipo=None):
    data = modelo_inform(cursor, modelo, tipo)
    return [m['REF'] for m in data]


def modelo_inform(cursor, modelo, tipo=None):
    filtra_tipo = ""
    if tipo:
        filtra_tipo = (
            f"""AND m.tipo = '{tipo.upper()}'
            """
        )

    sql = f"""
        WITH modelos AS (
        SELECT
          re.REF
        , COALESCE( r.DESCR_REFERENCIA, ' ' ) DESCR
        , CASE WHEN r.REFERENCIA <= '99999' THEN 'PA'
          WHEN r.REFERENCIA like 'A%' THEN 'PG'
          WHEN r.REFERENCIA like 'B%' THEN 'PB'
          WHEN r.REFERENCIA like 'Z%' THEN 'MP'
          ELSE 'MD'
          END TIPO
        , COALESCE( r.COLECAO_CLIENTE, ' ' ) COLECAO_CLIENTE
        , r.CGC_CLIENTE_9 CNPJ9
        , r.CGC_CLIENTE_4 CNPJ4
        , r.CGC_CLIENTE_2 CNPJ2
        , r.COLECAO CODIGO_COLECAO
        , r.COLECAO || ' - ' || col.DESCR_COLECAO COLECAO
        , cl.NOME_CLIENTE NOME
        , COALESCE( r.RESPONSAVEL, ' ' ) STATUS
        FROM
        (
        SELECT
          r.REFERENCIA REF
        FROM basi_030 r
        WHERE {sql_modelostr_ref('r.REFERENCIA')} = '{modelo}'
          AND r.REFERENCIA < 'C0000'
          AND r.NIVEL_ESTRUTURA = 1
        UNION
        SELECT DISTINCT
          ec.GRUPO_COMP REF
        FROM BASI_050 ec
        WHERE ec.NIVEL_ITEM = 1
          AND ec.NIVEL_COMP = 1
          AND {sql_modelostr_ref('ec.GRUPO_ITEM')} = '{modelo}'
          AND ec.GRUPO_ITEM < 'C0000'
        ) re
        JOIN basi_030 r
          ON r.REFERENCIA = re.REF
         AND r.NIVEL_ESTRUTURA = 1
        JOIN BASI_140 col
          ON col.COLECAO = r.COLECAO
        JOIN PEDI_010 cl
          ON cl.CGC_9 = r.CGC_CLIENTE_9
         and cl.CGC_4 = r.CGC_CLIENTE_4
         and cl.CGC_2 = r.CGC_CLIENTE_2
        ORDER BY
          NLSSORT(re.REF,'NLS_SORT=BINARY_AI')
        )
        SELECT
          m.*
        FROM modelos m
        WHERE 1=1
          {filtra_tipo} -- filtra_tipo
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def busca_cliente_de_produto(cursor, cliente):
    filtro = """--
          AND (  r.CGC_CLIENTE_9 LIKE '%{palavra}%'
              OR c.NOME_CLIENTE LIKE '%{palavra}%'
              OR c.FANTASIA_CLIENTE LIKE '%{palavra}%'
              )
    """.format(palavra=cliente)
    sql = """
        SELECT
          rr.CNPJ9
        , rr.CNPJ4
        , rr.CNPJ2
        , rr.CLIENTE
        FROM (
        SELECT DISTINCT
          count(*) conta
        , r.CGC_CLIENTE_9 CNPJ9
        , r.CGC_CLIENTE_4 CNPJ4
        , r.CGC_CLIENTE_2 CNPJ2
        , COALESCE(c.FANTASIA_CLIENTE, c.NOME_CLIENTE) CLIENTE
        FROM BASI_030 r
        LEFT JOIN PEDI_010 c
          ON c.CGC_9 = r.CGC_CLIENTE_9
         AND c.CGC_4 = r.CGC_CLIENTE_4
         AND c.CGC_2 = r.CGC_CLIENTE_2
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.REFERENCIA <= '99999'
          AND r.RESPONSAVEL IS NOT NULL
          {filtro} -- filtro
        GROUP BY
          r.CGC_CLIENTE_9
        , r.CGC_CLIENTE_4
        , r.CGC_CLIENTE_2
        , c.FANTASIA_CLIENTE
        , c.NOME_CLIENTE
        ORDER BY
          1 DESC
        ) rr
        where rownum = 1
    """.format(
        filtro=filtro,
        )
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)


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
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def get_roteiros_ref(cursor, ref):
    sql = """
        SELECT DISTINCT
          er.NIVEL_ESTRUTURA
        , er.GRUPO_ESTRUTURA
        , er.SUBGRU_ESTRUTURA
        , er.ITEM_ESTRUTURA
        , er.NUMERO_ALTERNATI
        , er.NUMERO_ROTEIRO
        , er.SEQ_OPERACAO
        , er.CODIGO_ESTAGIO
        , er.IND_ESTAGIO_GARGALO
        FROM MQOP_050 er
        WHERE er.NIVEL_ESTRUTURA = 1
          AND er.NUMERO_ROTEIRO = er.NUMERO_ALTERNATI
          AND er.GRUPO_ESTRUTURA = %s
        ORDER BY
          er.NUMERO_ROTEIRO
        , er.SEQ_OPERACAO
    """
    debug_cursor_execute(cursor, sql, [ref])
    return dictlist(cursor)


def mount_set_gargalo(roteiro, ref, tam, cor, estagio):
    return '''
        UPDATE SYSTEXTIL.MQOP_050
        SET
          IND_ESTAGIO_GARGALO = 1
        WHERE NIVEL_ESTRUTURA = '1'
          AND GRUPO_ESTRUTURA = '{ref}'
          AND SUBGRU_ESTRUTURA = '{tam}'
          AND ITEM_ESTRUTURA = '{cor}'
          AND NUMERO_ALTERNATI = {roteiro}
          AND NUMERO_ROTEIRO = {roteiro}
          AND CODIGO_ESTAGIO = {estagio}
    '''.format(
        roteiro=roteiro,
        ref=ref,
        tam=tam,
        cor=cor,
        estagio=estagio,
    )


def mount_unset_gargalo(roteiro, ref, tam, cor):
    return '''
        UPDATE SYSTEXTIL.MQOP_050
        SET
          IND_ESTAGIO_GARGALO = 0
        WHERE NIVEL_ESTRUTURA = '1'
          AND GRUPO_ESTRUTURA = '{ref}'
          AND SUBGRU_ESTRUTURA = '{tam}'
          AND ITEM_ESTRUTURA = '{cor}'
          AND NUMERO_ALTERNATI = {roteiro}
          AND NUMERO_ROTEIRO = {roteiro}
    '''.format(
        roteiro=roteiro,
        ref=ref,
        tam=tam,
        cor=cor,
    )


def mount_delete_estagios(roteiro, ref, tam, cor):
    return '''
        DELETE FROM SYSTEXTIL.MQOP_050
        WHERE NIVEL_ESTRUTURA = '1'
          AND GRUPO_ESTRUTURA = '{ref}'
          AND SUBGRU_ESTRUTURA = '{tam}'
          AND ITEM_ESTRUTURA = '{cor}'
          AND NUMERO_ALTERNATI = {roteiro}
          AND NUMERO_ROTEIRO = {roteiro}
    '''.format(
        roteiro=roteiro,
        ref=ref,
        tam=tam,
        cor=cor,
    )


def mount_inserts_estagios(roteiro, ref, tam, cor, estagios):
    ordem = 0
    inserts = []
    for estagio in estagios:
        ordem += 1
        seq = ordem * 10
        inserts.append('''
            INSERT INTO SYSTEXTIL.MQOP_050
            ( NIVEL_ESTRUTURA
            , GRUPO_ESTRUTURA
            , SUBGRU_ESTRUTURA
            , ITEM_ESTRUTURA
            , NUMERO_ALTERNATI
            , NUMERO_ROTEIRO
            , SEQ_OPERACAO
            , CODIGO_OPERACAO
            , MINUTOS
            , CODIGO_ESTAGIO
            , CENTRO_CUSTO
            , SEQUENCIA_ESTAGIO
            , ESTAGIO_ANTERIOR
            , ESTAGIO_DEPENDE
            , SEPARA_OPERACAO
            , MINUTOS_HOMEM
            , CCUSTO_HOMEM
            , NUMERO_CORDAS
            , NUMERO_ROLOS
            , VELOCIDADE
            , CODIGO_FAMILIA
            , OBSERVACAO
            , TIPO_PROCESSO
            , PECAS_1_HORA
            , PECAS_8_HORAS
            , CUSTO_MINUTO
            , PERC_EFICIENCIA
            , TEMPERATURA
            , TEMPO_LOTE_PRODUCAO
            , PECAS_LOTE_PRODUCAO
            , TIME_CELULA
            , CODIGO_APARELHO
            , PERC_EFIC_ROT
            , NUMERO_OPERADORAS
            , CONSIDERA_EFIC
            , SEQ_OPERACAO_AGRUPADORA
            , CODIGO_PARTE_PECA
            , SEQ_JUNCAO_PARTE_PECA
            , SITUACAO
            , PERC_PERDAS
            , PERC_CUSTOS
            , IND_ESTAGIO_GARGALO
            )
            VALUES
            ( '1'  -- NIVEL_ESTRUTURA
            , '{ref}'  -- GRUPO_ESTRUTURA
            , '{tam}'  -- SUBGRU_ESTRUTURA
            , '{cor}'  -- ITEM_ESTRUTURA
            , {roteiro}  -- NUMERO_ALTERNATI
            , {roteiro}  -- NUMERO_ROTEIRO
            , {seq}  -- SEQ_OPERACAO
            , {estagio}  -- CODIGO_OPERACAO
            , 0  -- MINUTOS
            , {estagio}  -- CODIGO_ESTAGIO
            , 0  -- CENTRO_CUSTO
            , {ordem}  -- SEQUENCIA_ESTAGIO
            , 0  -- ESTAGIO_ANTERIOR
            , 0  -- ESTAGIO_DEPENDE
            , NULL  -- SEPARA_OPERACAO
            , 0  -- MINUTOS_HOMEM
            , 0  -- CCUSTO_HOMEM
            , 0  -- NUMERO_CORDAS
            , 0  -- NUMERO_ROLOS
            , 0  -- VELOCIDADE
            , 0  -- CODIGO_FAMILIA
            , NULL  -- OBSERVACAO
            , 0  -- TIPO_PROCESSO
            , 0  -- PECAS_1_HORA
            , 0  -- PECAS_8_HORAS
            , 0  -- CUSTO_MINUTO
            , 0  -- PERC_EFICIENCIA
            , 0  -- TEMPERATURA
            , 0  -- TEMPO_LOTE_PRODUCAO
            , 0  -- PECAS_LOTE_PRODUCAO
            , 0  -- TIME_CELULA
            , NULL  -- CODIGO_APARELHO
            , 0  -- PERC_EFIC_ROT
            , 0  -- NUMERO_OPERADORAS
            , 0  -- CONSIDERA_EFIC
            , 0  -- SEQ_OPERACAO_AGRUPADORA
            , NULL  -- CODIGO_PARTE_PECA
            , 0  -- SEQ_JUNCAO_PARTE_PECA
            , 0  -- SITUACAO
            , 0  -- PERC_PERDAS
            , 0  -- PERC_CUSTOS
            , 0  -- IND_ESTAGIO_GARGALO
            )
        '''.format(
            roteiro=roteiro,
            ref=ref,
            tam=tam,
            cor=cor,
            estagio=estagio,
            ordem=ordem,
            seq=seq,
        ))
    return inserts


def get_refs(cursor):
    sql = """
        SELECT
          r.REFERENCIA
        FROM basi_030 r
        WHERE r.NIVEL_ESTRUTURA = 1
        ORDER BY
          r.REFERENCIA
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def info_xml(cursor, ref=None):
    filtra_ref = ''
    if ref != '':
        filtra_ref = '''--
          AND rtc.GRUPO_ESTRUTURA = '{}' '''.format(ref)

    sql = """
        SELECT
          rtc.GRUPO_ESTRUTURA REF
        , rtc.SUBGRU_ESTRUTURA TAM
        , rtc.ITEM_ESTRUTURA COR
        , CASE WHEN rtc.CODIGO_BARRAS IS NULL
                 OR rtc.CODIGO_BARRAS LIKE ' %'
          THEN 'SEM GTIN'
          ELSE rtc.CODIGO_BARRAS
          END GTIN
        , ic.REF_CLIENTE SKU_INFADPROD
        , rtc.PRODUTO_INTEGRACAO SKU_NARRATIVA
        , rtc.NARRATIVA
        , c.FANTASIA_CLIENTE
          || ' (' ||  c.NOME_CLIENTE
          || ' - ' || lpad(c.CGC_9, 8, '0')
          || '/' || lpad(c.CGC_4, 4, '0')
          || '-' || lpad(c.CGC_2, 2, '0')
          || ')' CLIENTE
        , c.CGC_9 CNPJ9
        FROM BASI_010 rtc -- item (ref+tam+cor)
        LEFT JOIN ESTQ_400 ic -- item do cliente
          ON ic.NIVEL_ESTRUTURA = rtc.NIVEL_ESTRUTURA
         AND ic.GRUPO_ESTRUTURA = rtc.GRUPO_ESTRUTURA
         AND ic.SUBGRUPO_ESTRUTURA = rtc.SUBGRU_ESTRUTURA
         AND ic.ITEM_ESTRUTURA = rtc.ITEM_ESTRUTURA
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = rtc.SUBGRU_ESTRUTURA
        JOIN BASI_030 r
          ON r.REFERENCIA = rtc.GRUPO_ESTRUTURA
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = r.CGC_CLIENTE_9
         AND c.CGC_4 = r.CGC_CLIENTE_4
         AND c.CGC_2 = r.CGC_CLIENTE_2
        WHERE rtc.NIVEL_ESTRUTURA = 1
          {filtra_ref} -- filtra_ref
        ORDER BY
          rtc.GRUPO_ESTRUTURA
        , rtc.ITEM_ESTRUTURA
        , t.ORDEM_TAMANHO
        , rtc.SUBGRU_ESTRUTURA
    """.format(
        filtra_ref=filtra_ref,
    )
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def por_cliente(cursor, cliente=None):
    filtra_cliente = ''
    if cliente != '':
        filtra_cliente = '''--
          AND c.FANTASIA_CLIENTE
              || ' (' ||  c.NOME_CLIENTE
              || ' - ' || lpad(c.CGC_9, 8, '0')
              || '/' || lpad(c.CGC_4, 4, '0')
              || '-' || lpad(c.CGC_2, 2, '0')
              || ')'
              LIKE '%{}%' '''.format(cliente)

    sql = """
        SELECT
          r.REFERENCIA REF
        , r.DESCR_REFERENCIA DESCR
        , c.FANTASIA_CLIENTE
          || ' (' ||  c.NOME_CLIENTE
          || ' - ' || lpad(c.CGC_9, 8, '0')
          || '/' || lpad(c.CGC_4, 4, '0')
          || '-' || lpad(c.CGC_2, 2, '0')
          || ')' CLIENTE
        FROM BASI_030 r
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = r.CGC_CLIENTE_9
         AND c.CGC_4 = r.CGC_CLIENTE_4
         AND c.CGC_2 = r.CGC_CLIENTE_2
        WHERE r.NIVEL_ESTRUTURA = 1
          {filtra_cliente} -- filtra_cliente
        ORDER BY
          r.REFERENCIA
    """.format(
        filtra_cliente=filtra_cliente,
    )
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def item_narrativa(cursor, nivel, ref, tam, cor):

    # key_cache = make_key_cache()
    key_cache = my_make_key_cache(
        'item_narrativa', nivel, ref, tam, cor)
    cached_result = cache.get(key_cache)
    if cached_result is not None:
        fo2logger.info('cached '+key_cache)
        return cached_result

    filtra_nivel = ''
    if nivel != '':
        filtra_nivel = f'''--
          AND i.NIVEL_ESTRUTURA = '{nivel}' '''

    filtra_ref = ''
    if ref != '':
        filtra_ref = f'''--
          AND i.GRUPO_ESTRUTURA = '{ref}' '''

    filtra_tam = ''
    if tam != '':
        filtra_tam = f'''--
          AND i.SUBGRU_ESTRUTURA = '{tam}' '''

    filtra_cor = ''
    if cor != '':
        filtra_cor = f'''--
          AND i.ITEM_ESTRUTURA = '{cor}' '''

    sql = f"""
        SELECT
          i.NARRATIVA
        FROM BASI_010 i
        WHERE 1 = 1
          {filtra_nivel} -- filtra_nivel
          {filtra_ref} -- filtra_ref
          {filtra_tam} -- filtra_tam
          {filtra_cor} -- filtra_cor
    """
    debug_cursor_execute(cursor, sql)
    result = dictlist(cursor)

    cache.set(key_cache, result, timeout=timeout.MINUTES_5)
    fo2logger.info('calculated '+key_cache)
    return result
