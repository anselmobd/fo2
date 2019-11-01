from django.core.cache import cache

from fo2.models import rows_to_dict_list, rows_to_dict_list_lower, GradeQtd

from utils.functions import make_key_cache, fo2logger, arg_def

from lotes.models import *
from lotes.models.base import *


def op_inform(cursor, op, cached=False):
    # informações gerais de 1 OP
    return(busca_op(cursor, op=op, cached=cached))


def busca_op(
        cursor, op=None, ref=None, modelo=None, tam=None, cor=None,
        deposito=None, tipo=None, tipo_alt=None, situacao=None, posicao=None,
        motivo=None, cached=False, quant_fin=None):
    key_cache = make_key_cache()

    cached_result = None
    if cached:
        cached_result = cache.get(key_cache)

    if cached_result is not None:
        fo2logger.info('cached '+key_cache)
        return cached_result

    filtra_op = ""
    if op is not None and op != '':
        filtra_op = """
            AND o.ORDEM_PRODUCAO = '{}'
            AND rownum = 1
        """.format(op)

    filtra_ref = ""
    if ref is not None and ref != '':
        if '%' in ref:
            filtra_ref = """--
                AND o.REFERENCIA_PECA like '{}'
            """.format(ref)
        else:
            filtra_ref = """--
                AND o.REFERENCIA_PECA = '{}'
            """.format(ref)

    filtra_modelo = ""
    if modelo is not None and modelo != '':
        filtra_modelo = """--
            AND TRIM(LEADING '0' FROM
                   (REGEXP_REPLACE(o.REFERENCIA_PECA,
                                   '^[abAB]?([^a-zA-Z]+)[a-zA-Z]*$', '\\1'
                                   ))) = '{}'
        """.format(modelo)

    filtra_tam = ""
    filtra_qtd_tam = ""
    if tam is not None and tam != '':
        filtra_tam = """
            AND EXISTS
            ( SELECT
                l.*
              FROM PCPC_040 l
              WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
                AND l.PROCONF_SUBGRUPO = '{}'
            )
        """.format(tam)
        filtra_qtd_tam = "AND l.PROCONF_SUBGRUPO = '{}'".format(tam)

    filtra_cor = ""
    filtra_qtd_cor = ""
    if cor is not None and cor != '':
        filtra_cor = """
            AND EXISTS
            ( SELECT
                l.*
              FROM PCPC_040 l
              WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
                AND l.PROCONF_ITEM = '{}'
            )
        """.format(cor)
        filtra_qtd_cor = "AND l.PROCONF_ITEM = '{}'".format(cor)

    filtra_deposito = ""
    if deposito is not None and deposito != '':
        filtra_deposito = """
            AND o.DEPOSITO_ENTRADA = '{}'
        """.format(deposito)

    filtra_posicao = ""
    if posicao == 'p':
        filtra_posicao = """--
            AND EXISTS
            ( SELECT
                *
              FROM PCPC_040 l
              WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
                AND (l.QTDE_EM_PRODUCAO_PACOTE) > 0
            )"""
    elif posicao == 'p63':
        filtra_posicao = """--
            AND EXISTS
            ( SELECT
                *
              FROM PCPC_040 l
              WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
                AND (l.QTDE_EM_PRODUCAO_PACOTE) > 0
                AND l.CODIGO_ESTAGIO <> 63
            )"""
    elif posicao == 'f':
        filtra_posicao = """--
            AND NOT EXISTS
            ( SELECT
                *
              FROM PCPC_040 l
              WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
                AND (l.QTDE_EM_PRODUCAO_PACOTE) > 0
            )"""
    elif posicao == 'f63':
        filtra_posicao = """--
            AND NOT EXISTS
            ( SELECT
                *
              FROM PCPC_040 l
              WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
                AND (l.QTDE_EM_PRODUCAO_PACOTE) > 0
                AND l.CODIGO_ESTAGIO <> 63
            )"""

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

    filtro_tipo_alt = ''
    if tipo_alt == 'e':
        filtro_tipo_alt = '''--
            AND o.REFERENCIA_PECA < 'A0000'
            AND (   ( o.ALTERNATIVA_PECA > 10 AND o.ALTERNATIVA_PECA < 50 )
                OR  ( o.ALTERNATIVA_PECA > 60 AND o.ALTERNATIVA_PECA < 100 )
                )
        '''
    elif tipo_alt == 'p':
        filtro_tipo_alt = '''--
            AND NOT (
              o.REFERENCIA_PECA < 'A0000'
              AND (   ( o.ALTERNATIVA_PECA > 10 AND o.ALTERNATIVA_PECA < 50 )
                  OR  ( o.ALTERNATIVA_PECA > 60 AND o.ALTERNATIVA_PECA < 100 )
                  )
            )
        '''

    filtro_motivo = ''
    if motivo == 'e':
        filtro_motivo = "AND o.PEDIDO_VENDA = 0"
    elif motivo == 'p':
        filtro_motivo = """--
            AND o.PEDIDO_VENDA <> 0
            AND ped.PEDIDO_VENDA IS NOT NULL
        """
    elif motivo == 'n':
        filtro_motivo = """--
            AND o.PEDIDO_VENDA <> 0
            AND ped.PEDIDO_VENDA IS NOT NULL
            AND fok.NUM_NOTA_FISCAL IS NULL
            AND fcanc.NUM_NOTA_FISCAL IS NULL
            """
    elif motivo == 'f':
        filtro_motivo = """--
            AND o.PEDIDO_VENDA <> 0
            AND ped.PEDIDO_VENDA IS NOT NULL
            AND fok.NUM_NOTA_FISCAL IS NOT NULL
            AND NOT EXISTS (
              SELECT
                fe.DOCUMENTO
              FROM OBRF_010 fe -- nota fiscal de entrada/devolução
              WHERE fe.NOTA_DEV = fok.NUM_NOTA_FISCAL
                AND fe.SITUACAO_ENTRADA <> 2 -- não cancelada
              )"""
    elif motivo == 'c':
        filtro_motivo = """--
            AND o.PEDIDO_VENDA <> 0
            AND ped.PEDIDO_VENDA IS NOT NULL
            AND fcanc.NUM_NOTA_FISCAL IS NOT NULL
            AND fok.NUM_NOTA_FISCAL IS NULL"""
    elif motivo == 'd':
        filtro_motivo = """--
            AND o.PEDIDO_VENDA <> 0
            AND ped.PEDIDO_VENDA IS NOT NULL
            AND fok.NUM_NOTA_FISCAL IS NOT NULL
            AND EXISTS (
                    SELECT
                      fe.DOCUMENTO
                    FROM OBRF_010 fe -- nota fiscal de entrada/devolução
                    WHERE fe.NOTA_DEV = fok.NUM_NOTA_FISCAL
                      AND fe.SITUACAO_ENTRADA <> 2 -- não cancelada
                  )"""
    elif motivo == 'a':
        filtro_motivo = """--
            AND o.PEDIDO_VENDA <> 0
            AND ped.PEDIDO_VENDA IS NOT NULL
            AND fok.NUM_NOTA_FISCAL IS NULL"""
    elif motivo == 'i':
        filtro_motivo = """--
            AND o.PEDIDO_VENDA <> 0
            AND ped.PEDIDO_VENDA IS NOT NULL
            AND fok.NUM_NOTA_FISCAL IS NOT NULL"""

    filtro_quant_fin = ''
    if quant_fin == 'z':
        filtro_quant_fin = "AND sele.QTD_F = 0"
    elif quant_fin == 'n':
        filtro_quant_fin = "AND sele.QTD_F <> 0"

    sql = '''
        SELECT
          sele.*
        FROM (
        SELECT
          o.ORDEM_PRODUCAO OP
        , o.PEDIDO_VENDA PED
        , ( SELECT
              LISTAGG(t.ESTAGIO, ', ')
                WITHIN GROUP (ORDER BY t.ESTAGIO) ESTAGIO
            FROM
            ( SELECT
                op.ORDEM_PRODUCAO
              , l.CODIGO_ESTAGIO ESTAGIO
              FROM pcpc_020 op
              JOIN PCPC_040 l
                ON l.ORDEM_PRODUCAO = op.ORDEM_PRODUCAO
              JOIN MQOP_005 e
                ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
              WHERE (l.QTDE_EM_PRODUCAO_PACOTE - l.QTDE_CONSERTO) > 0
              GROUP BY
                op.ORDEM_PRODUCAO
              , l.SEQUENCIA_ESTAGIO
              , l.CODIGO_ESTAGIO
              , e.DESCRICAO
              ORDER BY
                l.SEQUENCIA_ESTAGIO
            ) t
            WHERE t.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
          ) ESTAGIO
        , case
          when o.REFERENCIA_PECA <= '99999' then 'PA'
          when o.REFERENCIA_PECA <= 'B9999' then 'PG'
          else 'MD'
          end TIPO_REF
        , CASE
          WHEN o.ORDEM_PRINCIPAL <> 0
            OR LISTAGG(ofi.ORDEM_PRODUCAO, ', ')
              WITHIN GROUP (ORDER BY ofi.ORDEM_PRODUCAO)
                IS NOT NULL
            OR ome.ORDEM_PRODUCAO IS NOT NULL
            OR ose.ORDEM_PRODUCAO IS NOT NULL
          THEN 'Relacionada'
          ELSE 'Avulsa'
          END TIPO_OP
        , CASE
          WHEN o.ORDEM_PRINCIPAL <> 0 THEN 'Filha de'
          WHEN LISTAGG(ofi.ORDEM_PRODUCAO, ', ')
            WITHIN GROUP (ORDER BY ofi.ORDEM_PRODUCAO)
              IS NOT NULL THEN 'Mãe de'
          ELSE 'Avulsa'
          END TIPO_FM_OP
        , coalesce( LISTAGG(ofi.ORDEM_PRODUCAO, ', ')
            WITHIN GROUP (ORDER BY ofi.ORDEM_PRODUCAO)
              , CAST(o.ORDEM_PRINCIPAL AS varchar2(8)) ) OP_REL
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
              {filtra_qtd_tam} -- filtra_qtd_tam
              {filtra_qtd_cor} -- filtra_qtd_cor
              AND l.SEQ_OPERACAO = (
                SELECT
                  MAX( ls.SEQ_OPERACAO )
                FROM pcpc_040 ls
                WHERE ls.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
              )
          )
          , 0 ) QTD
        , COALESCE(
          ( SELECT
              SUM( l.QTDE_A_PRODUZIR_PACOTE )
            FROM pcpc_040 l
            WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
              {filtra_qtd_tam} -- filtra_qtd_tam
              {filtra_qtd_cor} -- filtra_qtd_cor
              AND l.SEQ_OPERACAO = (
                SELECT
                  MAX( ls.SEQ_OPERACAO )
                FROM pcpc_040 ls
                WHERE ls.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
              )
          )
          , 0 ) QTD_AP
        , COALESCE(
          ( SELECT
              SUM( l.QTDE_PECAS_PROD )
            FROM pcpc_040 l
            WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
              {filtra_qtd_tam} -- filtra_qtd_tam
              {filtra_qtd_cor} -- filtra_qtd_cor
              AND l.SEQ_OPERACAO = (
                SELECT
                  MAX( ls.SEQ_OPERACAO )
                FROM pcpc_040 ls
                WHERE ls.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
              )
          )
          , 0 ) QTD_F
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
         AND ped.STATUS_PEDIDO <> 5 -- não cancelado
        LEFT JOIN FATU_050 fok
          ON fok.PEDIDO_VENDA = ped.PEDIDO_VENDA
         AND fok.SITUACAO_NFISC <> 2  -- cancelada
        LEFT JOIN (
           SELECT
             fcanc1.PEDIDO_VENDA
           , MAX(fcanc1.NUM_NOTA_FISCAL) NUM_NOTA_FISCAL
           FROM FATU_050 fcanc1
           WHERE fcanc1.SITUACAO_NFISC = 2  -- cancelada
           GROUP BY
             fcanc1.PEDIDO_VENDA
         ) fcanc
          ON fcanc.PEDIDO_VENDA = ped.PEDIDO_VENDA
        JOIN basi_030 r
          ON r.NIVEL_ESTRUTURA = 1
         AND r.REFERENCIA = o.REFERENCIA_PECA
        WHERE 1=1
          {filtra_op} -- filtra_op
          {filtro_motivo} -- filtro_motivo
          {filtra_ref} -- filtra_ref
          {filtra_modelo} -- filtra_modelo
          {filtra_tam} -- filtra_tam
          {filtra_cor} -- filtra_cor
          {filtra_deposito} -- filtra_deposito
          {filtro_tipo} -- filtro_tipo
          {filtro_tipo_alt} -- filtro_tipo_alt
          {filtra_situacao} -- filtra_situacao
          {filtra_posicao} -- filtra_posicao
        GROUP BY
          o.ORDEM_PRODUCAO
        , o.REFERENCIA_PECA
        , o.ORDEM_PRINCIPAL
        , ome.ORDEM_PRODUCAO
        , ose.ORDEM_PRODUCAO
        , o.SITUACAO
        , o.COD_CANCELAMENTO
        , c.DESCRICAO
        , o.ALTERNATIVA_PECA
        , o.ROTEIRO_PECA
        , o.REFERENCIA_PECA
        , o.DATA_PROGRAMACAO
        , o.DATA_ENTRADA_CORTE
        , o.PERIODO_PRODUCAO
        , p.DATA_INI_PERIODO
        , p.DATA_FIM_PERIODO
        , o.DEPOSITO_ENTRADA
        , o.DEPOSITO_ENTRADA
        , d.DESCRICAO
        , o.PEDIDO_VENDA
        , ped.COD_PED_CLIENTE
        , r.NUMERO_MOLDE
        , r.DESCR_REFERENCIA
        , o.OBSERVACAO
        , o.OBSERVACAO2
        ORDER BY
          o.ORDEM_PRODUCAO DESC
        ) sele
        where 1=1
        {filtro_quant_fin} -- filtro_quant_fin
    '''.format(
        filtra_op=filtra_op,
        filtro_motivo=filtro_motivo,
        filtra_ref=filtra_ref,
        filtra_modelo=filtra_modelo,
        filtra_tam=filtra_tam,
        filtra_qtd_tam=filtra_qtd_tam,
        filtra_cor=filtra_cor,
        filtra_qtd_cor=filtra_qtd_cor,
        filtra_deposito=filtra_deposito,
        filtro_tipo=filtro_tipo,
        filtro_tipo_alt=filtro_tipo_alt,
        filtra_situacao=filtra_situacao,
        filtra_posicao=filtra_posicao,
        filtro_quant_fin=filtro_quant_fin,
    )
    cursor.execute(sql)

    cached_result = rows_to_dict_list(cursor)
    cache.set(key_cache, cached_result)
    fo2logger.info('calculated '+key_cache)
    return cached_result


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


def op_sortimento(cursor, **kwargs):
    header, fields, data, total = op_sortimentos(cursor, **kwargs)
    return header, fields, data


def op_sortimentos(cursor, **kwargs):
    def argdef(arg, default):
        return arg_def(kwargs, arg, default)

    op = argdef('op', None)
    tipo = argdef('tipo', 't')
    descr_sort = argdef('descr_sort', True)
    modelo = argdef('modelo', None)
    situacao = argdef('situacao', None)
    tipo_ref = argdef('tipo_ref', None)
    tipo_alt = argdef('tipo_alt', None)
    total = argdef('total', None)

    filtra_op = ''
    if op is not None:
        filtra_op = 'AND lote.ORDEM_PRODUCAO = {}'.format(op)

    filtra_modelo = ''
    if modelo is not None:
        filtra_modelo = """--
            AND TRIM( LEADING '0' FROM
                  REGEXP_REPLACE(
                    o.REFERENCIA_PECA,
                    '^[abAB]?([^a-zA-Z]+)[a-zA-Z]*$',
                    '\\1'
                  )
                ) = '{}'
        """.format(modelo)

    filtra_situacao = ''
    if situacao is not None:
        if situacao == 'a':
            filtra_situacao = "AND (NOT (o.SITUACAO = 9))"
        elif situacao == 'c':
            filtra_situacao = "AND o.SITUACAO = 9"

    filtro_tipo_ref = ''
    if tipo_ref is not None:
        if tipo_ref == 'a':
            filtro_tipo_ref = "AND o.REFERENCIA_PECA < 'A0000'"
        elif tipo_ref == 'g':
            filtro_tipo_ref = "AND o.REFERENCIA_PECA like 'A%'"
        elif tipo_ref == 'b':
            filtro_tipo_ref = "AND o.REFERENCIA_PECA like 'B%'"
        elif tipo_ref == 'p':
            filtro_tipo_ref = "AND (o.REFERENCIA_PECA like 'A%' OR " \
                "o.REFERENCIA_PECA like 'B%')"
        elif tipo_ref == 'v':
            filtro_tipo_ref = "AND o.REFERENCIA_PECA < 'C0000'"
        elif tipo_ref == 'm':
            filtro_tipo_ref = "AND o.REFERENCIA_PECA >= 'C0000'"

    filtro_tipo_alt = ''
    if tipo_alt is not None:
        if tipo_alt == 'e':
            filtro_tipo_alt = '''--
                AND o.REFERENCIA_PECA < 'A0000'
                AND (  (o.ALTERNATIVA_PECA > 10 AND o.ALTERNATIVA_PECA < 50)
                    OR (o.ALTERNATIVA_PECA > 60 AND o.ALTERNATIVA_PECA < 100)
                    )
            '''
        elif tipo_alt == 'p':
            filtro_tipo_alt = '''--
                AND NOT (
                  o.REFERENCIA_PECA < 'A0000'
                  AND (  (o.ALTERNATIVA_PECA > 10 AND o.ALTERNATIVA_PECA < 50)
                      OR (o.ALTERNATIVA_PECA > 60 AND o.ALTERNATIVA_PECA < 100)
                      )
                )
            '''

    filtro_especifico = ''
    if tipo == 'a':  # Ainda não produzido / não finalizado
        filtro_especifico = "AND (NOT (lote.QTDE_A_PRODUZIR_PACOTE = 0))"

    grade_args = {}
    if total is not None:
        grade_args = {
            'total': total,
            'forca_total': True,
        }

    # Grade de OP
    grade = GradeQtd(cursor)

    # tamanhos
    grade.col(
        id='TAMANHO',
        name='Tamanho',
        **grade_args,
        sql='''
            SELECT DISTINCT
              lote.PROCONF_SUBGRUPO TAMANHO
            , tam.ORDEM_TAMANHO SEQUENCIA_TAMANHO
            FROM PCPC_040 lote
            JOIN PCPC_020 o
              ON o.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = lote.PROCONF_SUBGRUPO
            WHERE 1=1
              {filtro_especifico} -- filtro_especifico
              {filtra_op} -- filtra_op
              {filtra_modelo} -- filtra_modelo
              {filtra_situacao} -- filtra_situacao
              {filtro_tipo_ref} -- filtro_tipo_ref
              {filtro_tipo_alt} -- filtro_tipo_alt
            ORDER BY
              2
        '''.format(
            filtro_especifico=filtro_especifico,
            filtra_op=filtra_op,
            filtra_modelo=filtra_modelo,
            filtra_situacao=filtra_situacao,
            filtro_tipo_ref=filtro_tipo_ref,
            filtro_tipo_alt=filtro_tipo_alt,
        )
    )

    # cores
    sql = '''
        SELECT
          lote.PROCONF_ITEM SORTIMENTO
    '''
    if descr_sort:
        sql += '''
            , lote.PROCONF_ITEM || ' - ' || max( p.DESCRICAO_15 ) DESCR
        '''
    else:
        sql += '''
            , lote.PROCONF_ITEM DESCR
        '''
    sql += '''
        FROM PCPC_040 lote
        JOIN PCPC_020 o
          ON o.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
    '''
    if descr_sort:
        sql += '''
            LEFT JOIN basi_010 p
              ON p.NIVEL_ESTRUTURA = 1
             AND p.GRUPO_ESTRUTURA = lote.PROCONF_GRUPO
             AND p.ITEM_ESTRUTURA = lote.PROCONF_ITEM
        '''
    sql += '''
        WHERE 1=1
          {filtro_especifico} -- filtro_especifico
          {filtra_op} -- filtra_op
          {filtra_modelo} -- filtra_modelo
          {filtra_situacao} -- filtra_situacao
          {filtro_tipo_ref} -- filtro_tipo_ref
          {filtro_tipo_alt} -- filtro_tipo_alt
        GROUP BY
          lote.PROCONF_ITEM
        ORDER BY
          2
    '''.format(
        filtro_especifico=filtro_especifico,
        filtra_op=filtra_op,
        filtra_modelo=filtra_modelo,
        filtra_situacao=filtra_situacao,
        filtro_tipo_ref=filtro_tipo_ref,
        filtro_tipo_alt=filtro_tipo_alt,
    )
    grade.row(
        id='SORTIMENTO',
        facade='DESCR',
        name='Cor',
        name_plural='Cores',
        **grade_args,
        sql=sql
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
                WHERE 1=1
                  {filtra_op} -- filtra_op
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
            '''.format(
                filtra_op=filtra_op,
            )
        )

    elif tipo == 'a':  # Ainda não produzido / não finalizado
        grade.value(
            id='QUANTIDADE',
            sql='''
                WITH opl AS
                (
                SELECT
                  o.ORDEM_PRODUCAO
                , max(lote.SEQ_OPERACAO) SEQ_OPERACAO
                FROM pcpc_040 lote
                JOIN PCPC_020 o
                  ON o.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
                WHERE 1=1
                  {filtro_especifico} -- filtro_especifico
                  {filtra_op} -- filtra_op
                  {filtra_modelo} -- filtra_modelo
                  {filtra_situacao} -- filtra_situacao
                  {filtro_tipo_ref} -- filtro_tipo_ref
                  {filtro_tipo_alt} -- filtro_tipo_alt
                GROUP BY
                  o.ORDEM_PRODUCAO
                )
                SELECT
                  l.PROCONF_SUBGRUPO TAMANHO
                , l.PROCONF_ITEM SORTIMENTO
                , SUM( l.QTDE_A_PRODUZIR_PACOTE ) QUANTIDADE
                FROM pcpc_040 l
                JOIN opl
                  ON opl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                 AND opl.SEQ_OPERACAO = l.SEQ_OPERACAO
                LEFT JOIN BASI_220 tam
                  ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
                GROUP BY
                  tam.ORDEM_TAMANHO
                , l.PROCONF_SUBGRUPO
                , l.PROCONF_ITEM
                ORDER BY
                  tam.ORDEM_TAMANHO
                , l.PROCONF_ITEM
            '''.format(
                filtro_especifico=filtro_especifico,
                filtra_op=filtra_op,
                filtra_modelo=filtra_modelo,
                filtra_situacao=filtra_situacao,
                filtro_tipo_ref=filtro_tipo_ref,
                filtro_tipo_alt=filtro_tipo_alt,
            )
        )

    elif tipo == 'fpnf':  # finalizado, de pedido, não faturado
        sql = '''
            WITH opl AS
            (
            SELECT
              o.ORDEM_PRODUCAO
            , max(lote.SEQ_OPERACAO) SEQ_OPERACAO
            FROM pcpc_040 lote
            JOIN PCPC_020 o
              ON o.ORDEM_PRODUCAO = lote.ORDEM_PRODUCAO
            LEFT JOIN PEDI_100 ped -- pedido de venda
              ON ped.PEDIDO_VENDA = o.PEDIDO_VENDA
             AND ped.STATUS_PEDIDO <> 5 -- não cancelado
            LEFT JOIN FATU_050 fok
              ON fok.PEDIDO_VENDA = ped.PEDIDO_VENDA
             AND fok.SITUACAO_NFISC <> 2  -- cancelada
            WHERE 1=1
              {filtro_especifico} -- filtro_especifico
              {filtra_op} -- filtra_op
              {filtra_modelo} -- filtra_modelo
              {filtra_situacao} -- filtra_situacao
              {filtro_tipo_ref} -- filtro_tipo_ref
              {filtro_tipo_alt} -- filtro_tipo_alt
              AND o.PEDIDO_VENDA <> 0
              AND ped.PEDIDO_VENDA IS NOT NULL
              AND fok.NUM_NOTA_FISCAL IS NULL
            GROUP BY
              o.ORDEM_PRODUCAO
            )
            SELECT
              l.PROCONF_SUBGRUPO TAMANHO
            , l.PROCONF_ITEM SORTIMENTO
            , SUM( l.QTDE_PECAS_PROD ) QUANTIDADE
            FROM pcpc_040 l
            JOIN opl
              ON opl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
             AND opl.SEQ_OPERACAO = l.SEQ_OPERACAO
            LEFT JOIN BASI_220 tam
              ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
            WHERE l.QTDE_A_PRODUZIR_PACOTE = 0
            GROUP BY
              tam.ORDEM_TAMANHO
            , l.PROCONF_SUBGRUPO
            , l.PROCONF_ITEM
            ORDER BY
              tam.ORDEM_TAMANHO
            , l.PROCONF_ITEM
        '''.format(
            filtro_especifico=filtro_especifico,
            filtra_op=filtra_op,
            filtra_modelo=filtra_modelo,
            filtra_situacao=filtra_situacao,
            filtro_tipo_ref=filtro_tipo_ref,
            filtro_tipo_alt=filtro_tipo_alt,
        )
        grade.value(
            id='QUANTIDADE',
            sql=sql,
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
                WHERE 1=1
                  {filtra_op} -- filtra_op
                GROUP BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_SUBGRUPO
                , lote.PROCONF_ITEM
                ORDER BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_ITEM
            '''.format(
                filtra_op=filtra_op,
            )
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
                WHERE 1=1
                  {filtra_op} -- filtra_op
                GROUP BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_SUBGRUPO
                , lote.PROCONF_ITEM
                ORDER BY
                  tam.ORDEM_TAMANHO
                , lote.PROCONF_ITEM
            '''.format(
                filtra_op=filtra_op,
            )
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
                WHERE 1=1
                  {filtra_op} -- filtra_op
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
            '''.format(
                filtra_op=filtra_op,
            )
        )

    fields = grade.table_data['fields']
    data = grade.table_data['data']
    if total is None:
        result = (
            grade.table_data['header'],
            fields,
            data,
            grade.total,
        )
    else:
        style = {}
        right_style = 'text-align: right;'
        bold_style = 'font-weight: bold;'
        for i in range(2, len(fields)):
            style[i] = right_style
        style[len(fields)] = right_style + bold_style
        data[-1]['|STYLE'] = bold_style

        result = (
            grade.table_data['header'],
            fields,
            data,
            style,
            grade.total,
        )

    return result


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
