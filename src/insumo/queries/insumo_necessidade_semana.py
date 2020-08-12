from pprint import pprint

from utils.functions.models import rows_to_dict_list


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
