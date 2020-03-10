from utils.functions.models import rows_to_dict_list_lower


def confronta_estoque_transacoes(
        cursor,
        deposito,
        tam=None,
        cor=None,
        modelo=None,
        ref=None,
        corrige=False,
        ):

    filtro_tam = ''
    if tam is not None and tam != '':
        filtro_tam = '''--
            AND e.cditem_subgrupo = '{}'
            '''.format(tam)

    filtro_cor = ''
    if cor is not None and cor != '':
        filtro_cor = '''--
            AND e.cditem_item = '{}'
            '''.format(cor)

    filtro_ref = ''
    if ref is not None and ref != '':
        filtro_ref = '''--
            AND e.cditem_grupo = '{}'
            '''.format(ref)

    filtro_modelo = ''
    if modelo is not None and modelo != '':
        filtro_modelo = '''--
            AND
              TRIM(
                LEADING '0' FROM (
                  REGEXP_REPLACE(
                    e.cditem_grupo,
                    '^0?[abAB]?([0-9]+)[a-zA-Z]*$',
                    '\\1'
                  )
                )
              ) = '{}'
        '''.format(
            modelo,
        )

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
            AND e.cditem_grupo < 'C0000'
            {filtro_ref} -- filtro_ref
            {filtro_modelo} -- filtro_modelo
            {filtro_tam} -- filtro_tam
            {filtro_cor} -- filtro_cor
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
                AND t.SEQUENCIA_FICHA =
                    ( SELECT
                        max(td.SEQUENCIA_FICHA)
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
                AND t.SEQUENCIA_INSERCAO =
                    ( SELECT
                        max(t.SEQUENCIA_INSERCAO)
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
                        AND t.SEQUENCIA_FICHA =
                            ( SELECT
                                max(td.SEQUENCIA_FICHA)
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
        filtro_ref=filtro_ref,
        filtro_modelo=filtro_modelo,
        filtro_tam=filtro_tam,
        filtro_cor=filtro_cor,
    )
    cursor.execute(sql)
    data = rows_to_dict_list_lower(cursor)

    exec_ok = True
    count = 0
    if corrige:
        for row in data:
            if row['stq'] != (row['qtd_old'] + row['qtd']):
                sql = '''
                    UPDATE estq_040
                    SET
                      estq_040.qtde_estoque_atu = {est}
                    WHERE estq_040.deposito = {deposito}
                      AND estq_040.cditem_nivel99 = 1
                      AND estq_040.cditem_grupo = '{ref}'
                      AND estq_040.cditem_subgrupo = '{tam}'
                      AND estq_040.cditem_item = '{cor}'
                      AND estq_040.lote_acomp = 0
                '''.format(
                    deposito=row['dep'],
                    ref=row['ref'],
                    tam=row['tam'],
                    cor=row['cor'],
                    est=(row['qtd_old'] + row['qtd']),
                    )
                try:
                    cursor.execute(sql)
                    row['stq'] = row['qtd_old'] + row['qtd']
                except Exception:
                    exec_ok = False
                    break
                count += 1
                if count == 1000:
                    break

    return data, exec_ok, count
