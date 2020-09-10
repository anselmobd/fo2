from pprint import pprint

from django.core.cache import cache

from utils.functions.models import rows_to_dict_list_lower

from utils.functions import my_make_key_cache, fo2logger


def pedido_faturavel_modelo_sortimento(
        cursor, modelo=None, periodo=None, cached=True):
    # key_cache = make_key_cache()
    key_cache = my_make_key_cache(
        'pedido_faturavel_modelo_sortimento', modelo, periodo, cached)

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
    result = rows_to_dict_list_lower(cursor)

    headers = ['Cores / Tamanhos']
    fields = ['SORTIMENTO']
    sortimento = {'Total': {}}
    cores = []
    total = 0

    for row in result:
        tam = row['tam']
        cor = row['cor']
        qtd = row['qtd']
        if tam not in headers:
            headers.append(tam)
            fields.append(tam)
        if cor not in cores:
            cores.append(cor)

        if cor not in sortimento:
            sortimento[cor] = {}
        if tam not in sortimento[cor]:
            sortimento[cor][tam] = 0
        if 'Total' not in sortimento[cor]:
            sortimento[cor]['Total'] = 0
        if tam not in sortimento['Total']:
            sortimento['Total'][tam] = 0
        if 'Total' not in sortimento['Total']:
            sortimento['Total']['Total'] = 0

        sortimento[cor][tam] += qtd
        sortimento[cor]['Total'] += qtd
        sortimento['Total'][tam] += qtd
        sortimento['Total']['Total'] += qtd
        total += qtd

    headers.append('Total')
    fields.append('Total')

    dados = []
    for cor in cores:
        dict_cor = sortimento[cor]
        dict_cor['SORTIMENTO'] = cor
        dados.append(dict_cor)
    dict_cor = sortimento['Total']
    dict_cor['SORTIMENTO'] = 'Total'
    dados.append(dict_cor)

    style = {}
    right_style = 'text-align: right;'
    bold_style = 'font-weight: bold;'
    for i in range(2, len(fields)):
        style[i] = right_style
    style[len(fields)] = right_style + bold_style
    dados[-1]['|STYLE'] = bold_style

    cached_result = (
        headers,
        fields,
        dados,
        style,
        total,
    )

    cache.set(key_cache, cached_result)
    fo2logger.info('calculated '+key_cache)
    return cached_result
