from django.core.cache import cache

from fo2.models import rows_to_dict_list

from utils.functions import make_key_cache, fo2logger


def pedido_faturavel_modelo_sortimento(
        cursor, modelo=None, periodo=None, cached=True):
    key_cache = make_key_cache()

    cached_result = cache.get(key_cache)
    if cached and cached_result is not None:
        fo2logger.info('cached '+key_cache)
        return cached_result

    filtro_modelo = ''
    if modelo is not None:
        filtro_modelo = '''--
            AND TRIM(LEADING '0' FROM
                     (REGEXP_REPLACE(i.CD_IT_PE_GRUPO,
                                     '^[abAB]?([^a-zA-Z]+)[a-zA-Z]*$', '\\1'
                                     ))) = '{}' '''.format(modelo)

    filtra_periodo = ''
    if periodo is not None:
        periodo_list = periodo.split(':')
        if periodo_list[0] != '':
            filtra_periodo += '''--
                AND ped.DATA_ENTR_VENDA > CURRENT_DATE + {}
            '''.format(periodo_list[0])
        if periodo_list[1] != '':
            filtra_periodo += '''--
                AND ped.DATA_ENTR_VENDA <= CURRENT_DATE + {}
            '''.format(periodo_list[1])

    sql = """
        SELECT
          pref.TAM
        , t.ORDEM_TAMANHO
        , pref.COR
        , sum(pref.QTD - pref.QTD_FAT) QTD
        FROM (
          SELECT
            pqs.PEDIDO
          , pqs.TAM
          , pqs.COR
          , sum(pqs.QTD) QTD
          , sum(pqs.QTD_FAT) QTD_FAT
          FROM (
            SELECT
              pq.PEDIDO
            , pq.REF
            , pq.TAM
            , pq.COR
            , pq.QTD
            , sum(COALESCE(inf.QTDE_ITEM_FATUR, 0)) QTD_FAT
            FROM (
              SELECT
                ps.PEDIDO
              , i.CD_IT_PE_GRUPO REF
              , i.CD_IT_PE_SUBGRUPO TAM
              , i.CD_IT_PE_ITEM COR
              , sum(i.QTDE_PEDIDA) QTD
              FROM (
                SELECT
                  ped.PEDIDO_VENDA PEDIDO
                -- , max(fok.NUM_NOTA_FISCAL) NFOK
                , max(fcanc.NUM_NOTA_FISCAL) NFCANC
                FROM PEDI_100 ped -- pedido de venda
                LEFT JOIN FATU_050 fok -- fatura
                  ON fok.PEDIDO_VENDA = ped.PEDIDO_VENDA
                 AND fok.SITUACAO_NFISC <> 2  -- cancelada
                LEFT JOIN FATU_050 fcanc -- fatura
                  ON fcanc.PEDIDO_VENDA = ped.PEDIDO_VENDA
                 AND fcanc.SITUACAO_NFISC = 2  -- cancelada
                WHERE ped.STATUS_PEDIDO <> 5 -- não cancelado
                  AND fok.NUM_NOTA_FISCAL IS NULL
                {filtra_periodo} -- filtra_periodo
                -- AND ped.DATA_ENTR_VENDA <= CURRENT_DATE + 148
                GROUP BY
                  ped.PEDIDO_VENDA
              ) ps -- pedidos pré-filtrados
              JOIN PEDI_110 i -- item de pedido de venda
                ON i.PEDIDO_VENDA = ps.PEDIDO
              WHERE 1=1
                {filtro_modelo} -- filtro_modelo
                -- AND TRIM(LEADING '0' FROM
                --          (REGEXP_REPLACE(i.CD_IT_PE_GRUPO,
                --                          '^[abAB]?([^a-zA-Z]+)[a-zA-Z]*$',
                --                          '\\1'
                --                          ))) = '5156'  -- filtro_modelo
              GROUP BY
                ps.PEDIDO
              , i.CD_IT_PE_NIVEL99
              , i.CD_IT_PE_GRUPO
              , i.CD_IT_PE_SUBGRUPO
              , i.CD_IT_PE_ITEM
              , ps.NFCANC
            ) pq -- itens de pedidos com qtd
            LEFT JOIN fatu_060 inf -- item de nf de saída
              ON inf.PEDIDO_VENDA = pq.PEDIDO
             AND inf.COD_CANCELAMENTO = 0
             AND inf.NIVEL_ESTRUTURA = 1
             AND inf.GRUPO_ESTRUTURA = pq.REF
             AND inf.SUBGRU_ESTRUTURA = pq.TAM
             AND inf.ITEM_ESTRUTURA = pq.COR
            GROUP BY
              pq.PEDIDO
            , pq.REF
            , pq.TAM
            , pq.COR
            , pq.QTD
          ) pqs -- itens de pedidos com qtd e qtd faturada
          GROUP BY
            pqs.PEDIDO
          , pqs.TAM
          , pqs.COR
        ) pref -- referencias de pedidos  com qtds
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = pref.TAM
        WHERE pref.QTD > pref.QTD_FAT
        GROUP BY
          pref.COR
        , t.ORDEM_TAMANHO
        , pref.TAM
        ORDER BY
          pref.COR
        , t.ORDEM_TAMANHO
        , pref.TAM
    """.format(
        filtro_modelo=filtro_modelo,
        filtra_periodo=filtra_periodo,
    )
    cursor.execute(sql)

    # A partir dos dados captados, montar a
    # grade = GradeQtd(cursor)

    cached_result = rows_to_dict_list(cursor)
    cache.set(key_cache, cached_result)
    fo2logger.info('calculated '+key_cache)
    return cached_result
