from pprint import pprint

from django.db import models
from django.db import connections

from fo2.models import rows_to_dict_list

import produto.models


class ContaEstoque(models.Model):
    conta_estoque = models.IntegerField(
        primary_key=True,
        verbose_name='Código')
    descr_ct_estoque = models.CharField(
        max_length=100,
        verbose_name='Descrição')

    def __str__(self):
        return '{}-{}'.format(self.conta_estoque, self.descr_ct_estoque)

    class Meta:
        managed = False
        app_label = 'systextil'
        db_table = "BASI_150"
        verbose_name = "Conta de estoque"


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

    quais_insumos = ''
    if quais == 'a':
        quais_insumos = """
            ( l.QTDE_PECAS_PROG - l.QTDE_PECAS_PROD - l.QTDE_PECAS_2A
            - l.QTDE_PERDAS - l.QTDE_CONSERTO )
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
         AND ia.ALTERNATIVA_ITEM = o.ALTERNATIVA_PECA
         AND ia.ESTAGIO = l.CODIGO_ESTAGIO
        LEFT JOIN BASI_040 coc -- combinação cor
          ON ia.ITEM_COMP = '000000'
         AND coc.GRUPO_ITEM = ia.GRUPO_ITEM
         AND coc.ALTERNATIVA_ITEM = o.ALTERNATIVA_PECA
         AND coc.SEQUENCIA = ia.SEQUENCIA
         AND coc.ITEM_ITEM = l.PROCONF_ITEM
        LEFT JOIN BASI_040 cot -- combinação tamanho
          ON ia.SUB_COMP = '000'
         AND cot.GRUPO_ITEM = ia.GRUPO_ITEM
         AND cot.ALTERNATIVA_ITEM = o.ALTERNATIVA_PECA
         AND cot.SEQUENCIA = ia.SEQUENCIA
         AND cot.SUB_ITEM = l.PROCONF_SUBGRUPO
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
        quais_insumos=quais_insumos)
    cursor.execute(sql)
    # , [data_corte, data_corte, conta_estoque, conta_estoque])
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
                CASE WHEN '{recebimento}' = 'a' AND
                  (
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
              , 0)
            ) QTD_A_RECEBER
        , ROUND(
            sum(
              GREATEST(
             '{recebimento}' = 'a' AND    CASE WHEN '{recebimento}' = 'a' AND
                  (
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
        recebimento=recebimento,
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
