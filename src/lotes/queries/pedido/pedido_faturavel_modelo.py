import datetime
from pprint import pprint

from django.core.cache import cache

from utils.functions.models import rows_to_dict_list

from utils.functions import (
    cache_ttl,
    fo2logger,
    my_make_key_cache,
)


def pedido_faturavel_modelo(
        cursor, modelo=None, ref=None, cor=None, tam=None, periodo=None,
        cached=True, deposito=None, empresa=1, nat_oper=None, group="dpnr",
        colecao=None):
    """Devolve dados de pedidos faturáveis

    Recebe:
        group: "dpnr" = data, pedido, nivel, referência  
               "p" = pedido
    """

    # key_cache = make_key_cache()
    key_cache = my_make_key_cache(
        'pedido_faturavel_modelo',
        modelo, ref, cor, tam, periodo, deposito,
        empresa, nat_oper, group, colecao
    )

    cached_result = cache.get(key_cache)
    if cached and cached_result is not None:
        fo2logger.info('cached '+key_cache)
        cache_ttl(cache, key_cache)
        return cached_result

    filtro_modelo = ''
    if modelo is not None and modelo != '':
        filtro_modelo = f'''--
            AND TRIM(LEADING '0' FROM
                     (REGEXP_REPLACE(i.CD_IT_PE_GRUPO,
                                     '^[abAB]?([^a-zA-Z]+)[a-zA-Z]*$', '\\1'
                                     ))) = '{modelo}' '''

    filtro_colecao = ''
    if colecao is not None:
        filtro_colecao = f'''--
            AND r.COLECAO = {colecao}'''

    filtro_ref = ''
    if ref is not None and ref != '':
        filtro_ref = f"AND i.CD_IT_PE_GRUPO = '{ref}'"

    filtro_tam = ''
    if tam is not None and tam != '':
        filtro_tam = f"AND i.CD_IT_PE_SUBGRUPO = '{tam}'"

    filtro_cor = ''
    if cor is not None and cor != '':
        filtro_cor = f"AND i.CD_IT_PE_ITEM = '{cor}'"

    filtro_deposito = ''
    if deposito is not None and cor != '':
        filtro_deposito = f"AND i.CODIGO_DEPOSITO = '{deposito}'"

    filtra_periodo = ''
    if periodo is not None:
        periodo_list = periodo.split(':')
        if periodo_list[0] != '':
            filtra_periodo += f'''--
                AND ped.DATA_ENTR_VENDA > CURRENT_DATE + {periodo_list[0]}
            '''
        if periodo_list[1] != '':
            filtra_periodo += f'''--
                AND ped.DATA_ENTR_VENDA <= CURRENT_DATE + {periodo_list[1]}
            '''

    # (1, 2) = venda
    # (4, 8) = amostra / bonificação
    filtra_nat_oper = ''
    if nat_oper is not None:
        filtra_nat_oper = '''--
            AND ped.NATOP_PV_NAT_OPER IN (
        '''
        sep = ''
        for natu in nat_oper:
            filtra_nat_oper += f'{sep}{natu}'
            sep = ', '
        filtra_nat_oper += f')'

    sql = f"""
        SELECT
          pref.PEDIDO
        , pref.NIVEL
        , pref.REF
        , pref.FAT
        , pref.QTD
        , pref.PRECO
        , pref.QTD_FAT
        , ped.DATA_ENTR_VENDA DATA
        , c.FANTASIA_CLIENTE CLIENTE
        FROM (
          SELECT
            pqs.PEDIDO
          , pqs.NIVEL
          , pqs.REF
          , pqs.FAT
          , sum(pqs.QTD) QTD
          , sum(pqs.PRECO) PRECO
          , sum(pqs.QTD_FAT) QTD_FAT
          FROM (
            SELECT
              pq.PEDIDO
            , pq.NIVEL
            , pq.REF
            , pq.TAM
            , pq.COR
            , pq.QTD
            , pq.PRECO
            , pq.FAT
            , sum(COALESCE(inf.QTDE_ITEM_FATUR, 0)) QTD_FAT
            FROM (
              SELECT
                ps.PEDIDO
              , i.CD_IT_PE_NIVEL99 NIVEL
              , i.CD_IT_PE_GRUPO REF
              , i.CD_IT_PE_SUBGRUPO TAM
              , i.CD_IT_PE_ITEM COR
              , sum(i.QTDE_PEDIDA) QTD
              , sum(i.QTDE_PEDIDA*i.VALOR_UNITARIO) PRECO
              , CASE WHEN ps.NFCANC IS NULL
                THEN 'Não faturado'
                ELSE 'Faturamento cancelado'
                END FAT
              FROM (
                SELECT
                  ped.PEDIDO_VENDA PEDIDO
        --        , max(fok.NUM_NOTA_FISCAL) NFOK
                , max(fcanc.NUM_NOTA_FISCAL) NFCANC
                FROM PEDI_100 ped -- pedido de venda
                LEFT JOIN FATU_050 fok -- fatura
                  ON fok.PEDIDO_VENDA = ped.PEDIDO_VENDA
                 AND fok.SITUACAO_NFISC <> 2  -- cancelada
                 AND fok.NUMERO_CAIXA_ECF = 0
                LEFT JOIN FATU_050 fcanc -- fatura
                  ON fcanc.PEDIDO_VENDA = ped.PEDIDO_VENDA
                 AND fcanc.SITUACAO_NFISC = 2  -- cancelada
                 AND fcanc.NUMERO_CAIXA_ECF = 0
                WHERE 1=1
                  AND ped.CODIGO_EMPRESA = {empresa}
                  AND ped.STATUS_PEDIDO <> 5 -- não cancelado
                  AND ped.SITUACAO_VENDA = 0 -- pedido liberado
                  {filtra_nat_oper} -- filtra_nat_oper
                  AND fok.NUM_NOTA_FISCAL IS NULL
                  -- AND ped.DATA_ENTR_VENDA <= CURRENT_DATE + 148
                  {filtra_periodo} -- filtra_periodo
                GROUP BY
                  ped.PEDIDO_VENDA
              ) ps -- pedidos pré-filtrados
              JOIN PEDI_110 i -- item de pedido de venda
                ON i.PEDIDO_VENDA = ps.PEDIDO
              JOIN basi_030 r
                ON r.REFERENCIA = i.CD_IT_PE_GRUPO
              WHERE 1=1
                {filtro_colecao} -- filtro_colecao
                {filtro_modelo} -- filtro_modelo
                {filtro_ref} -- filtro_ref
                {filtro_tam} -- filtro_tam
                {filtro_cor} -- filtro_cor
                {filtro_deposito} -- filtro_deposito
              GROUP BY
                ps.PEDIDO
              , r.COLECAO
              , i.CD_IT_PE_NIVEL99
              , i.CD_IT_PE_GRUPO
              , i.CD_IT_PE_SUBGRUPO
              , i.CD_IT_PE_ITEM
              , ps.NFCANC
            ) pq -- itens de pedidos com qtd
            LEFT JOIN fatu_060 inf -- item de nf de saída
              ON inf.PEDIDO_VENDA = pq.PEDIDO
             AND inf.COD_CANCELAMENTO = 0
             AND inf.NIVEL_ESTRUTURA = pq.NIVEL
             AND inf.GRUPO_ESTRUTURA = pq.REF
             AND inf.SUBGRU_ESTRUTURA = pq.TAM
             AND inf.ITEM_ESTRUTURA = pq.COR
             AND inf.NR_CAIXA = 0
            GROUP BY
              pq.PEDIDO
            , pq.NIVEL
            , pq.REF
            , pq.TAM
            , pq.COR
            , pq.QTD
            , pq.PRECO
            , pq.FAT
          ) pqs -- itens de pedidos com qtd e qtd faturada
          GROUP BY
            pqs.PEDIDO
          , pqs.NIVEL
          , pqs.REF
          , pqs.FAT
        ) pref -- referencias de pedidos  com qtds
        JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = pref.PEDIDO
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND c.CGC_4 = ped.CLI_PED_CGC_CLI4
         AND c.CGC_2 = ped.CLI_PED_CGC_CLI2
        WHERE pref.QTD > pref.QTD_FAT
        ORDER BY
          ped.DATA_ENTR_VENDA
        , pref.PEDIDO
        , pref.NIVEL
        , pref.REF
    """

    cursor.execute(sql)

    data = rows_to_dict_list(cursor)

    if group == "p":
        dp_dict = {}
        for row in data:
            try:
                anterior = dp_dict[row['PEDIDO']]
                anterior['QTD'] += row['QTD']
                anterior['QTD_FAT'] += row['QTD_FAT']
                anterior['PRECO'] += row['PRECO']
            except KeyError:
                dp_dict[row['PEDIDO']] = row
        dp_list = []
        for pedido in sorted(dp_dict.keys()):
            dp_list.append(dp_dict[pedido])
        data = dp_list

    cached_result = data
    cache.set(key_cache, cached_result)
    fo2logger.info('calculated '+key_cache)
    return cached_result
