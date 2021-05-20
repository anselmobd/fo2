from django.core.cache import cache

from utils.functions.models import rows_to_dict_list

from utils.functions import fo2logger, my_make_key_cache


def op_inform(cursor, op, cached=False):
    # informações gerais de 1 OP
    return(busca_op(cursor, op=op, cached=cached))


def busca_op(
        cursor, op=None, ref=None, modelo=None, tam=None, cor=None,
        deposito=None, tipo=None, tipo_alt=None, situacao=None, posicao=None,
        motivo=None, cached=False, quant_fin=None, quant_emp=None,
        data_de=None, data_ate=None):
    """
    posicao: t - Todas as OPs
             p - Em produção
             f - Finalizadas
             p63 - Em produção, exceto OPs apenas no 63-CD
             f63 - Finalizadas, incluindo OPs apenas no 63-CD
    """
    # key_cache = make_key_cache()
    key_cache = my_make_key_cache(
        'busca_op',
        op, ref, modelo, tam, cor,
        deposito, tipo, tipo_alt, situacao, posicao,
        motivo, quant_fin, quant_emp,
    )

    cached_result = None
    if cached:
        cached_result = cache.get(key_cache)

    if cached_result is not None:
        fo2logger.info('cached '+key_cache)
        return cached_result

    filtra_op = ""
    if op is not None and op != '':
        filtra_op = """--
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
                AND (l.QTDE_DISPONIVEL_BAIXA > 0 OR l.QTDE_CONSERTO > 0)
            )"""
    elif posicao == 'p63':
        filtra_posicao = """--
            AND EXISTS
            ( SELECT
                *
              FROM PCPC_040 l
              WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
                AND (l.QTDE_DISPONIVEL_BAIXA > 0 OR l.QTDE_CONSERTO > 0)
                AND l.CODIGO_ESTAGIO <> 63
            )"""
    elif posicao == 'f':
        filtra_posicao = """--
            AND NOT EXISTS
            ( SELECT
                *
              FROM PCPC_040 l
              WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
                AND (l.QTDE_DISPONIVEL_BAIXA > 0 OR l.QTDE_CONSERTO > 0)
            )"""
    elif posicao == 'f63':
        filtra_posicao = """--
            AND NOT EXISTS
            ( SELECT
                *
              FROM PCPC_040 l
              WHERE l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
                AND (l.QTDE_DISPONIVEL_BAIXA > 0 OR l.QTDE_CONSERTO > 0)
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

    filtro_quant_emp = ''
    if quant_emp == 'z':
        filtro_quant_emp = "AND sele.QTD_AP = 0"
    elif quant_emp == 'n':
        filtro_quant_emp = "AND sele.QTD_AP <> 0"

    filtra_data_de = ""
    if data_de is not None and data_de != '':
        filtra_data_de = f"""
            AND o.DATA_ENTRADA_CORTE >= '{data_de}'
        """

    filtra_data_ate = ""
    if data_ate is not None and data_ate != '':
        filtra_data_ate = f"""
            AND o.DATA_ENTRADA_CORTE <= '{data_ate}'
        """

    sql = '''
        SELECT
          sele.OP
        , sele.PED
        , sele.ESTAGIO
        , sele.TIPO_REF
        , sele.TIPO_OP
        , sele.TIPO_FM_OP
        , sele.OP_REL
        , sele.SITUACAO
        , sele.CANCELAMENTO
        , sele.ALTERNATIVA
        , sele.ROTEIRO
        , sele."REF"
        , sele.MODELO
        , sele.LOTES
        , COALESCE(sele.QTD, 0) QTD
        , COALESCE(sele.QTD_AP, 0) QTD_AP
        , COALESCE(sele.QTD_CD, 0) QTD_CD
        , COALESCE(sele.QTD_F, 0) QTD_F
        , sele.DT_DIGITACAO
        , sele.DT_CORTE
        , sele.PERIODO
        , sele.PERIODO_INI
        , sele.PERIODO_FIM
        , sele.DEPOSITO_CODIGO
        , sele.DEPOSITO
        , sele.PEDIDO
        , sele.PRIORIDADE
        , sele.PED_CLIENTE
        , sele.DT_EMBARQUE
        , sele.STATUS_PEDIDO
        , sele.MOLDE
        , sele.DESCR_REF
        , sele.COLECAO
        , sele.OBSERVACAO
        , sele.OBSERVACAO2
        , sele.UNIDADE
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
              -- WHERE (l.QTDE_EM_PRODUCAO_PACOTE - l.QTDE_CONSERTO) > 0
              WHERE ( ( l.CODIGO_ESTAGIO <> 63
                      AND (l.QTDE_EM_PRODUCAO_PACOTE - l.QTDE_CONSERTO) > 0
                      )
                    OR
                      ( l.CODIGO_ESTAGIO = 63
                      AND (l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO) > 0
                      )
                    )
              GROUP BY
                op.ORDEM_PRODUCAO
              , l.SEQUENCIA_ESTAGIO
              , l.CODIGO_ESTAGIO
              --ORDER BY
              --  l.SEQUENCIA_ESTAGIO
            ) t
            WHERE t.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
          ) ESTAGIO
        , case
          when o.REFERENCIA_PECA <= '99999' then 'PA'
          when o.REFERENCIA_PECA <= 'A9999' then 'PG'
          when o.REFERENCIA_PECA <= 'B9999' then 'PB'
          when o.REFERENCIA_PECA LIKE 'F%' then 'MP'
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
        , seq_op.LOTES
        , seq_l.QTD
        , lotes_ap.QTD_AP
        , lotes_cd.QTD_CD
        , seq_l.QTD_F
        , o.DATA_PROGRAMACAO DT_DIGITACAO
        , o.DATA_ENTRADA_CORTE DT_CORTE
        , o.PERIODO_PRODUCAO PERIODO
        , p.DATA_INI_PERIODO PERIODO_INI
        , p.DATA_FIM_PERIODO PERIODO_FIM
        , o.DEPOSITO_ENTRADA DEPOSITO_CODIGO
        , o.DEPOSITO_ENTRADA || ' - ' || d.DESCRICAO DEPOSITO
        , o.PEDIDO_VENDA PEDIDO
        , o.PRIORIDADE_PRODU PRIORIDADE
        , COALESCE(ped.COD_PED_CLIENTE, ' ') PED_CLIENTE
        , COALESCE(ped.DATA_ENTR_VENDA, NULL) DT_EMBARQUE
        , COALESCE(ped.STATUS_PEDIDO, NULL) STATUS_PEDIDO
        , COALESCE(r.NUMERO_MOLDE, '-') MOLDE
        , r.DESCR_REFERENCIA DESCR_REF
        , r.COLECAO
        , o.OBSERVACAO
        , o.OBSERVACAO2
        , CASE WHEN div.DIVISAO_PRODUCAO IS NULL
          THEN ' '
          ELSE div.DIVISAO_PRODUCAO || '-' || div.DESCRICAO
          END UNIDADE
        FROM PCPC_020 o
        LEFT JOIN (
          SELECT
            l.ORDEM_PRODUCAO
          , MAX( l.SEQ_OPERACAO ) MAXSEQ
          , COUNT( DISTINCT l.ORDEM_CONFECCAO ) LOTES
          , MAX(
              CASE WHEN l.CODIGO_FAMILIA > 1 AND l.CODIGO_FAMILIA < 1000
              THEN l.CODIGO_FAMILIA
              ELSE 0
              END
            ) CODIGO_FAMILIA
          FROM pcpc_040 l
          GROUP BY
            l.ORDEM_PRODUCAO
          ) seq_op
          ON seq_op.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
        LEFT JOIN BASI_180 div
          ON seq_op.CODIGO_FAMILIA <> 0
         AND div.DIVISAO_PRODUCAO = seq_op.CODIGO_FAMILIA
        LEFT JOIN (
          SELECT
            l.ORDEM_PRODUCAO
          , l.SEQ_OPERACAO
          , SUM( l.QTDE_PECAS_PROD ) QTD_F
          -- , SUM( l.QTDE_A_PRODUZIR_PACOTE ) QTD_AP
          , SUM( l.QTDE_PECAS_PROG ) QTD
          FROM pcpc_040 l
          WHERE 1=1
            {filtra_qtd_tam} -- filtra_qtd_tam
            {filtra_qtd_cor} -- filtra_qtd_cor
          GROUP BY
            l.ORDEM_PRODUCAO
          , l.SEQ_OPERACAO
          ) seq_l
          ON seq_l.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
         AND seq_l.SEQ_OPERACAO = seq_op.MAXSEQ
        LEFT JOIN (
          SELECT
            l.ORDEM_PRODUCAO
          , SUM( l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO ) QTD_AP
          FROM pcpc_040 l
          WHERE 1=1
            {filtra_qtd_tam} -- filtra_qtd_tam
            {filtra_qtd_cor} -- filtra_qtd_cor
          GROUP BY
            l.ORDEM_PRODUCAO
          ) lotes_ap
          ON lotes_ap.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
        LEFT JOIN (
          SELECT
            l.ORDEM_PRODUCAO
          , SUM( l.QTDE_DISPONIVEL_BAIXA + l.QTDE_CONSERTO ) QTD_CD
          FROM pcpc_040 l
          WHERE 1=1
            AND l.CODIGO_ESTAGIO IN (57, 63)
            {filtra_qtd_tam} -- filtra_qtd_tam
            {filtra_qtd_cor} -- filtra_qtd_cor
          GROUP BY
            l.ORDEM_PRODUCAO
          ) lotes_cd
          ON lotes_cd.ORDEM_PRODUCAO = o.ORDEM_PRODUCAO
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
          {filtra_data_de} -- filtra_data_de
          {filtra_data_ate} -- filtra_data_ate
        GROUP BY
          o.ORDEM_PRODUCAO
        , o.REFERENCIA_PECA
        , o.ORDEM_PRINCIPAL
        , div.DIVISAO_PRODUCAO
        , div.DESCRICAO
        , seq_op.LOTES
        , seq_l.QTD
        , lotes_ap.QTD_AP
        , lotes_cd.QTD_CD
        , seq_l.QTD_F
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
        , o.PRIORIDADE_PRODU
        , ped.COD_PED_CLIENTE
        , ped.DATA_ENTR_VENDA
        , ped.STATUS_PEDIDO
        , r.NUMERO_MOLDE
        , r.DESCR_REFERENCIA
        , r.COLECAO
        , o.OBSERVACAO
        , o.OBSERVACAO2
        ORDER BY
          o.ORDEM_PRODUCAO DESC
        ) sele
        where 1=1
        {filtro_quant_fin} -- filtro_quant_fin
        {filtro_quant_emp} -- filtro_quant_emp
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
        filtro_quant_emp=filtro_quant_emp,
        filtra_data_de=filtra_data_de,
        filtra_data_ate=filtra_data_ate,
    )
    cursor.execute(sql)

    cached_result = rows_to_dict_list(cursor)
    cache.set(key_cache, cached_result)
    fo2logger.info('calculated '+key_cache)
    return cached_result
