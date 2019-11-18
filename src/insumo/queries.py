import re
from pprint import pprint
from operator import itemgetter

from django.db import connections

from fo2.models import rows_to_dict_list, rows_to_dict_list_lower

import produto.queries


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
        SELECT DISTINCT
          r.DESCR_REFERENCIA DESCR
        , CASE WHEN f.NOME_FORNECEDOR IS NULL THEN ''
          ELSE
            f.NOME_FORNECEDOR
            || ' (' || lpad(f.FORNECEDOR9, 8, '0')
            || '/' || lpad(f.FORNECEDOR4, 4, '0')
            || '-' || lpad(f.FORNECEDOR2, 2, '0')
            || ')'
          END FORNECEDOR
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
          ON lin.NIVEL_ESTRUTURA = r.NIVEL_ESTRUTURA
         AND lin.LINHA_PRODUTO = r.LINHA_PRODUTO
        LEFT JOIN BASI_140 col
          ON col.COLECAO = r.COLECAO
        LEFT JOIN BASI_290 ac
          ON ac.NIVEL_ESTRUTURA = r.NIVEL_ESTRUTURA
         AND ac.ARTIGO = r.ARTIGO
        LEFT JOIN supr_100 ipc -- item de pedido de compra
          ON ipc.ITEM_100_NIVEL99 = r.NIVEL_ESTRUTURA
         AND ipc.ITEM_100_GRUPO = r.REFERENCIA
        LEFT JOIN supr_090 pc -- pedido de compra
          ON pc.PEDIDO_COMPRA = ipc.NUM_PED_COMPRA
        LEFT JOIN SUPR_010 f -- fornecedor
          ON f.FORNECEDOR9 = pc.FORN_PED_FORNE9
         AND f.FORNECEDOR4 = pc.FORN_PED_FORNE4
         AND f.FORNECEDOR2 = pc.FORN_PED_FORNE2
        WHERE r.NIVEL_ESTRUTURA = %s
         AND r.REFERENCIA = %s
         AND ( pc.DATETIME_PEDIDO IS NULL OR
               pc.DATETIME_PEDIDO =
               ( SELECT
                   max(pc2.DATETIME_PEDIDO)
                 FROM supr_090 pc2 -- pedido de compra
                 JOIN supr_100 ipc2 -- item de pedido de compra
                   ON ipc2.NUM_PED_COMPRA = pc2.PEDIDO_COMPRA
                 WHERE ipc2.ITEM_100_NIVEL99 = r.NIVEL_ESTRUTURA
                   AND ipc2.ITEM_100_GRUPO = r.REFERENCIA
               )
             )
    """
    cursor.execute(sql, [nivel, ref])
    return rows_to_dict_list(cursor)


def ref_cores(cursor, nivel, ref):
    return produto.queries.prod_cores(cursor, nivel, ref)


def ref_tamanhos(cursor, nivel, ref):
    return produto.queries.prod_tamanhos(cursor, nivel, ref)


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


def lista_insumo(cursor, busca, conta_estoque, tipo_conta_estoque):
    filtro = ''
    for palavra in busca.split(' '):
        filtro += """
              AND (  r.REFERENCIA LIKE '%{}%'
                  OR r.DESCR_REFERENCIA LIKE '%{}%'
                  )
        """.format(palavra, palavra)

    filtro_conta_estoque = ''
    if conta_estoque is not None:
        filtro_conta_estoque += """
              AND r.CONTA_ESTOQUE = {}
        """.format(conta_estoque.conta_estoque)

    filtro_tipo_conta_estoque = ''
    if tipo_conta_estoque != '':
        filtro_tipo_conta_estoque += """
              AND ce.TIPO_CONTA_ESTOQUE = {}
        """.format(tipo_conta_estoque)

    sql = """
        SELECT
          rownum NUM
        , rr.NIVEL
        , rr.REF
        , rr.DESCR
        , rr.CONTA_ESTOQUE
        FROM (
        SELECT
          r.NIVEL_ESTRUTURA NIVEL
        , r.REFERENCIA REF
        , r.DESCR_REFERENCIA DESCR
        , r.CONTA_ESTOQUE || '-' || ce.ce.DESCR_CT_ESTOQUE CONTA_ESTOQUE
        FROM BASI_030 r
        LEFT JOIN BASI_150 ce
          ON ce.CONTA_ESTOQUE = r.CONTA_ESTOQUE
        WHERE r.NIVEL_ESTRUTURA in (2, 9)
          {filtro} -- filtro
          {filtro_conta_estoque} -- filtro_conta_estoque
          {filtro_tipo_conta_estoque} -- filtro_tipo_conta_estoque
        ORDER BY
          r.NIVEL_ESTRUTURA
        , NLSSORT(r.REFERENCIA,'NLS_SORT=BINARY_AI')
        ) rr
    """.format(
        filtro=filtro,
        filtro_conta_estoque=filtro_conta_estoque,
        filtro_tipo_conta_estoque=filtro_tipo_conta_estoque,
    )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def necessidade(
        cursor, op, data_corte, data_corte_ate, periodo_corte,
        data_compra, data_compra_ate, periodo_compra,
        insumo, conta_estoque,
        ref, conta_estoque_ref, colecao, quais):
    filtro_op = ''
    if op:
        filtro_op = \
            "AND o.ORDEM_PRODUCAO = '{op}'".format(
                op=op)

    filtro_data_corte = ''
    if data_corte:
        filtro_data_corte = \
            "AND o.DATA_ENTRADA_CORTE >= '{data_corte}'".format(
                data_corte=data_corte)

    filtro_data_corte_ate = ''
    if data_corte_ate:
        filtro_data_corte_ate = \
            "AND o.DATA_ENTRADA_CORTE <= '{data_corte_ate}'".format(
                data_corte_ate=data_corte_ate)
    elif data_corte:
        filtro_data_corte_ate = \
            "AND o.DATA_ENTRADA_CORTE <= '{data_corte}'".format(
                data_corte=data_corte)

    filtro_periodo_corte = ''
    if periodo_corte:
        filtro_periodo_corte = \
            "AND pcorte.PERIODO_PRODUCAO = '{periodo_corte}'".format(
                periodo_corte=periodo_corte)

    filtro_data_compra = ''
    if data_compra:
        filtro_data_compra = """
            AND ( o.DATA_ENTRADA_CORTE
                - 7
                - coalesce(parm.TEMPO_REPOSICAO, 0)
                )
                >= '{data_compra}'""".format(
                    data_compra=data_compra)

    filtro_data_compra_ate = ''
    if data_compra_ate:
        filtro_data_compra_ate = """
            AND ( o.DATA_ENTRADA_CORTE
                - 7
                - coalesce(parm.TEMPO_REPOSICAO, 0)
                )
                <= '{data_compra_ate}'""".format(
                data_compra_ate=data_compra_ate)
    elif data_compra:
        filtro_data_compra_ate = """
            AND ( o.DATA_ENTRADA_CORTE
                - 7
                - coalesce(parm.TEMPO_REPOSICAO, 0)
                )
                <= '{data_compra}'""".format(
                data_compra=data_compra)

    filtro_periodo_compra = ''
    if periodo_compra:
        filtro_periodo_compra = \
            "AND pcompra.PERIODO_PRODUCAO = '{periodo_compra}'".format(
                periodo_compra=periodo_compra)

    filtro_insumo = ''
    if insumo:
        filtro_insumo = \
            "AND ia.GRUPO_COMP = '{insumo}'".format(
                insumo=insumo)

    filtro_conta_estoque = ''
    if conta_estoque:
        filtro_conta_estoque = \
            "AND r.CONTA_ESTOQUE = '{conta_estoque}'".format(
                conta_estoque=conta_estoque.conta_estoque)

    filtro_ref = ''
    if ref:
        filtro_ref = \
            "AND o.REFERENCIA_PECA = '{ref}'".format(
                ref=ref)

    filtro_conta_estoque_ref = ''
    if conta_estoque_ref:
        filtro_conta_estoque_ref = \
            "AND ref.CONTA_ESTOQUE = '{conta_estoque_ref}'".format(
                conta_estoque_ref=conta_estoque_ref.conta_estoque)

    filtro_colecao = ''
    if colecao:
        filtro_colecao = \
            "AND ref.COLECAO = '{colecao}'".format(
                colecao=colecao.colecao)

    filtro_insumos = ''
    quais_insumos = ''
    if quais == 'a':
        quais_insumos = """
            ( l.QTDE_PECAS_PROG
            - l.QTDE_PECAS_PROD
            - l.QTDE_PECAS_2A
            - l.QTDE_PERDAS
            - l.QTDE_CONSERTO
            )
        """
    elif quais == 'd':
        filtro_insumos = """
            AND (  ia.NIVEL_COMP = 2
                OR l.QTDE_EM_PRODUCAO_PACOTE <> l.QTDE_PECAS_PROG
                OR ( l.QTDE_EM_PRODUCAO_PACOTE = l.QTDE_PECAS_PROG
                   AND e.CODIGO_DEPOSITO <> 0
                   )
                )
        """
        quais_insumos = """
            ( l.QTDE_PECAS_PROG
            - l.QTDE_PECAS_PROD
            - l.QTDE_PECAS_2A
            - l.QTDE_PERDAS
            - l.QTDE_CONSERTO
            - CASE WHEN l.QTDE_EM_PRODUCAO_PACOTE <>
                        l.QTDE_PECAS_PROG
                    AND e.CODIGO_DEPOSITO = 0
              THEN
                l.QTDE_EM_PRODUCAO_PACOTE
              ELSE
                0
              END
            )
        """
    else:
        quais_insumos = """
            ( l.QTDE_PECAS_PROG )
        """

    # lista insumos
    sql = """
        WITH NESSECIDADE AS (
        SELECT
          ia.NIVEL_COMP NIVEL
        , ia.GRUPO_COMP REF
        , CASE WHEN ia.ITEM_COMP = '000000'
          THEN coc.ITEM_COMP
          ELSE ia.ITEM_COMP
          END COR
        , CASE WHEN ia.SUB_COMP = '000'
          THEN cot.SUB_COMP
          ELSE ia.SUB_COMP
          END TAM
        , coalesce(parm.ESTOQUE_MINIMO, 0) STQ_MIN
        , coalesce(parm.TEMPO_REPOSICAO, 0) REPOSICAO
        , r.DESCR_REFERENCIA DESCR
        , r.UNIDADE_MEDIDA UNID
        , o.REFERENCIA_PECA REFP
        , o.ORDEM_PRODUCAO OP
        , sum( ia.CONSUMO *
               ( {quais_insumos}
               )
             ) QTD
        FROM PCPC_020 o -- OP
        JOIN PCPC_040 l -- lote
          ON l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
        LEFT JOIN PCPC_010 pcorte
          ON pcorte.AREA_PERIODO = 1
         AND o.DATA_ENTRADA_CORTE >= pcorte.DATA_INI_PERIODO
         AND o.DATA_ENTRADA_CORTE <= pcorte.DATA_FIM_PERIODO
        JOIN BASI_050 ia -- insumos de alternativa
          ON ia.NIVEL_ITEM = 1
         AND ia.NIVEL_COMP <> 1
         AND ia.GRUPO_ITEM = o.REFERENCIA_PECA
         AND (ia.SUB_ITEM = l.PROCONF_SUBGRUPO OR ia.SUB_ITEM = '000')
         AND (ia.ITEM_ITEM = l.PROCONF_ITEM OR ia.ITEM_ITEM = '000000')
         AND ia.ALTERNATIVA_ITEM = o.ALTERNATIVA_PECA
         AND ia.ESTAGIO = l.CODIGO_ESTAGIO
        LEFT JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = ia.ESTAGIO
        LEFT JOIN BASI_040 cot -- combinação tamanho
          ON ia.SUB_COMP = '000'
         AND cot.GRUPO_ITEM = ia.GRUPO_ITEM
         AND cot.SUB_ITEM = l.PROCONF_SUBGRUPO
         AND cot.ITEM_ITEM = ia.ITEM_ITEM
         AND cot.ALTERNATIVA_ITEM = ia.ALTERNATIVA_ITEM
         AND cot.SEQUENCIA = ia.SEQUENCIA
        LEFT JOIN BASI_040 coc -- combinação cor
          ON ia.ITEM_COMP = '000000'
         AND coc.GRUPO_ITEM = ia.GRUPO_ITEM
         AND coc.SUB_ITEM = ia.SUB_ITEM
         AND coc.ITEM_ITEM = l.PROCONF_ITEM
         AND coc.ALTERNATIVA_ITEM = ia.ALTERNATIVA_ITEM
         AND coc.SEQUENCIA = ia.SEQUENCIA
        JOIN basi_030 r -- referencia
          ON r.NIVEL_ESTRUTURA = ia.NIVEL_COMP
         AND r.REFERENCIA = ia.GRUPO_COMP
        LEFT JOIN BASI_015 parm -- parâmetros de item
          ON parm.NIVEL_ESTRUTURA = ia.NIVEL_COMP
         AND parm.GRUPO_ESTRUTURA = ia.GRUPO_COMP
         AND parm.SUBGRU_ESTRUTURA = CASE WHEN ia.SUB_COMP = '000'
             THEN cot.SUB_COMP
             ELSE ia.SUB_COMP
             END
         AND parm.ITEM_ESTRUTURA = CASE WHEN ia.ITEM_COMP = '000000'
             THEN coc.ITEM_COMP
             ELSE ia.ITEM_COMP
             END
        LEFT JOIN PCPC_010 pcompra
          ON pcompra.AREA_PERIODO = 1
         AND ( o.DATA_ENTRADA_CORTE
             - 7
             - coalesce(parm.TEMPO_REPOSICAO, 0)
             ) >= pcompra.DATA_INI_PERIODO
         AND ( o.DATA_ENTRADA_CORTE
             - 7
             - coalesce(parm.TEMPO_REPOSICAO, 0)
             ) <= pcompra.DATA_FIM_PERIODO
        JOIN basi_030 ref -- referencia
          ON ref.NIVEL_ESTRUTURA = 1
         AND ref.REFERENCIA = o.REFERENCIA_PECA
        WHERE o.SITUACAO IN (2, 4)
        --  AND (ia.NIVEL_COMP = 2 OR e.CODIGO_DEPOSITO <> 0)
          {filtro_insumos} -- filtro_insumos
        --  AND ( l.QTDE_PECAS_PROG - l.QTDE_PECAS_PROD - l.QTDE_PECAS_2A
        --  - l.QTDE_PERDAS - l.QTDE_CONSERTO
        --  ) > 0
            AND (
              {quais_insumos} -- quais_insumos
            ) > 0
          {filtro_op} -- filtro_op
        --  AND o.DATA_ENTRADA_CORTE >= TO_DATE('01/01/2018','DD/MM/YYYY')
        --  AND o.DATA_ENTRADA_CORTE <= TO_DATE('01/01/2019','DD/MM/YYYY')
          {filtro_data_corte} -- filtro_data_corte
          {filtro_data_corte_ate} -- filtro_data_corte_ate
          {filtro_periodo_corte} -- filtro_periodo_corte
          {filtro_data_compra} -- filtro_data_compra
          {filtro_data_compra_ate} -- filtro_data_compra_ate
          {filtro_periodo_compra} -- filtro_periodo_compra
          {filtro_insumo} -- filtro_insumo
          {filtro_conta_estoque} -- filtro_conta_estoque
          {filtro_ref} -- filtro_ref
          {filtro_conta_estoque_ref} -- filtro_conta_estoque_ref
          {filtro_colecao} --filtro_colecao
        GROUP BY
          ia.NIVEL_COMP
        , ia.GRUPO_COMP
        , CASE WHEN ia.ITEM_COMP = '000000'
          THEN coc.ITEM_COMP
          ELSE ia.ITEM_COMP
          END
        , CASE WHEN ia.SUB_COMP = '000'
          THEN cot.SUB_COMP
          ELSE ia.SUB_COMP
          END
        , parm.ESTOQUE_MINIMO
        , parm.TEMPO_REPOSICAO
        , r.DESCR_REFERENCIA
        , r.UNIDADE_MEDIDA
        , o.REFERENCIA_PECA
        , o.ORDEM_PRODUCAO
        ORDER BY
          ia.NIVEL_COMP
        , ia.GRUPO_COMP
        , 3
        , 4
        , o.REFERENCIA_PECA
        , o.ORDEM_PRODUCAO
        )
        SELECT
          n.NIVEL
        , n.REF
        , n.DESCR
        , n.COR
        , n.TAM
        , n.UNID
        , n.STQ_MIN
        , n.REPOSICAO
        , REPLACE(
            REGEXP_REPLACE(
              LISTAGG('#'||n.REFP, ', ')
              WITHIN GROUP (ORDER BY n.REFP)
            , '([^,]+)(, \1)+'
            , '\1'
            )
          , '#'
          , ''
          )
          AS REFS
        , REPLACE(
            REGEXP_REPLACE(
              LISTAGG('#'||n.OP, ', ')
              WITHIN GROUP (ORDER BY n.OP)
            , '([^,]+)(, \1)+'
            , '\1'
            )
          , '#'
          , ''
          )
          AS OPS
        , sum( n.QTD ) QTD
        FROM NESSECIDADE n
        GROUP BY
          n.NIVEL
        , n.REF
        , n.DESCR
        , n.COR
        , n.TAM
        , n.UNID
        , n.STQ_MIN
        , n.REPOSICAO
        ORDER BY
          n.NIVEL
        , n.REF
        , n.COR
        , n.TAM
    """.format(
        filtro_op=filtro_op,
        filtro_data_corte=filtro_data_corte,
        filtro_data_corte_ate=filtro_data_corte_ate,
        filtro_periodo_corte=filtro_periodo_corte,
        filtro_data_compra=filtro_data_compra,
        filtro_data_compra_ate=filtro_data_compra_ate,
        filtro_periodo_compra=filtro_periodo_compra,
        filtro_insumo=filtro_insumo,
        filtro_conta_estoque=filtro_conta_estoque,
        filtro_ref=filtro_ref,
        filtro_conta_estoque_ref=filtro_conta_estoque_ref,
        filtro_colecao=filtro_colecao,
        filtro_insumos=filtro_insumos,
        quais_insumos=quais_insumos)
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def receber(cursor, insumo, conta_estoque, recebimento):
    filtro_insumo = ''
    if insumo:
        filtro_insumo = \
            "AND x.ITEM_100_GRUPO = '{insumo}'".format(
                insumo=insumo)

    filtro_conta_estoque = ''
    if conta_estoque:
        filtro_conta_estoque = \
            "AND r.CONTA_ESTOQUE = '{conta_estoque}'".format(
                conta_estoque=conta_estoque.conta_estoque)

    filtro_recebimento = ''
    if recebimento == 'a':
        filtro_recebimento = """
            AND (
              CASE WHEN (
                CASE WHEN pc.COD_CANCELAMENTO = 0
                  THEN x.QTDE_SALDO_ITEM
                  ELSE 0 END
                / x.QTDE_PEDIDA_ITEM
                ) <= 0.05
              THEN 0
              ELSE
                CASE WHEN pc.COD_CANCELAMENTO = 0
                  THEN x.QTDE_SALDO_ITEM
                  ELSE 0 END
              END
            ) > 0
        """

    sql = """
        SELECT
          x.ITEM_100_NIVEL99 NIVEL
        , x.ITEM_100_GRUPO REF
        , r.DESCR_REFERENCIA DESCR
        , x.ITEM_100_SUBGRUPO TAM
        , x.ITEM_100_ITEM COR
        , x.DATA_PREV_ENTR DT_ENTREGA
        , sum(x.QTDE_PEDIDA_ITEM) QTD_PEDIDA
        , sum(x.QTDE_PEDIDA_ITEM)
          - sum(x.QTDE_SALDO_ITEM) QTD_RECEBIDA
        , ROUND(
            (sum(x.QTDE_PEDIDA_ITEM) - sum(x.QTDE_SALDO_ITEM))
            / sum(x.QTDE_PEDIDA_ITEM) * 100
          , 1) P_RECEBIDO
          , sum(
              GREATEST(
                CASE WHEN pc.COD_CANCELAMENTO = 0
                  THEN x.QTDE_SALDO_ITEM
                  ELSE 0 END
              , 0)
            ) QTD_A_RECEBER
        , ROUND(
            sum(
              GREATEST(
                CASE WHEN pc.COD_CANCELAMENTO = 0
                  THEN x.QTDE_SALDO_ITEM
                  ELSE 0 END
              , 0)
            ) / sum(x.QTDE_PEDIDA_ITEM) * 100
          , 1) P_A_RECEBER
        , REPLACE(
            REGEXP_REPLACE(
              LISTAGG('#'||x.NUM_PED_COMPRA, ', ')
              WITHIN GROUP (ORDER BY x.NUM_PED_COMPRA)
            , '([^,]+)(, @)+'
            , '@'
            )
          , '#'
          , ''
          )
          AS PEDIDOS
        FROM SUPR_100 x -- item de pedido de compra
        JOIN SUPR_090 pc -- pedido de compra
          ON pc.PEDIDO_COMPRA = x.NUM_PED_COMPRA
        JOIN basi_030 r -- referencia
          ON r.NIVEL_ESTRUTURA = x.ITEM_100_NIVEL99
         AND r.REFERENCIA = x.ITEM_100_GRUPO
        WHERE 1=1
          {filtro_insumo} -- filtro_insumo
          {filtro_conta_estoque} -- filtro_conta_estoque
          {filtro_recebimento} -- filtro_recebimento
        GROUP BY
          x.ITEM_100_NIVEL99
        , x.ITEM_100_GRUPO
        , r.DESCR_REFERENCIA
        , x.ITEM_100_SUBGRUPO
        , x.ITEM_100_ITEM
        , x.DATA_PREV_ENTR
        ORDER BY
          x.ITEM_100_NIVEL99
        , x.ITEM_100_GRUPO
        , x.ITEM_100_SUBGRUPO
        , x.ITEM_100_ITEM
        , x.DATA_PREV_ENTR
    """.format(
        filtro_insumo=filtro_insumo,
        filtro_conta_estoque=filtro_conta_estoque,
        filtro_recebimento=filtro_recebimento)
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def estoque(cursor, insumo, conta_estoque):
    filtro_insumo = ''
    if insumo:
        filtro_insumo = \
            "AND e.CDITEM_GRUPO = '{insumo}'".format(
                insumo=insumo)

    filtro_conta_estoque = ''
    if conta_estoque:
        filtro_conta_estoque = \
            "AND r.CONTA_ESTOQUE = '{conta_estoque}'".format(
                conta_estoque=conta_estoque.conta_estoque)

    sql = """
        SELECT
          e.CDITEM_NIVEL99 NIVEL
        , e.CDITEM_GRUPO REF
        , r.DESCR_REFERENCIA DESCR
        , e.CDITEM_SUBGRUPO TAM
        , e.CDITEM_ITEM COR
        , r.UNIDADE_MEDIDA UNID
        , e.DEPOSITO
        , d.DESCRICAO
        , e.QTDE_ESTOQUE_ATU QUANT
        , e.DATA_ULT_ENTRADA ULT_ENTRADA
        , e.DATA_ULT_SAIDA ULT_SAIDA
        , e.DT_INVENTARIO
        --, e.*
        FROM ESTQ_040 e -- estoque por depósito
        JOIN basi_030 r -- referencia
          ON r.NIVEL_ESTRUTURA = e.CDITEM_NIVEL99
         AND r.REFERENCIA = e.CDITEM_GRUPO
        JOIN BASI_205 d -- cadastro de depósitos
          ON d.CODIGO_DEPOSITO = e.DEPOSITO
        WHERE 1=1
          {filtro_insumo} -- filtro_insumo
          {filtro_conta_estoque} -- filtro_conta_estoque
        ORDER BY
          e.CDITEM_NIVEL99
        , e.CDITEM_GRUPO
        , e.CDITEM_SUBGRUPO
        , e.CDITEM_ITEM
        , e.DEPOSITO
    """.format(
        filtro_insumo=filtro_insumo,
        filtro_conta_estoque=filtro_conta_estoque)
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def mapa_refs(cursor, insumo, conta_estoque, necessidade):
    filtro_insumo = ''
    if insumo:
        if len(insumo) == 5:
            filtro_insumo = \
                "AND ia.GRUPO_COMP = '{insumo}'".format(
                    insumo=insumo)
        else:
            filtro_insumo = \
                "AND ia.GRUPO_COMP LIKE '%{insumo}%'".format(
                    insumo=insumo)

    filtro_necessidade = ''
    if necessidade == 'a':
        # TO_DATE('20/03/2018','DD/MM/YYYY')
        filtro_necessidade = \
            "AND TRUNC(op.DATA_ENTRADA_CORTE - 7, 'iw') " \
            "    >= TRUNC(sysdate, 'iw')"

    filtro_conta_estoque = ''
    if conta_estoque:
        filtro_conta_estoque = \
            "AND ins.CONTA_ESTOQUE = {conta_estoque}".format(
                conta_estoque=conta_estoque.conta_estoque)

    sql = """
        SELECT
          ia.NIVEL_COMP NIVEL
        , ia.GRUPO_COMP REF
        , ins.DESCR_REFERENCIA DESCR
        , ic.ITEM_ESTRUTURA COR
        , ic.DESCRICAO_15 DESCR_COR
        , it.TAMANHO_REF TAM
        , it.DESCR_TAM_REFER DESCR_TAM
        FROM BASI_030 ref -- referencia
        JOIN PCPC_020 op -- OP
          ON op.REFERENCIA_PECA = ref.REFERENCIA
        JOIN PCPC_040 lote -- lote
          ON lote.ORDEM_PRODUCAO = op.ORDEM_PRODUCAO
        JOIN BASI_050 ia -- insumos de alternativa
          ON ia.NIVEL_ITEM = 1
         AND ia.NIVEL_COMP <> 1
         AND ia.GRUPO_ITEM = op.REFERENCIA_PECA
         AND ia.ALTERNATIVA_ITEM = op.ALTERNATIVA_PECA
         AND ia.ESTAGIO = lote.CODIGO_ESTAGIO
        JOIN BASI_030 ins -- insumo referencia
          ON ins.NIVEL_ESTRUTURA = ia.NIVEL_COMP
         AND ins.REFERENCIA = ia.GRUPO_COMP
        LEFT JOIN BASI_040 cot -- combinação tamanho
          ON ia.SUB_COMP = '000'
         AND cot.GRUPO_ITEM = ia.GRUPO_ITEM
         AND cot.ALTERNATIVA_ITEM = op.ALTERNATIVA_PECA
         AND cot.SEQUENCIA = ia.SEQUENCIA
         AND cot.SUB_ITEM = lote.PROCONF_SUBGRUPO
        JOIN BASI_020 it -- insumo tamanho
          ON it.BASI030_NIVEL030 = ia.NIVEL_COMP
         AND it.BASI030_REFERENC = ia.GRUPO_COMP
         AND it.TAMANHO_REF
            = CASE WHEN ia.SUB_COMP = '000'
              THEN cot.SUB_COMP
              ELSE ia.SUB_COMP
              END
        LEFT JOIN BASI_040 coc -- combinação cor
          ON ia.ITEM_COMP = '000000'
         AND coc.GRUPO_ITEM = ia.GRUPO_ITEM
         AND coc.ALTERNATIVA_ITEM = op.ALTERNATIVA_PECA
         AND coc.SEQUENCIA = ia.SEQUENCIA
         AND coc.ITEM_ITEM = lote.PROCONF_ITEM
        JOIN BASI_010 ic -- insumo cor
          ON ic.NIVEL_ESTRUTURA = ia.NIVEL_COMP
         AND ic.GRUPO_ESTRUTURA = ia.GRUPO_COMP
         AND ic.SUBGRU_ESTRUTURA = it.TAMANHO_REF
         AND ic.ITEM_ESTRUTURA
            = CASE WHEN ia.ITEM_COMP = '000000'
              THEN coc.ITEM_COMP
              ELSE ia.ITEM_COMP
              END
        WHERE op.SITUACAO IN (2, 4) -- não cancelada
          {filtro_insumo} -- filtro_insumo
          {filtro_conta_estoque} -- filtro_conta_estoque
          {filtro_necessidade} -- filtro_necessidade
        --  AND op.DATA_ENTRADA_CORTE >= TO_DATE('16/03/2018','DD/MM/YYYY')
        --  AND op.ORDEM_PRODUCAO > 5078
        GROUP BY
          ia.NIVEL_COMP
        , ia.GRUPO_COMP
        , ins.DESCR_REFERENCIA
        , ic.ITEM_ESTRUTURA
        , ic.DESCRICAO_15
        , it.TAMANHO_REF
        , it.DESCR_TAM_REFER
        ORDER BY
          ia.NIVEL_COMP
        , ia.GRUPO_COMP
        , ic.ITEM_ESTRUTURA
        , it.TAMANHO_REF
    """.format(
        filtro_insumo=filtro_insumo,
        filtro_conta_estoque=filtro_conta_estoque,
        filtro_necessidade=filtro_necessidade)
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def insumo_descr(cursor, nivel, ref, cor, tam):
    sql = """
        SELECT
          i.NIVEL_ESTRUTURA NIVEL
        , i.REFERENCIA REF
        , i.DESCR_REFERENCIA DESCR
        , ic.ITEM_ESTRUTURA COR
        , ic.DESCRICAO_15 DESCR_COR
        , it.TAMANHO_REF TAM
        , it.DESCR_TAM_REFER DESCR_TAM
        , coalesce(parm.ESTOQUE_MINIMO, 0) STQ_MIN
        , coalesce(parm.TEMPO_REPOSICAO, 0) REPOSICAO
        , coalesce(parm.LOTE_MULTIPLO, 0) LOTE_MULTIPLO
        , i.UNIDADE_MEDIDA UNID
        , COALESCE(e.QTDE_ESTOQUE_ATU, 0) QUANT
        , e.DATA_ULT_ENTRADA ULT_ENTRADA
        , e.DATA_ULT_SAIDA ULT_SAIDA
        , e.DT_INVENTARIO
        FROM BASI_010 ic -- insumo cor
        JOIN BASI_020 it -- insumo tamanho
          ON it.BASI030_NIVEL030 = ic.NIVEL_ESTRUTURA
         AND it.BASI030_REFERENC = ic.GRUPO_ESTRUTURA
         AND it.TAMANHO_REF = ic.SUBGRU_ESTRUTURA
        JOIN BASI_030 i -- insumo
          ON i.NIVEL_ESTRUTURA = ic.NIVEL_ESTRUTURA
         AND i.REFERENCIA = ic.GRUPO_ESTRUTURA
        LEFT JOIN BASI_015 parm -- parâmetros de item
          ON parm.NIVEL_ESTRUTURA = ic.NIVEL_ESTRUTURA
         AND parm.GRUPO_ESTRUTURA = ic.GRUPO_ESTRUTURA
         AND parm.SUBGRU_ESTRUTURA = ic.SUBGRU_ESTRUTURA
         AND parm.ITEM_ESTRUTURA = ic.ITEM_ESTRUTURA
        LEFT JOIN ESTQ_040 e -- estoque por depósito
          ON e.CDITEM_NIVEL99 = ic.NIVEL_ESTRUTURA
         AND e.CDITEM_GRUPO = ic.GRUPO_ESTRUTURA
         AND e.CDITEM_SUBGRUPO = ic.SUBGRU_ESTRUTURA
         AND e.CDITEM_ITEM = ic.ITEM_ESTRUTURA
         -- vvv não tenho certeza disso, mas evita aparecer mais de um registro
         AND e.LOTE_ACOMP = 0
         AND e.DEPOSITO =
             CASE WHEN i.NIVEL_ESTRUTURA = 2 THEN 202
             ELSE -- i.NIVEL_ESTRUTURA = 9
               CASE WHEN i.CONTA_ESTOQUE = 22 THEN 212
               ELSE 231
               END
             END
        WHERE ic.NIVEL_ESTRUTURA = {nivel}
          AND ic.GRUPO_ESTRUTURA = '{ref}'
          AND ic.ITEM_ESTRUTURA = '{cor}'
          AND ic.SUBGRU_ESTRUTURA = '{tam}'
    """.format(
        nivel=nivel,
        ref=ref,
        cor=cor,
        tam=tam)
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def insumo_necessidade_semana(
        cursor, nivel, ref, cor, tam, dtini=None, nsem=None, new_calc=True):

    try:
        filtra_DATA_ENTRADA_CORTE = \
            "AND coalesce(op.DATA_ENTRADA_CORTE, SYSDATE) <= " \
            "(TO_DATE('{dtini}','YYYYMMDD')+6+7*{nsem}+7)".format(
                dtini=dtini, nsem=int(nsem)-1)
    except Exception:
        filtra_DATA_ENTRADA_CORTE = ''

    sql = """
        WITH NECES AS (
          SELECT
            ness.SEMANA_NECESSIDADE
          , ness.ORDEM_PRODUCAO
          , ness.QTD_INSUMO
          , max( oss.NUMERO_ORDEM ) NUMERO_ORDEM
          , sum( nfs.QTDE_ESTRUTURA ) QTD_OS
          FROM (
            SELECT
              TRUNC(coalesce(op.DATA_ENTRADA_CORTE, SYSDATE) - 7, 'iw')
                SEMANA_NECESSIDADE
            , op.ORDEM_PRODUCAO
            , sum(
                ia.CONSUMO
    """
    if new_calc:
        sql += """--
                  * QTDE_A_PRODUZIR_PACOTE
        """
    else:
        sql += """--
                  * ( lote.QTDE_PECAS_PROG -- QTDE_A_PRODUZIR_PACOTE
                    - lote.QTDE_PECAS_PROD
                    - lote.QTDE_PECAS_2A
                    - lote.QTDE_PERDAS
                    - lote.QTDE_CONSERTO
                    - CASE WHEN lote.QTDE_EM_PRODUCAO_PACOTE <>
                                lote.QTDE_PECAS_PROG
                            AND e.CODIGO_DEPOSITO = 0
                      THEN
                        lote.QTDE_EM_PRODUCAO_PACOTE
                      ELSE
                        0
                      END
                    )
        """
    sql += """--
              ) QTD_INSUMO
            FROM BASI_030 ref -- referencia
            JOIN PCPC_020 op -- OP
              ON op.REFERENCIA_PECA = ref.REFERENCIA
            JOIN PCPC_040 lote -- lote
              ON lote.ORDEM_PRODUCAO = op.ORDEM_PRODUCAO
            JOIN BASI_050 ia -- insumos de alternativa
              ON ia.NIVEL_ITEM = 1
             AND ia.NIVEL_COMP <> 1
             AND ia.GRUPO_ITEM = op.REFERENCIA_PECA
             AND (ia.SUB_ITEM = lote.PROCONF_SUBGRUPO OR ia.SUB_ITEM = '000')
             AND (ia.ITEM_ITEM = lote.PROCONF_ITEM OR ia.ITEM_ITEM = '000000')
             AND ia.ALTERNATIVA_ITEM = op.ALTERNATIVA_PECA
             AND ia.ESTAGIO = lote.CODIGO_ESTAGIO
            LEFT JOIN MQOP_005 e
              ON e.CODIGO_ESTAGIO = ia.ESTAGIO
            LEFT JOIN BASI_040 cot -- combinação tamanho
              ON ia.SUB_COMP = '000'
             AND cot.GRUPO_ITEM = ia.GRUPO_ITEM
             AND cot.SUB_ITEM = lote.PROCONF_SUBGRUPO
             AND cot.ITEM_ITEM = ia.ITEM_ITEM
             AND cot.ALTERNATIVA_ITEM = ia.ALTERNATIVA_ITEM
             AND cot.SEQUENCIA = ia.SEQUENCIA
            LEFT JOIN BASI_040 coc -- combinação cor
              ON ia.ITEM_COMP = '000000'
             AND coc.GRUPO_ITEM = ia.GRUPO_ITEM
             AND coc.SUB_ITEM = ia.SUB_ITEM
             AND coc.ITEM_ITEM = lote.PROCONF_ITEM
             AND coc.ALTERNATIVA_ITEM = ia.ALTERNATIVA_ITEM
             AND coc.SEQUENCIA = ia.SEQUENCIA
            WHERE op.SITUACAO IN (2, 4) -- não cancelada
              AND lote.NUMERO_ORDEM = 0
              AND (  ia.NIVEL_COMP = 2
                  OR lote.QTDE_EM_PRODUCAO_PACOTE <> lote.QTDE_PECAS_PROG
                  OR ( lote.QTDE_EM_PRODUCAO_PACOTE = lote.QTDE_PECAS_PROG
                     AND e.CODIGO_DEPOSITO <> 0
                     )
                  )
              AND ia.NIVEL_COMP = {nivel}
              AND ia.GRUPO_COMP = '{ref}'
              AND CASE WHEN ia.ITEM_COMP = '000000'
                  THEN coc.ITEM_COMP
                  ELSE ia.ITEM_COMP
                  END = '{cor}'
              AND CASE WHEN ia.SUB_COMP = '000'
                  THEN cot.SUB_COMP
                  ELSE ia.SUB_COMP
                  END = '{tam}'
              {filtra_DATA_ENTRADA_CORTE} -- filtra_DATA_ENTRADA_CORTE
            GROUP BY
              TRUNC(coalesce(op.DATA_ENTRADA_CORTE, SYSDATE) - 7, 'iw')
            , op.ORDEM_PRODUCAO
            HAVING
              sum(
                ia.CONSUMO
    """
    if new_calc:
        sql += """--
                  * lote.QTDE_A_PRODUZIR_PACOTE
        """
    else:
        sql += """--
                  * ( lote.QTDE_PECAS_PROG -- QTDE_A_PRODUZIR_PACOTE
                    - lote.QTDE_PECAS_PROD
                    - lote.QTDE_PECAS_2A
                    - lote.QTDE_PERDAS
                    - lote.QTDE_CONSERTO
                    - CASE WHEN lote.QTDE_EM_PRODUCAO_PACOTE <>
                                lote.QTDE_PECAS_PROG
                            AND e.CODIGO_DEPOSITO = 0
                      THEN
                        lote.QTDE_EM_PRODUCAO_PACOTE
                      ELSE
                        0
                      END
                    )
        """
    sql += """--
              ) > 0
            ORDER BY
              1, 2
          ) ness
          LEFT JOIN (
            SELECT UNIQUE
              os.NUMERO_ORDEM
            , l.ORDEM_PRODUCAO
            FROM OBRF_080 os
            JOIN pcpc_040 l
              ON l.NUMERO_ORDEM = os.NUMERO_ORDEM
            WHERE l.NUMERO_ORDEM <> 0
          ) oss
            ON oss.ORDEM_PRODUCAO = ness.ORDEM_PRODUCAO
          LEFT JOIN OBRF_082 nfs
            ON nfs.NUMERO_ORDEM = oss.NUMERO_ORDEM
            AND nfs.PRODSAI_NIVEL99 = {nivel}
            AND nfs.PRODSAI_GRUPO = '{ref}'
            AND nfs.PRODSAI_ITEM = '{cor}'
            AND nfs.PRODSAI_SUBGRUPO = '{tam}'
          GROUP BY
            ness.SEMANA_NECESSIDADE
          , ness.ORDEM_PRODUCAO
          , ness.QTD_INSUMO
        --  , oss.NUMERO_ORDEM
        --  ORDER BY
        --    1, 2, 3, 4
        )
        SELECT
          n.SEMANA_NECESSIDADE
        , sum(n.QTD_INSUMO) - coalesce(sum(n.QTD_OS), 0) QTD_INSUMO
        FROM NECES n
        GROUP BY
          n.SEMANA_NECESSIDADE
        HAVING
          sum(n.QTD_INSUMO) - coalesce(sum(n.QTD_OS), 0) > 0
        ORDER BY
          n.SEMANA_NECESSIDADE
    """
    sql = sql.format(
        nivel=nivel,
        ref=ref,
        cor=cor,
        tam=tam,
        filtra_DATA_ENTRADA_CORTE=filtra_DATA_ENTRADA_CORTE
    )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def insumo_recebimento_semana(
        cursor, nivel, ref, cor, tam, dtini=None, nsem=None):

    try:
        filtra_DATA_PREV_ENTR = \
            "AND x.DATA_PREV_ENTR < " \
            "(TO_DATE('{dtini}','YYYYMMDD')+6+7*{nsem})".format(
                dtini=dtini, nsem=int(nsem)-1)
    except Exception:
        filtra_DATA_PREV_ENTR = ''

    sql = """
        SELECT
          TRUNC(x.DATA_PREV_ENTR, 'iw') SEMANA_ENTREGA
        , sum(
            GREATEST(
              CASE WHEN pc.COD_CANCELAMENTO = 0
                THEN x.QTDE_SALDO_ITEM
                ELSE 0 END
            , 0)
          ) QTD_A_RECEBER
        FROM SUPR_100 x -- item de pedido de compra
        JOIN SUPR_090 pc -- pedido de compra
          ON pc.PEDIDO_COMPRA = x.NUM_PED_COMPRA
        JOIN basi_030 r -- referencia
          ON r.NIVEL_ESTRUTURA = x.ITEM_100_NIVEL99
         AND r.REFERENCIA = x.ITEM_100_GRUPO
        WHERE 1=1
          AND x.ITEM_100_NIVEL99 = {nivel}
          AND x.ITEM_100_GRUPO = '{ref}'
          AND x.ITEM_100_SUBGRUPO = '{tam}'
          AND x.ITEM_100_ITEM = '{cor}'
          {filtra_DATA_PREV_ENTR} -- filtra_DATA_PREV_ENTR
        GROUP BY
          x.ITEM_100_NIVEL99
        , x.ITEM_100_GRUPO
        , x.ITEM_100_SUBGRUPO
        , x.ITEM_100_ITEM
        , TRUNC(x.DATA_PREV_ENTR, 'iw')
        HAVING
          ROUND(
            sum(
              GREATEST(
                CASE WHEN pc.COD_CANCELAMENTO = 0
                  THEN x.QTDE_SALDO_ITEM
                  ELSE 0 END
              , 0)
            ) / sum(x.QTDE_PEDIDA_ITEM) * 100
          , 1) >= 5
        ORDER BY
          1
    """.format(
        nivel=nivel,
        ref=ref,
        cor=cor,
        tam=tam,
        filtra_DATA_PREV_ENTR=filtra_DATA_PREV_ENTR
    )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def insumo_necessidade_detalhe(
        cursor, nivel, ref, cor, tam, semana, new_calc=True):
    sql = """
        SELECT
          TRUNC(coalesce(op.DATA_ENTRADA_CORTE, SYSDATE) - 7, 'iw') SEMANA
        , op.REFERENCIA_PECA REF
        , ref.DESCR_REFERENCIA DESCR
        , op.ORDEM_PRODUCAO OP
        , sum(
    """
    if new_calc:
        sql += """--
                lote.QTDE_A_PRODUZIR_PACOTE
        """
    else:
        sql += """--
                ( lote.QTDE_PECAS_PROG -- QTDE_A_PRODUZIR_PACOTE
                - lote.QTDE_PECAS_PROD
                - lote.QTDE_PECAS_2A
                - lote.QTDE_PERDAS
                - lote.QTDE_CONSERTO
                - CASE WHEN lote.QTDE_EM_PRODUCAO_PACOTE <>
                            lote.QTDE_PECAS_PROG
                        AND e.CODIGO_DEPOSITO = 0
                  THEN
                    lote.QTDE_EM_PRODUCAO_PACOTE
                  ELSE
                    0
                  END
                )
        """
    sql += """--
          ) QTD_PRODUTO
        , sum(
            ia.CONSUMO
    """
    if new_calc:
        sql += """--
              * lote.QTDE_A_PRODUZIR_PACOTE
        """
    else:
        sql += """--
              * ( lote.QTDE_PECAS_PROG -- QTDE_A_PRODUZIR_PACOTE
                - lote.QTDE_PECAS_PROD
                - lote.QTDE_PECAS_2A
                - lote.QTDE_PERDAS
                - lote.QTDE_CONSERTO
                - CASE WHEN lote.QTDE_EM_PRODUCAO_PACOTE <>
                            lote.QTDE_PECAS_PROG
                        AND e.CODIGO_DEPOSITO = 0
                  THEN
                    lote.QTDE_EM_PRODUCAO_PACOTE
                  ELSE
                    0
                  END
                )
        """
    sql += """--
          ) QTD_INSUMO
        FROM BASI_030 ref -- referencia
        JOIN PCPC_020 op -- OP
          ON op.REFERENCIA_PECA = ref.REFERENCIA
        JOIN PCPC_040 lote -- lote
          ON lote.ORDEM_PRODUCAO = op.ORDEM_PRODUCAO
        JOIN BASI_050 ia -- insumos de alternativa
          ON ia.NIVEL_ITEM = 1
         AND ia.NIVEL_COMP <> 1
         AND ia.GRUPO_ITEM = op.REFERENCIA_PECA
         AND (ia.SUB_ITEM = lote.PROCONF_SUBGRUPO OR ia.SUB_ITEM = '000')
         AND (ia.ITEM_ITEM = lote.PROCONF_ITEM OR ia.ITEM_ITEM = '000000')
         AND ia.ALTERNATIVA_ITEM = op.ALTERNATIVA_PECA
         AND ia.ESTAGIO = lote.CODIGO_ESTAGIO
        LEFT JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = ia.ESTAGIO
        LEFT JOIN BASI_040 cot -- combinação tamanho
          ON ia.SUB_COMP = '000'
         AND cot.GRUPO_ITEM = ia.GRUPO_ITEM
         AND cot.SUB_ITEM = lote.PROCONF_SUBGRUPO
         AND cot.ITEM_ITEM = ia.ITEM_ITEM
         AND cot.ALTERNATIVA_ITEM = ia.ALTERNATIVA_ITEM
         AND cot.SEQUENCIA = ia.SEQUENCIA
        LEFT JOIN BASI_040 coc -- combinação cor
          ON ia.ITEM_COMP = '000000'
         AND coc.GRUPO_ITEM = ia.GRUPO_ITEM
         AND coc.SUB_ITEM = ia.SUB_ITEM
         AND coc.ITEM_ITEM = lote.PROCONF_ITEM
         AND coc.ALTERNATIVA_ITEM = ia.ALTERNATIVA_ITEM
         AND coc.SEQUENCIA = ia.SEQUENCIA
        WHERE op.SITUACAO IN (2, 4) -- não cancelada
          AND lote.NUMERO_ORDEM = 0
          AND (  ia.NIVEL_COMP = 2
              OR lote.QTDE_EM_PRODUCAO_PACOTE <> lote.QTDE_PECAS_PROG
              OR ( lote.QTDE_EM_PRODUCAO_PACOTE = lote.QTDE_PECAS_PROG
                 AND e.CODIGO_DEPOSITO <> 0
                 )
              )
          AND ia.NIVEL_COMP = {nivel}
          AND ia.GRUPO_COMP = '{ref}'
          AND CASE WHEN ia.ITEM_COMP = '000000'
              THEN coc.ITEM_COMP
              ELSE ia.ITEM_COMP
              END = '{cor}'
          AND CASE WHEN ia.SUB_COMP = '000'
              THEN cot.SUB_COMP
              ELSE ia.SUB_COMP
              END = '{tam}'
          AND TRUNC(coalesce(op.DATA_ENTRADA_CORTE, SYSDATE) - 7, 'iw')
              = '{semana}'
        GROUP BY
          TRUNC(coalesce(op.DATA_ENTRADA_CORTE, SYSDATE) - 7, 'iw')
        , op.REFERENCIA_PECA
        , ref.DESCR_REFERENCIA
        , op.ORDEM_PRODUCAO
        HAVING
          sum(
            ia.CONSUMO
    """
    if new_calc:
        sql += """--
              * lote.QTDE_A_PRODUZIR_PACOTE
        """
    else:
        sql += """--
              * ( lote.QTDE_PECAS_PROG -- QTDE_A_PRODUZIR_PACOTE
                - lote.QTDE_PECAS_PROD
                - lote.QTDE_PECAS_2A
                - lote.QTDE_PERDAS
                - lote.QTDE_CONSERTO
                - CASE WHEN lote.QTDE_EM_PRODUCAO_PACOTE <>
                            lote.QTDE_PECAS_PROG
                        AND e.CODIGO_DEPOSITO = 0
                  THEN
                    lote.QTDE_EM_PRODUCAO_PACOTE
                  ELSE
                    0
                  END
                )
        """
    sql += """--
          ) > 0
        ORDER BY
          TRUNC(coalesce(op.DATA_ENTRADA_CORTE, SYSDATE) - 7, 'iw')
        , op.REFERENCIA_PECA
        , op.ORDEM_PRODUCAO
    """
    sql = sql.format(
        nivel=nivel,
        ref=ref,
        cor=cor,
        tam=tam,
        semana=semana)
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def previsao(cursor, periodo=None, dtini=None, nsem=None):
    filtro_date = ''
    filtro_periodo = ''
    if periodo:
        filtro_date = ''
        filtro_periodo = \
            "AND prev.DESCRICAO LIKE '{} %'".format(periodo)
    else:
        filtro_date = 'AND p.DATA_INI_PERIODO > (CURRENT_DATE + 30)'
        filtro_periodo = """
            AND TRANSLATE( SUBSTR(prev.DESCRICAO, 1, 5)
                         , '0123456789'
                         , '9999999999'
                         ) = '9999 '
            """
    try:
        filtra_DATA_INI_PERIODO = \
            "AND p.DATA_INI_PERIODO < " \
            "(TO_DATE('{dtini}','YYYYMMDD')+6+7+7*{nsem})".format(
                dtini=dtini, nsem=int(nsem)-1)
    except Exception:
        filtra_DATA_INI_PERIODO = ''

    # lista primeiro nível de necessidade da previsao
    sql = """
        WITH previsao AS (
        SELECT
          prev.NR_SOLICITACAO NR
        , prev.DESCRICAO PREV_DESCR
        , CASE WHEN prev.ALTERNATIVA = 0
          THEN ic.NUMERO_ALTERNATI
          ELSE prev.ALTERNATIVA
          END ALT
        , p.PERIODO_PRODUCAO
        , p.DATA_INI_PERIODO INI_PERIODO
        , p.DATA_INI_PERIODO - 6 DT_NECESSIDADE
        , prev.NIVEL_ESTRUTURA NIVEL
        , prev.GRUPO_ESTRUTURA REF
        , ir.DESCR_REFERENCIA REF_DESCR
        , ic.ITEM_ESTRUTURA COR
        , ic.DESCRICAO_15 COR_DESCR
        , it.TAMANHO_REF TAM
        , it.DESCR_TAM_REFER TAM_DESCR
        , tam.ORDEM_TAMANHO ORD_TAM
        , SUM(prev.QTDE_NEC_BRUTAS) QTDE_NEC_BRUTAS
        , MAX(
          CASE WHEN prev.ITEM_ESTRUTURA = '000000'
          THEN
            ( SELECT
                MIN(icc.ITEM_ESTRUTURA)
              FROM BASI_010 icc -- item cor contador
              WHERE icc.NIVEL_ESTRUTURA = ic.NIVEL_ESTRUTURA
                AND icc.GRUPO_ESTRUTURA = ic.GRUPO_ESTRUTURA
                AND icc.SUBGRU_ESTRUTURA = ic.SUBGRU_ESTRUTURA
            )
          ELSE prev.ITEM_ESTRUTURA
          END
          ) MIN_COR
        , MAX(
          CASE WHEN prev.ITEM_ESTRUTURA = '000000'
          THEN
            ( SELECT
                count(*)
              FROM BASI_010 icc -- item cor contador
              WHERE icc.NIVEL_ESTRUTURA = ic.NIVEL_ESTRUTURA
                AND icc.GRUPO_ESTRUTURA = ic.GRUPO_ESTRUTURA
                AND icc.SUBGRU_ESTRUTURA = ic.SUBGRU_ESTRUTURA
            )
          ELSE 1
          END
          ) COUNT_COR
        , MAX(
          CASE WHEN prev.SUBGRU_ESTRUTURA = '000'
          THEN
            ( SELECT
                MIN(tamc.ORDEM_TAMANHO)
              FROM BASI_020 itc -- item tamanho contador
              LEFT JOIN BASI_220 tamc
                ON tamc.TAMANHO_REF = itc.TAMANHO_REF
              WHERE itc.BASI030_NIVEL030 = it.BASI030_NIVEL030
                AND itc.BASI030_REFERENC = it.BASI030_REFERENC
            )
          ELSE 0
          END
          ) MIN_ORD_TAM
        , MAX(
          CASE WHEN prev.SUBGRU_ESTRUTURA = '000'
          THEN
            ( SELECT
                count(*)
              FROM BASI_020 itc -- item tamanho contador
              WHERE itc.BASI030_NIVEL030 = it.BASI030_NIVEL030
                AND itc.BASI030_REFERENC = it.BASI030_REFERENC
            )
          ELSE 1
          END
          ) COUNT_TAM
        FROM RCNB_020 prev
        LEFT JOIN BASI_030 ir -- combinação referencia
           ON ir.NIVEL_ESTRUTURA = prev.NIVEL_ESTRUTURA
          AND ir.REFERENCIA = prev.GRUPO_ESTRUTURA
        LEFT JOIN BASI_020 it -- combinação tam
          ON ( prev.SUBGRU_ESTRUTURA = '000'
             OR it.TAMANHO_REF = prev.SUBGRU_ESTRUTURA
             )
         AND it.BASI030_NIVEL030 = prev.NIVEL_ESTRUTURA
         AND it.BASI030_REFERENC = prev.GRUPO_ESTRUTURA
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = it.TAMANHO_REF
        LEFT JOIN BASI_010 ic -- combinação cor
          ON ( prev.ITEM_ESTRUTURA = '000000'
             OR ic.ITEM_ESTRUTURA = prev.ITEM_ESTRUTURA
             )
         AND ic.NIVEL_ESTRUTURA = prev.NIVEL_ESTRUTURA
         AND ic.GRUPO_ESTRUTURA = prev.GRUPO_ESTRUTURA
         AND ic.SUBGRU_ESTRUTURA = it.TAMANHO_REF
        JOIN PCPC_010 p
          ON p.PERIODO_PRODUCAO = SUBSTR(prev.DESCRICAO, 1, 4)
         AND p.AREA_PERIODO = 1
          {filtro_date} -- filtro_date
        WHERE 1=1
          {filtro_periodo} -- filtro_periodo
          {filtra_DATA_INI_PERIODO} -- filtra_DATA_INI_PERIODO
        GROUP BY
          prev.NR_SOLICITACAO
        , prev.DESCRICAO
        , p.PERIODO_PRODUCAO
        , p.DATA_INI_PERIODO
        , p.DATA_INI_PERIODO - 6
        , prev.NIVEL_ESTRUTURA
        , prev.GRUPO_ESTRUTURA
        , ir.DESCR_REFERENCIA
        , ic.ITEM_ESTRUTURA
        , ic.DESCRICAO_15
        , tam.ORDEM_TAMANHO
        , it.TAMANHO_REF
        , it.DESCR_TAM_REFER
        , CASE WHEN prev.ALTERNATIVA = 0
          THEN ic.NUMERO_ALTERNATI
          ELSE prev.ALTERNATIVA
          END
        ORDER BY
          prev.NIVEL_ESTRUTURA
        , prev.GRUPO_ESTRUTURA
        , ic.ITEM_ESTRUTURA
        , tam.ORDEM_TAMANHO
        , 3
        )
        SELECT
          pp.NR
        , pp.PREV_DESCR
        , pp.PERIODO_PRODUCAO
        , pp.INI_PERIODO
        , pp.DT_NECESSIDADE
        , pp.NIVEL
        , pp.REF
        , pp.REF_DESCR
        , pp.COR
        , pp.COR_DESCR
        , pp.MIN_COR
        , pp.TAM
        , pp.TAM_DESCR
        , pp.ORD_TAM
        , pp.MIN_ORD_TAM
        , pp.ALT
        , CASE WHEN pp.COR = pp.MIN_COR AND pp.ORD_TAM = pp.MIN_ORD_TAM
          THEN
            pp.QTDE_NEC_BRUTAS -
            (
              TRUNC(
                pp.QTDE_NEC_BRUTAS
                / pp.COUNT_COR
                / pp.COUNT_TAM
              )
            * ((pp.COUNT_COR * pp.COUNT_TAM) - 1)
            )
          ELSE
            TRUNC(
              pp.QTDE_NEC_BRUTAS
              / pp.COUNT_COR
              / pp.COUNT_TAM
            )
          END QTD
        FROM previsao pp
    """.format(
        filtro_date=filtro_date,
        filtro_periodo=filtro_periodo,
        filtra_DATA_INI_PERIODO=filtra_DATA_INI_PERIODO,
        )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def insumos_de_produtos_em_dual(
        cursor, dual_nivel1, extra_field=None, order='ct'):
    # insumos de produtos selecionados em dual_nivel1
    stm_extra_field = ''
    if extra_field is not None:
        stm_extra_field = ', pre.{extra_field} {extra_field}'.format(
            extra_field=extra_field)

    if order == 'ct':
        ordem_choice = '''
            , CASE WHEN ia.ITEM_COMP = '000000'
              THEN coc.ITEM_COMP
              ELSE ia.ITEM_COMP
              END
            , tam.ORDEM_TAMANHO
        '''
    elif order == 'tc':
        ordem_choice = '''
            , tam.ORDEM_TAMANHO
            , CASE WHEN ia.ITEM_COMP = '000000'
              THEN coc.ITEM_COMP
              ELSE ia.ITEM_COMP
              END
        '''

    sql = """
        WITH previsao AS ({dual_nivel1})
        SELECT
          ia.NIVEL_COMP NIVEL
        , ia.GRUPO_COMP REF
        , ir.DESCR_REFERENCIA REF_DESCR
        , CASE WHEN ia.ITEM_COMP = '000000'
          THEN coc.ITEM_COMP
          ELSE ia.ITEM_COMP
          END COR
        , ic.DESCRICAO_15 COR_DESCR
        , CASE WHEN ia.SUB_COMP = '000'
          THEN cot.SUB_COMP
          ELSE ia.SUB_COMP
          END TAM
        , it.DESCR_TAM_REFER TAM_DESCR
        , tam.ORDEM_TAMANHO ORD_TAM
        , ia.ALTERNATIVA_COMP ALT
        , ia.CONSUMO * pre.QTD QTD
        {stm_extra_field} -- stm_extra_field
        FROM previsao pre
        JOIN BASI_050 ia -- insumos de alternativa
          ON ia.NIVEL_ITEM = pre.NIVEL
         AND ia.GRUPO_ITEM = pre.REF
         AND (ia.SUB_ITEM = pre.TAM OR ia.SUB_ITEM = '000')
         AND (ia.ITEM_ITEM = pre.COR OR ia.ITEM_ITEM = '000000')
         AND ia.ALTERNATIVA_ITEM = pre.ALT
        LEFT JOIN BASI_040 coc -- combinação cor
          ON ia.ITEM_COMP = '000000'
         AND coc.GRUPO_ITEM = pre.REF
         AND coc.ALTERNATIVA_ITEM = pre.ALT
         AND coc.SEQUENCIA = ia.SEQUENCIA
         AND coc.SUB_ITEM = ia.SUB_ITEM
         AND coc.ITEM_ITEM = pre.COR
        LEFT JOIN BASI_040 cot -- combinação tamanho
          ON ia.SUB_COMP = '000'
         AND cot.GRUPO_ITEM = pre.REF
         AND cot.ALTERNATIVA_ITEM = pre.ALT
         AND cot.SEQUENCIA = ia.SEQUENCIA
         AND cot.SUB_ITEM = pre.TAM
         AND cot.ITEM_ITEM = ia.ITEM_ITEM
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF =
            CASE WHEN ia.SUB_COMP = '000'
            THEN cot.SUB_COMP
            ELSE ia.SUB_COMP
            END
        LEFT JOIN BASI_030 ir -- item referencia
          ON ir.NIVEL_ESTRUTURA = ia.NIVEL_COMP
         AND ir.REFERENCIA = ia.GRUPO_COMP
        LEFT JOIN BASI_020 it -- item tamanho
          ON it.BASI030_NIVEL030 = ia.NIVEL_COMP
         AND it.BASI030_REFERENC = ia.GRUPO_COMP
         AND it.TAMANHO_REF =
          CASE WHEN ia.SUB_COMP = '000'
          THEN cot.SUB_COMP
          ELSE ia.SUB_COMP
          END
        LEFT JOIN BASI_010 ic -- item cor
          ON ic.NIVEL_ESTRUTURA = ia.NIVEL_COMP
         AND ic.GRUPO_ESTRUTURA = ia.GRUPO_COMP
         AND ic.SUBGRU_ESTRUTURA =
          CASE WHEN ia.SUB_COMP = '000'
          THEN cot.SUB_COMP
          ELSE ia.SUB_COMP
          END
         AND ic.ITEM_ESTRUTURA =
          CASE WHEN ia.ITEM_COMP = '000000'
          THEN coc.ITEM_COMP
          ELSE ia.ITEM_COMP
          END
        ORDER BY
          ia.NIVEL_COMP
        , ia.GRUPO_COMP
        , ia.ALTERNATIVA_COMP
        {ordem_choice} -- ordem_choice
    """.format(
        dual_nivel1=dual_nivel1,
        stm_extra_field=stm_extra_field,
        ordem_choice=ordem_choice,
        )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def rolo_ref(cursor, barcode):
    # pega informações do item rolo
    sql = """
        SELECT
          x.CODIGO_ROLO ROLO
        , x.PANOACAB_NIVEL99 NIVEL
        , x.PANOACAB_GRUPO REF
        , x.PANOACAB_SUBGRUPO TAM
        , x.PANOACAB_ITEM COR
        FROM PCPT_020 x -- cadastro de rolos
        WHERE x.CODIGO_ROLO = %s
    """
    cursor.execute(sql, (barcode,))
    return rows_to_dict_list(cursor)


def insumo_previsoes_semana_insumo(
        cursor, nivel, ref, cor, tam, dtini=None, nsem=None):
    data = previsao(cursor, dtini=dtini, nsem=nsem)
    insumo = []
    while True:
        dual_nivel1 = ''
        union = ''
        # TO_DATE('20/03/2018','DD/MM/YYYY')
        for row in data:
            if row['NIVEL'] == '1':
                dual_select = '''
                    SELECT
                      {nivel} NIVEL
                    , '{ref}' REF
                    , '{cor}' COR
                    , '{tam}' TAM
                    , {qtd} QTD
                    , {alt} ALT
                    , TO_DATE('{dt}','YYYY-MM-DD') DT_NECESSIDADE
                    FROM SYS.DUAL
                '''.format(
                    nivel=row['NIVEL'],
                    ref=row['REF'],
                    cor=row['COR'],
                    tam=row['TAM'],
                    qtd=row['QTD'],
                    alt=row['ALT'],
                    dt=row['DT_NECESSIDADE'].date(),
                )
                dual_nivel1 += union + dual_select
                union = ' UNION '
            elif row['NIVEL'] == nivel \
                    and row['REF'] == ref \
                    and row['COR'] == cor \
                    and row['TAM'] == tam:
                busca_insumo = [
                    item for item in insumo
                    if item['DT_NECESSIDADE'] == row['DT_NECESSIDADE']
                    and item['NIVEL'] == row['NIVEL']
                    and item['REF'] == row['REF']
                    and item['COR'] == row['COR']
                    and item['TAM'] == row['TAM']
                    and item['ALT'] == row['ALT']
                    ]
                if busca_insumo == []:
                    insumo.append(row)
                else:
                    busca_insumo[0]['QTD'] += row['QTD']
        if dual_nivel1 == '':
            break
        else:
            data = insumos_de_produtos_em_dual(
                cursor, dual_nivel1, 'DT_NECESSIDADE')

    insumo = sorted(
        insumo, key=itemgetter(
            'DT_NECESSIDADE', 'NIVEL', 'REF', 'ALT', 'COR', 'ORD_TAM'))

    return insumo


def insumos_cor_tamanho_usados(
        cursor, qtd_itens='0', nivel=None, uso=None, insumo=None):

    if uso == 'T':
        return insumos_cor_tamanho(
                cursor, qtd_itens=qtd_itens, nivel=nivel, insumo=insumo)

    filtra_qtd_itens = ''
    if qtd_itens != '0':
        filtra_qtd_itens = 'WHERE rownum <= {qtd_itens}'.format(
            qtd_itens=qtd_itens)

    filtra_nivel = ''
    if nivel in ['2', '9']:
        filtra_nivel = "AND r.NIVEL_ESTRUTURA = '{nivel}'".format(nivel=nivel)

    filtra_uso = ''
    if uso == 'U':
        filtra_uso = "AND ia.NIVEL_COMP IS NOT NULL"
    elif uso == 'N':
        filtra_uso = "AND ia.NIVEL_COMP IS NULL"

    filtra_insumo = ''
    if insumo:
        sep = ' AND '
        ref = ''
        nivel = ''

        so_ref = re.compile("^[A-Z0-9]{5}$")
        nivelref = re.compile("^\d[A-Z0-9]{5}$")
        nivel_ref = re.compile("^\d[\. -][A-Z0-9]{5}$")
        if so_ref.match(insumo):
            ref = insumo
        elif nivelref.match(insumo) or nivel_ref.match(insumo):
            ref = insumo[-5:]
            nivel = insumo[0]
        else:
            for parte in insumo.split():
                if parte:
                    filtra_insumo += sep + """
                        ( r.REFERENCIA LIKE '%{parte}%'
                        OR r.DESCR_REFERENCIA LIKE '%{parte}%')
                    """.format(parte=parte)
        if nivel:
            filtra_insumo += sep + """
                r.NIVEL_ESTRUTURA = '{nivel}'
            """.format(nivel=nivel)
        if ref:
            filtra_insumo += sep + """
                r.REFERENCIA = '{ref}'
            """.format(ref=ref)

    sql = """
        WITH insumos AS
        (
            SELECT DISTINCT
              r.NIVEL_ESTRUTURA NIVEL
            , r.REFERENCIA REF
            , r.DESCR_REFERENCIA DESCR
            , t.TAMANHO_REF TAM
            , t.DESCR_TAM_REFER DESCR_TAM
            , tam.ORDEM_TAMANHO ORDEM_TAM
            , c.ITEM_ESTRUTURA COR
            , c.DESCRICAO_15 DESCR_COR
            FROM BASI_030 r -- referencia
            JOIN BASI_020 t -- tamanho
              ON t.BASI030_NIVEL030 = r.NIVEL_ESTRUTURA
             AND t.BASI030_REFERENC = r.REFERENCIA
            LEFT JOIN BASI_220 tam -- cadastro de tamanhos
              ON tam.TAMANHO_REF = t.TAMANHO_REF
            JOIN BASI_010 c -- cor
              ON c.NIVEL_ESTRUTURA = r.NIVEL_ESTRUTURA
             AND c.GRUPO_ESTRUTURA = r.REFERENCIA
             AND c.SUBGRU_ESTRUTURA = t.TAMANHO_REF
            LEFT JOIN BASI_050 ia -- insumos de alternativa
              ON ia.NIVEL_COMP = r.NIVEL_ESTRUTURA
             AND ia.GRUPO_COMP = r.REFERENCIA
             AND (ia.SUB_COMP = t.TAMANHO_REF OR ia.SUB_COMP = '000')
             AND (ia.ITEM_COMP = c.ITEM_ESTRUTURA OR ia.ITEM_COMP = '000000')
            WHERE r.NIVEL_ESTRUTURA IN (2, 9)
              AND r.DESCR_REFERENCIA NOT LIKE '-%'
              AND t.DESCR_TAM_REFER  NOT LIKE '-%'
              AND c.DESCRICAO_15  NOT LIKE '-%'
              AND c.ITEM_ATIVO = 0 -- ativo
              {filtra_nivel} -- filtra_nivel
              {filtra_uso} -- filtra_uso
              {filtra_insumo} -- filtra_insumo
            ORDER BY
              r.NIVEL_ESTRUTURA
            , r.REFERENCIA
            , c.ITEM_ESTRUTURA
            , tam.ORDEM_TAMANHO
            , t.TAMANHO_REF
        )
        SELECT
          i.*
        FROM insumos i
        {filtra_qtd_itens} -- filtra_qtd_itens
    """.format(
        filtra_qtd_itens=filtra_qtd_itens,
        filtra_nivel=filtra_nivel,
        filtra_uso=filtra_uso,
        filtra_insumo=filtra_insumo)
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def insumos_cor_tamanho(
        cursor, qtd_itens='0', nivel=None, insumo=None):
    filtra_qtd_itens = ''
    if qtd_itens != '0':
        filtra_qtd_itens = 'WHERE rownum <= {qtd_itens}'.format(
            qtd_itens=qtd_itens)

    filtra_nivel = ''
    if nivel in ['2', '9']:
        filtra_nivel = "AND r.NIVEL_ESTRUTURA = '{nivel}'".format(nivel=nivel)

    filtra_insumo = ''
    if insumo:
        sep = ' AND '
        ref = ''
        nivel = ''

        so_ref = re.compile("^[A-Z0-9]{5}$")
        nivelref = re.compile("^\d[A-Z0-9]{5}$")
        nivel_ref = re.compile("^\d[\. -][A-Z0-9]{5}$")
        if so_ref.match(insumo):
            ref = insumo
        elif nivelref.match(insumo) or nivel_ref.match(insumo):
            ref = insumo[-5:]
            nivel = insumo[0]
        else:
            for parte in insumo.split():
                if parte:
                    filtra_insumo += sep + """
                        ( r.REFERENCIA LIKE '%{parte}%'
                        OR r.DESCR_REFERENCIA LIKE '%{parte}%')
                    """.format(parte=parte)
        if nivel:
            filtra_insumo += sep + """
                r.NIVEL_ESTRUTURA = '{nivel}'
            """.format(nivel=nivel)
        if ref:
            filtra_insumo += sep + """
                r.REFERENCIA = '{ref}'
            """.format(ref=ref)

    sql = """
        WITH insumos AS
        (
            SELECT DISTINCT
              r.NIVEL_ESTRUTURA NIVEL
            , r.REFERENCIA REF
            , r.DESCR_REFERENCIA DESCR
            , t.TAMANHO_REF TAM
            , t.DESCR_TAM_REFER DESCR_TAM
            , tam.ORDEM_TAMANHO ORDEM_TAM
            , c.ITEM_ESTRUTURA COR
            , c.DESCRICAO_15 DESCR_COR
            FROM BASI_030 r -- referencia
            JOIN BASI_020 t -- tamanho
              ON t.BASI030_NIVEL030 = r.NIVEL_ESTRUTURA
             AND t.BASI030_REFERENC = r.REFERENCIA
            LEFT JOIN BASI_220 tam -- cadastro de tamanhos
              ON tam.TAMANHO_REF = t.TAMANHO_REF
            JOIN BASI_010 c -- cor
              ON c.NIVEL_ESTRUTURA = r.NIVEL_ESTRUTURA
             AND c.GRUPO_ESTRUTURA = r.REFERENCIA
             AND c.SUBGRU_ESTRUTURA = t.TAMANHO_REF
            WHERE r.NIVEL_ESTRUTURA IN (2, 9)
              AND r.DESCR_REFERENCIA NOT LIKE '-%'
              AND t.DESCR_TAM_REFER  NOT LIKE '-%'
              AND c.DESCRICAO_15  NOT LIKE '-%'
              AND c.ITEM_ATIVO = 0 -- ativo
              {filtra_nivel} -- filtra_nivel
              {filtra_insumo} -- filtra_insumo
            ORDER BY
              r.NIVEL_ESTRUTURA
            , r.REFERENCIA
            , c.ITEM_ESTRUTURA
            , tam.ORDEM_TAMANHO
            , t.TAMANHO_REF
        )
        SELECT
          i.*
        FROM insumos i
        {filtra_qtd_itens} -- filtra_qtd_itens
    """.format(
        filtra_qtd_itens=filtra_qtd_itens,
        filtra_nivel=filtra_nivel,
        filtra_insumo=filtra_insumo)
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def compras_periodo_insumo(cursor, nivel, ref, cor, tam):
    sql = """
        SELECT
          r.NIVEL_ESTRUTURA NIVEL
        , r.REFERENCIA REF
        , r.DESCR_REFERENCIA DESCR
        , t.TAMANHO_REF TAM
        , t.DESCR_TAM_REFER DESCR_TAM
        , tam.ORDEM_TAMANHO ORDEM_TAM
        , c.ITEM_ESTRUTURA COR
        , c.DESCRICAO_15 DESCR_COR
        FROM BASI_030 r -- referencia
        JOIN BASI_020 t -- tamanho
          ON t.BASI030_NIVEL030 = r.NIVEL_ESTRUTURA
         AND t.BASI030_REFERENC = r.REFERENCIA
        LEFT JOIN BASI_220 tam -- cadastro de tamanhos
          ON tam.TAMANHO_REF = t.TAMANHO_REF
        JOIN BASI_010 c -- cor
          ON c.NIVEL_ESTRUTURA = r.NIVEL_ESTRUTURA
         AND c.GRUPO_ESTRUTURA = r.REFERENCIA
         AND c.SUBGRU_ESTRUTURA = t.TAMANHO_REF
        WHERE r.NIVEL_ESTRUTURA = %s
          AND r.REFERENCIA = %s
          AND c.ITEM_ESTRUTURA = %s
          AND t.TAMANHO_REF = %s
    """
    cursor.execute(sql, [nivel, ref, cor, tam])
    return rows_to_dict_list_lower(cursor)


def rolo_inform(cursor, rolo):
    sql = """
        SELECT
          ro.CODIGO_ROLO
        , ro.PANOACAB_NIVEL99
        , ro.PANOACAB_GRUPO
        , ro.PANOACAB_SUBGRUPO
        , ro.PANOACAB_ITEM
        , ro.ROLO_ESTOQUE
        , COALESCE(re.ORDEM_PRODUCAO, 0) ORDEM_PRODUCAO
        FROM PCPT_020 ro -- cadastro de rolos
        LEFT JOIN TMRP_141 re -- reserva de rolo para OP
          ON re.CODIGO_ROLO = ro.CODIGO_ROLO
        WHERE ro.CODIGO_ROLO = %s
    """
    cursor.execute(sql, [rolo])
    return rows_to_dict_list_lower(cursor)
