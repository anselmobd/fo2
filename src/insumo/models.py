from django.db import models
from django.db import connections

from fo2.models import rows_to_dict_list

import produto.models


def item_count_nivel(cursor, ref, nivel=None):
    # verifica existêcia, unicidade e nível
    param = [ref, ]
    sql = """
        SELECT
          count(*) COUNT
        , min(r.NIVEL_ESTRUTURA) NIVEL
        FROM basi_030 r
        WHERE r.REFERENCIA = %s
    """
    if nivel is not None:
        sql = sql + """
            AND r.NIVEL_ESTRUTURA = %s
        """
        param.append(nivel)
    cursor.execute(sql, param)
    return rows_to_dict_list(cursor)


def ref_inform(cursor, nivel, ref):
    # Informações básicas
    sql = """
        SELECT
          r.DESCR_REFERENCIA DESCR
        , r.UNIDADE_MEDIDA || ' - ' || um.DESCR_UNIDADE UM
        , r.CONTA_ESTOQUE || ' - ' || ce.DESCR_CT_ESTOQUE CONTA_ESTOQUE
        , r.CLASSIFIC_FISCAL || ' - ' || cf.DESCR_CLASS_FISC NCM
        , r.CODIGO_CONTABIL || ' - ' || cc.DESCRICAO CODIGO_CONTABIL
        , r.LINHA_PRODUTO || ' - ' || lin.DESCRICAO_LINHA LINHA
        , r.COLECAO || ' - ' || col.DESCR_COLECAO COLECAO
        , r.ARTIGO  || ' - ' || ac.DESCR_ARTIGO ARTIGO
        , CASE
          WHEN r.TIPO_PRODUTO = 1
              THEN '1 - Tecido Normal (liso e estampado)'
          WHEN r.TIPO_PRODUTO = 2 THEN '2 - Tecido Listrado (com fio tinto)'
          WHEN r.TIPO_PRODUTO = 3 THEN '3 - Gola'
          WHEN r.TIPO_PRODUTO = 4 THEN '4 - Punho'
          WHEN r.TIPO_PRODUTO = 5 THEN '5 - Ribanas'
          WHEN r.TIPO_PRODUTO = 6
              THEN '6 - Retilínea(Golas, punhos, tiras, decotes)'
          END TIPO_PRODUTO
        FROM basi_030 r
        JOIN basi_200 um
          ON um.unidade_medida = r.UNIDADE_MEDIDA
        JOIN BASI_150 ce
          ON ce.CONTA_ESTOQUE = r.CONTA_ESTOQUE
        JOIN BASI_240 cf
          ON cf.CLASSIFIC_FISCAL = r.CLASSIFIC_FISCAL
        JOIN CONT_540 cc
          ON cc.TIPO_CONTABIL = 3
         AND cc.CODIGO_CONTABIL = r.CODIGO_CONTABIL
        LEFT JOIN BASI_120 lin
          ON lin.NIVEL_ESTRUTURA = 2
         AND lin.LINHA_PRODUTO = r.LINHA_PRODUTO
        LEFT JOIN BASI_140 col
          ON col.COLECAO = r.COLECAO
        LEFT JOIN BASI_290 ac
          ON ac.NIVEL_ESTRUTURA = 2
         AND ac.ARTIGO = r.ARTIGO
        WHERE r.NIVEL_ESTRUTURA = %s
         AND r.REFERENCIA = %s
    """
    cursor.execute(sql, [nivel, ref])
    return rows_to_dict_list(cursor)


def ref_cores(cursor, nivel, ref):
    return produto.models.prod_cores(cursor, nivel, ref)


def ref_tamanhos(cursor, nivel, ref):
    return produto.models.prod_tamanhos(cursor, nivel, ref)


def ref_parametros(cursor, nivel, ref):
    # Informações básicas
    sql = """
        SELECT
          p.SUBGRU_ESTRUTURA TAM
        , p.ITEM_ESTRUTURA COR
        , p.CODIGO_DEPOSITO || ' - ' || d.DESCRICAO DEPOSITO
        , p.ESTOQUE_MINIMO
        , p.ESTOQUE_MAXIMO
        , p.TEMPO_REPOSICAO LEAD
        FROM BASI_015 p
        JOIN BASI_205 d
          ON d.CODIGO_DEPOSITO = p.CODIGO_DEPOSITO
        WHERE p.NIVEL_ESTRUTURA = %s
          AND p.GRUPO_ESTRUTURA = %s
    """
    cursor.execute(sql, [nivel, ref])
    return rows_to_dict_list(cursor)


def ref_usado_em(cursor, nivel, ref):
    # Informações básicas
    sql = """
        SELECT DISTINCT
          CASE WHEN r.REFERENCIA <= '99999' THEN 'PA'
          WHEN r.REFERENCIA like 'A%' or r.REFERENCIA like 'B%' THEN 'PG'
          WHEN r.REFERENCIA like 'Z%' THEN 'MP'
          ELSE 'MD'
          END TIPO
        , e.GRUPO_ITEM REF
        , r.DESCR_REFERENCIA DESCR
        , e.ALTERNATIVA_ITEM ALTERNATIVA
        , e.CONSUMO
        , e.ESTAGIO || '-' || es.DESCRICAO ESTAGIO
        FROM BASI_050 e
        LEFT JOIN basi_030 r
          ON r.NIVEL_ESTRUTURA = e.NIVEL_ITEM
         AND r.REFERENCIA = e.GRUPO_ITEM
        LEFT JOIN MQOP_005 es
          ON es.CODIGO_ESTAGIO = e.ESTAGIO
        WHERE r.RESPONSAVEL IS NOT NULL
          AND e.NIVEL_ITEM = 1
          AND e.NIVEL_COMP = {}
          AND e.GRUPO_COMP = '{}'
        ORDER BY
          NLSSORT(e.GRUPO_ITEM,'NLS_SORT=BINARY_AI')
        , e.ALTERNATIVA_ITEM
    """
    sql = sql.format(nivel, ref)
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def lista_insumo(cursor, busca):
    # lista insumos
    filtro = ''
    for palavra in busca.split(' '):
        filtro += """
              AND (  r.REFERENCIA LIKE '%{}%'
                  OR r.DESCR_REFERENCIA LIKE '%{}%'
                  )
        """.format(palavra, palavra)
    sql = """
        SELECT
          rownum NUM
        , rr.NIVEL
        , rr.REF
        , rr.DESCR
        FROM (
        SELECT
          r.NIVEL_ESTRUTURA NIVEL
        , r.REFERENCIA REF
        , r.DESCR_REFERENCIA DESCR
        FROM BASI_030 r
        WHERE r.NIVEL_ESTRUTURA in (2, 9)
          {}
        ORDER BY
          r.NIVEL_ESTRUTURA
        , NLSSORT(r.REFERENCIA,'NLS_SORT=BINARY_AI')
        ) rr
    """.format(filtro)
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
