from fo2.models import rows_to_dict_list_lower


def confronta_estoque_transacoes(
        cursor,
        deposito,
        tam,
        cor,
        modelo=None,
        ref=None,
        ):
    sql = '''
        WITH filtro AS
        ( SELECT
            e.deposito dep
          , e.cditem_nivel99 nivel
          , e.cditem_grupo ref
          , e.cditem_subgrupo tam
          , e.cditem_item cor
          FROM estq_040 e
          WHERE e.deposito =  {deposito}
            AND e.cditem_nivel99 = 1
            AND e.cditem_grupo = '{ref}'
            AND e.cditem_subgrupo = '{tam}'
            AND e.cditem_item = '{cor}'
            AND e.lote_acomp = 0
        )
        SELECT
          filtro.dep
        , filtro.nivel
        , filtro.ref
        , filtro.tam
        , filtro.cor
        , COALESCE(
            (
              SELECT
                t.SALDO_FISICO
              FROM (
                SELECT
                  t.NIVEL_ESTRUTURA
                , t.CODIGO_DEPOSITO
                , t.GRUPO_ESTRUTURA
                , t.SUBGRUPO_ESTRUTURA
                , t.ITEM_ESTRUTURA
                , t.DATA_MOVIMENTO
                , max(t.SEQUENCIA_INSERCAO) SEQUENCIA_INSERCAO
                FROM (
                  SELECT
                    t.CODIGO_DEPOSITO
                  , t.NIVEL_ESTRUTURA
                  , t.GRUPO_ESTRUTURA
                  , t.SUBGRUPO_ESTRUTURA
                  , t.ITEM_ESTRUTURA
                  , max(t.DATA_MOVIMENTO) DATA_MOVIMENTO
                  FROM filtro
                  JOIN ESTQ_310 t
                    ON t.codigo_deposito = filtro.dep
                   AND t.NIVEL_ESTRUTURA = filtro.nivel
                   AND t.GRUPO_ESTRUTURA = filtro.ref
                   AND t.SUBGRUPO_ESTRUTURA = filtro.tam
                   AND t.ITEM_ESTRUTURA = filtro.cor
                  GROUP BY
                    t.CODIGO_DEPOSITO
                  , t.NIVEL_ESTRUTURA
                  , t.GRUPO_ESTRUTURA
                  , t.SUBGRUPO_ESTRUTURA
                  , t.ITEM_ESTRUTURA
                ) old1
                JOIN ESTQ_310 t
                  ON t.CODIGO_DEPOSITO = old1.CODIGO_DEPOSITO
                 AND t.NIVEL_ESTRUTURA = old1.NIVEL_ESTRUTURA
                 AND t.GRUPO_ESTRUTURA = old1.GRUPO_ESTRUTURA
                 AND t.SUBGRUPO_ESTRUTURA = old1.SUBGRUPO_ESTRUTURA
                 AND t.ITEM_ESTRUTURA = old1.ITEM_ESTRUTURA
                 AND t.DATA_MOVIMENTO = old1.DATA_MOVIMENTO
                GROUP BY
                  t.NIVEL_ESTRUTURA
                , t.CODIGO_DEPOSITO
                , t.GRUPO_ESTRUTURA
                , t.SUBGRUPO_ESTRUTURA
                , t.ITEM_ESTRUTURA
                , t.DATA_MOVIMENTO
              ) old2
              JOIN ESTQ_310 t
                ON t.CODIGO_DEPOSITO = old2.CODIGO_DEPOSITO
               AND t.NIVEL_ESTRUTURA = old2.NIVEL_ESTRUTURA
               AND t.GRUPO_ESTRUTURA = old2.GRUPO_ESTRUTURA
               AND t.SUBGRUPO_ESTRUTURA = old2.SUBGRUPO_ESTRUTURA
               AND t.ITEM_ESTRUTURA = old2.ITEM_ESTRUTURA
               AND t.DATA_MOVIMENTO = old2.DATA_MOVIMENTO
               AND t.SEQUENCIA_INSERCAO = old2.SEQUENCIA_INSERCAO
            )
          , 0
          ) QTD_OLD
        , COALESCE(
            ( SELECT
                sum(
                  CASE WHEN t.ENTRADA_SAIDA = 'S' THEN
                    -t.QUANTIDADE
                  ELSE t.QUANTIDADE
                  END
                ) QTD
              FROM filtro
              JOIN ESTQ_300 t
                ON t.CODIGO_DEPOSITO = filtro.dep
               AND t.NIVEL_ESTRUTURA = filtro.nivel
               AND t.GRUPO_ESTRUTURA = filtro.ref
               AND t.SUBGRUPO_ESTRUTURA = filtro.tam
               AND t.ITEM_ESTRUTURA = filtro.cor
            )
          , 0
          ) QTD
        , COALESCE(
            ( SELECT
                estq_040.qtde_estoque_atu
              FROM filtro
              JOIN estq_040
                ON estq_040.deposito = filtro.dep
               AND estq_040.cditem_nivel99 = filtro.nivel
               AND estq_040.cditem_grupo = filtro.ref
               AND estq_040.cditem_subgrupo = filtro.tam
               AND estq_040.cditem_item = filtro.cor
               AND estq_040.lote_acomp = 0
            )
          , 0
          ) STQ
        FROM filtro
    '''.format(
        deposito=deposito,
        ref=ref,
        cor=cor,
        tam=tam,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
