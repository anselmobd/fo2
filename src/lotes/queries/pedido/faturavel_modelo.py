import datetime
from pprint import pprint

from django.core.cache import cache

from utils.functions import (
    cache_ttl,
    fo2logger,
    my_make_key_cache,
)
from utils.functions.models.dictlist import dictlist
from utils.functions.queries import debug_cursor_execute

from cd.queries.novo_modulo.gerais import *


def query(
        cursor, modelo=None, ref=None, cor=None, tam=None, periodo=None,
        cached=True, deposito=None, empresa=1, nat_oper=None, group="dpnr",
        colecao=None, desconto_duplicata=False, com_pac=False):
    """Devolve dados de pedidos faturáveis

    Recebe:
        group: "dpnr" = data, pedido, nivel, referência  
               "p" = pedido
    """

    # key_cache = make_key_cache()
    key_cache = my_make_key_cache(
        'lotes/queries/pedido/faturavel_modelo/query',
        modelo, ref, cor, tam, periodo,
        deposito, empresa, nat_oper, group,
        colecao, desconto_duplicata, com_pac,
    )

    cached_result = cache.get(key_cache)
    if cached and cached_result is not None:
        fo2logger.info('cached '+key_cache)
        cache_ttl(cache, key_cache)
        return cached_result

    # filtro_modelo = ''
    # if modelo is not None and modelo != '':
    #     filtro_modelo = f'''--
    #         AND TRIM(LEADING '0' FROM
    #                  (REGEXP_REPLACE(i.CD_IT_PE_GRUPO,
    #                                  '^[abAB]?([^a-zA-Z]+)[a-zA-Z]*$', '\\1'
    #                                  ))) = '{modelo}' '''

    filtro_colecao = ''
    if colecao is not None:
        filtro_colecao = f'''--
            AND r.COLECAO = {colecao}'''

    # filtro_ref = ''
    # if ref is not None and ref != '':
    #     filtro_ref = f"AND i.CD_IT_PE_GRUPO = '{ref}'"

    filtro_ref = get_filtra_ref(
        cursor,
        field="i.CD_IT_PE_GRUPO",
        ref=ref,
        modelo=modelo,
        com_ped=True,
        com_pac=com_pac,
    )

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

    if desconto_duplicata:
        calculo_preco = "sum(i.QTDE_PEDIDA*i.VALOR_UNITARIO*(100-ps.PERC_DESC_DUPLIC)/100) PRECO"
    else:
        calculo_preco = "sum(i.QTDE_PEDIDA*i.VALOR_UNITARIO) PRECO"


    sql = f"""
        SELECT
          pref.PEDIDO
        , COALESCE(
            ( SELECT
                MIN(sl.SITUACAO)
              FROM pcpc_044 sl -- solicitação / lote 
              JOIN PCPC_040 l
                ON l.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO 
               AND l.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
               AND l.SEQUENCIA_ESTAGIO = 1
              WHERE sl.PEDIDO_DESTINO = pref.PEDIDO
                AND sl.ORDEM_CONFECCAO <> 0 
                -- AND sl.GRUPO_DESTINO <> '0'
                -- AND sl.GRUPO_DESTINO = pref.REF
                   AND (
                     CASE WHEN sl.GRUPO_DESTINO = '00000'
                     THEN l.PROCONF_GRUPO
                     ELSE sl.GRUPO_DESTINO
                     END = pref.REF
                   )
                AND sl.SITUACAO <> 0
            )
          , 0 
          ) EMP_SIT_MIN
        , COALESCE(
            ( SELECT
                MAX(sl.SITUACAO)
              FROM pcpc_044 sl -- solicitação / lote 
              JOIN PCPC_040 l
                ON l.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO 
               AND l.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
               AND l.SEQUENCIA_ESTAGIO = 1
              WHERE sl.PEDIDO_DESTINO = pref.PEDIDO
                AND sl.ORDEM_CONFECCAO <> 0 
                -- AND sl.GRUPO_DESTINO <> '0'
                -- AND sl.GRUPO_DESTINO = pref.REF
                   AND (
                     CASE WHEN sl.GRUPO_DESTINO = '00000'
                     THEN l.PROCONF_GRUPO
                     ELSE sl.GRUPO_DESTINO
                     END = pref.REF
                   )
                AND sl.SITUACAO <> 0
            )
          , 0 
          ) EMP_SIT_MAX
        , COALESCE(
            ( SELECT 
                MIN(iped.AGRUPADOR_PRODUCAO)
              FROM PEDI_110 iped -- item de pedido de venda
              WHERE iped.PEDIDO_VENDA = pref.PEDIDO
            )
          , 0 
          ) AGRUPADOR
        , pref.QTD_SOL
        , pref.QTD_EMP
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
          , SUM(COALESCE(
              ( SELECT
                  SUM(sl.QTDE)
                FROM pcpc_044 sl -- solicitação / lote 
                JOIN PCPC_040 l
                  ON l.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO 
                 AND l.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
                 AND l.SEQUENCIA_ESTAGIO = 1
                WHERE sl.PEDIDO_DESTINO = pqs.PEDIDO
                  AND sl.ORDEM_CONFECCAO <> 0 
                  -- AND sl.GRUPO_DESTINO = pqs.REF
                  AND (
                     CASE WHEN sl.GRUPO_DESTINO = '00000'
                     THEN l.PROCONF_GRUPO
                     ELSE sl.GRUPO_DESTINO
                     END = pqs.REF
                  )
                  -- AND sl.SUB_DESTINO = pqs.TAM
                  AND (
                     CASE WHEN sl.GRUPO_DESTINO = '00000'
                     THEN l.PROCONF_SUBGRUPO
                     ELSE sl.SUB_DESTINO
                     END = pqs.TAM
                  )
                  -- AND sl.COR_DESTINO = pqs.COR
                  AND (
                     CASE WHEN sl.GRUPO_DESTINO = '00000'
                     THEN l.PROCONF_ITEM
                     ELSE sl.COR_DESTINO
                     END = pqs.COR
                  )
                  AND sl.SITUACAO = 5
              )
            , 0 
            )) QTD_SOL
          , SUM(COALESCE(
              ( SELECT
                  SUM(sl.QTDE)
                FROM pcpc_044 sl -- solicitação / lote 
                JOIN PCPC_040 l
                  ON l.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO 
                 AND l.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
                 AND l.SEQUENCIA_ESTAGIO = 1
                WHERE sl.PEDIDO_DESTINO = pqs.PEDIDO
                  AND sl.ORDEM_CONFECCAO <> 0 
                  -- AND sl.GRUPO_DESTINO = pqs.REF
                  AND (
                     CASE WHEN sl.GRUPO_DESTINO = '00000'
                     THEN l.PROCONF_GRUPO
                     ELSE sl.GRUPO_DESTINO
                     END = pqs.REF
                  )
                  -- AND sl.SUB_DESTINO = pqs.TAM
                  AND (
                     CASE WHEN sl.GRUPO_DESTINO = '00000'
                     THEN l.PROCONF_SUBGRUPO
                     ELSE sl.SUB_DESTINO
                     END = pqs.TAM
                  )
                  -- AND sl.COR_DESTINO = pqs.COR
                  AND (
                     CASE WHEN sl.GRUPO_DESTINO = '00000'
                     THEN l.PROCONF_ITEM
                     ELSE sl.COR_DESTINO
                     END = pqs.COR
                  )
                  AND sl.SITUACAO IN (1, 2, 3, 4)
              )
            , 0 
            )) QTD_EMP
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
              , {calculo_preco} -- calculo_preco
              , CASE WHEN ps.NFCANC IS NULL
                THEN 'Não faturado'
                ELSE 'Faturamento cancelado'
                END FAT
              FROM (
                SELECT
                  ped.PEDIDO_VENDA PEDIDO
                , ped.PERC_DESC_DUPLIC
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
                , ped.PERC_DESC_DUPLIC  
              ) ps -- pedidos pré-filtrados
              JOIN PEDI_110 i -- item de pedido de venda
                ON i.PEDIDO_VENDA = ps.PEDIDO
              JOIN basi_030 r
                ON r.REFERENCIA = i.CD_IT_PE_GRUPO
               AND r.NIVEL_ESTRUTURA = i.CD_IT_PE_NIVEL99 
              WHERE 1=1
                {filtro_colecao} -- filtro_colecao
                -- filtro_modelo -- filtro_modelo
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
          2
        , 3
        , 4
        , ped.DATA_ENTR_VENDA
        , pref.PEDIDO
        , pref.NIVEL
        , pref.REF
    """

    debug_cursor_execute(cursor, sql)
    data = dictlist(cursor)

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
