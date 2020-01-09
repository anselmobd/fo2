from fo2.models import rows_to_dict_list_lower


def confronta_estoque_transacoes(
        cursor,
        deposito,
        cor,
        tam=None,
        modelo=None,
        ref=None,
        ):

    filtro_tam = ''
    if tam is None or tam != '':
        filtro_tam = '''--
            AND e.cditem_subgrupo = '{}'
            '''.format(tam)

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
            {filtro_tam} -- filtro_tam
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
              FROM ESTQ_310 t
              WHERE t.CODIGO_DEPOSITO = filtro.dep
                AND t.NIVEL_ESTRUTURA = filtro.nivel
                AND t.GRUPO_ESTRUTURA = filtro.ref
                AND t.SUBGRUPO_ESTRUTURA = filtro.tam
                AND t.ITEM_ESTRUTURA = filtro.cor
                AND t.DATA_MOVIMENTO =
                    ( SELECT
                        max(td.DATA_MOVIMENTO)
                      FROM ESTQ_310 td
                      WHERE td.codigo_deposito = filtro.dep
                       AND td.NIVEL_ESTRUTURA = filtro.nivel
                       AND td.GRUPO_ESTRUTURA = filtro.ref
                       AND td.SUBGRUPO_ESTRUTURA = filtro.tam
                       AND td.ITEM_ESTRUTURA = filtro.cor
                    )
                AND t.SEQUENCIA_INSERCAO =
                    ( SELECT
                        max(td.SEQUENCIA_INSERCAO)
                      FROM ESTQ_310 td
                      WHERE td.codigo_deposito = filtro.dep
                        AND td.NIVEL_ESTRUTURA = filtro.nivel
                        AND td.GRUPO_ESTRUTURA = filtro.ref
                        AND td.SUBGRUPO_ESTRUTURA = filtro.tam
                        AND td.ITEM_ESTRUTURA = filtro.cor
                        AND td.DATA_MOVIMENTO =
                            ( SELECT
                                max(td.DATA_MOVIMENTO)
                              FROM ESTQ_310 td
                              WHERE td.codigo_deposito = filtro.dep
                               AND td.NIVEL_ESTRUTURA = filtro.nivel
                               AND td.GRUPO_ESTRUTURA = filtro.ref
                               AND td.SUBGRUPO_ESTRUTURA = filtro.tam
                               AND td.ITEM_ESTRUTURA = filtro.cor
                            )
                    )
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
              FROM ESTQ_300 t
              WHERE t.CODIGO_DEPOSITO = filtro.dep
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
              FROM estq_040
              WHERE estq_040.deposito = filtro.dep
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
        filtro_tam=filtro_tam,
    )
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
