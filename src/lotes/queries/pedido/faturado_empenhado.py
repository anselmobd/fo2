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
        cursor,
        empresa=1,
        modelo=None,
        ref=None,
        colecao=None,
        cor=None,
        tam=None,
        com_pac=False,
        cached=False,
    ):
    """Dados de pedidos faturados com empenhos
    """

    key_cache = my_make_key_cache(
        'lotes/queries/pedido/faturado_empenhado/query',
        empresa,
        modelo,
        ref,
        colecao,
        cor,
        tam,
        com_pac,
    )

    if cached:
        cached_result = cache.get(key_cache)
        if cached_result is not None:
            fo2logger.info('cached '+key_cache)
            cache_ttl(cache, key_cache)
            return cached_result

    filtro_colecao = ''
    if colecao is not None:
        filtro_colecao = f'''--
            AND r.COLECAO = {colecao}'''

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

    sql = f"""
        WITH
          peds AS 
        ( SELECT
            ped.PEDIDO_VENDA PEDIDO
          FROM PEDI_100 ped -- pedido de venda
          WHERE 1=1
            AND ped.CODIGO_EMPRESA = 1
            AND ped.STATUS_PEDIDO <> 5 -- não cancelado
            AND ped.SITUACAO_VENDA = 10 -- faturado
        )
        , itens AS 
        ( SELECT
            peds.PEDIDO
          , i.CD_IT_PE_NIVEL99 NIVEL
          , i.CD_IT_PE_GRUPO REF
          , i.CD_IT_PE_SUBGRUPO TAM
          , i.CD_IT_PE_ITEM COR
          , sum(i.QTDE_PEDIDA) QTD
          FROM peds
          JOIN PEDI_110 i -- item de pedido de venda
            ON i.PEDIDO_VENDA = peds.PEDIDO
          JOIN basi_030 r
            ON r.REFERENCIA = i.CD_IT_PE_GRUPO
           AND r.NIVEL_ESTRUTURA = i.CD_IT_PE_NIVEL99 
          WHERE 1=1
            {filtro_colecao} -- filtro_colecao
            {filtro_ref} -- filtro_ref
            {filtro_tam} -- filtro_tam
            {filtro_cor} -- filtro_cor
          GROUP BY
            peds.PEDIDO
          , r.COLECAO
          , i.CD_IT_PE_NIVEL99
          , i.CD_IT_PE_GRUPO
          , i.CD_IT_PE_SUBGRUPO
          , i.CD_IT_PE_ITEM
        )
        , itens_emp AS
        ( SELECT
            i.PEDIDO
          , i.NIVEL
          , i.REF
          , i.TAM
          , i.COR
          , i.QTD
          , COALESCE(
              ( SELECT
                  SUM(sl.QTDE)
                FROM pcpc_044 sl -- solicitação / lote 
                WHERE sl.PEDIDO_DESTINO = i.PEDIDO
                  AND sl.ORDEM_CONFECCAO <> 0
                  AND sl.GRUPO_DESTINO = i.REF
                  AND sl.SUB_DESTINO = i.TAM
                  AND sl.COR_DESTINO = i.COR
                  AND sl.SITUACAO = 5
              )
            , 0 
            ) QTD_SOL
          , COALESCE(
              ( SELECT
                  SUM(sl.QTDE)
                FROM pcpc_044 sl -- solicitação / lote 
                WHERE sl.PEDIDO_DESTINO = i.PEDIDO
                  AND sl.ORDEM_CONFECCAO <> 0 
                  AND sl.GRUPO_DESTINO = i.REF
                  AND sl.SUB_DESTINO = i.TAM
                  AND sl.COR_DESTINO = i.COR
                  AND sl.SITUACAO IN (1, 2, 3, 4)
              )
            , 0 
            ) QTD_EMP
          FROM itens i
          WHERE 1=1
            AND EXISTS (
              SELECT
                sl.QTDE
              FROM pcpc_044 sl -- solicitação / lote 
              WHERE sl.PEDIDO_DESTINO = i.PEDIDO
                AND sl.ORDEM_CONFECCAO <> 0 
                AND sl.GRUPO_DESTINO = i.REF
                AND sl.SUB_DESTINO = i.TAM
                AND sl.COR_DESTINO = i.COR
                AND sl.SITUACAO IN (1, 2, 3, 4)
            )
        )
        , ref_emp AS 
        ( SELECT
            i.PEDIDO
          , i.NIVEL
          , i.REF
          , sum(i.QTD) QTD
          , sum(i.QTD_SOL) QTD_SOL
          , sum(i.QTD_EMP) QTD_EMP
          FROM itens_emp i
          GROUP BY 
            i.PEDIDO
          , i.NIVEL
          , i.REF
        )
        , ped_sit AS
        ( SELECT 
            i.PEDIDO
          , i.NIVEL
          , i.REF
          , i.QTD
          , i.QTD_EMP
          , i.QTD_SOL
          , COALESCE(
              ( SELECT
                  MIN(sl.SITUACAO)
                FROM pcpc_044 sl -- solicitação / lote 
                WHERE sl.PEDIDO_DESTINO = i.PEDIDO
                  AND sl.ORDEM_CONFECCAO <> 0 
                  AND sl.GRUPO_DESTINO = i.REF
                  AND sl.SITUACAO <> 0
              )
            , 0 
            ) EMP_SIT_MIN
          , COALESCE(
              ( SELECT
                  MAX(sl.SITUACAO)
                FROM pcpc_044 sl -- solicitação / lote 
                WHERE sl.PEDIDO_DESTINO = i.PEDIDO
                  AND sl.ORDEM_CONFECCAO <> 0 
                  AND sl.GRUPO_DESTINO = i.REF
                  AND sl.SITUACAO <> 0
              )
            , 0 
            ) EMP_SIT_MAX
          FROM ref_emp i
        )
        SELECT
          i.PEDIDO
        , i.EMP_SIT_MIN
        , i.EMP_SIT_MAX
        , i.NIVEL
        , i.REF
        , i.QTD
        , i.QTD QTD_FAT
        , i.QTD_EMP
        , i.QTD_SOL
        , ped.DATA_ENTR_VENDA DATA
        , c.FANTASIA_CLIENTE CLIENTE
        FROM ped_sit i
        JOIN PEDI_100 ped -- pedido de venda
          ON ped.PEDIDO_VENDA = i.PEDIDO
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = ped.CLI_PED_CGC_CLI9
         AND c.CGC_4 = ped.CLI_PED_CGC_CLI4
         AND c.CGC_2 = ped.CLI_PED_CGC_CLI2
        ORDER BY
          i.EMP_SIT_MIN
        , i.EMP_SIT_MAX
        , i.PEDIDO
        , i.NIVEL
        , i.REF
    """

    debug_cursor_execute(cursor, sql)
    data = dictlist(cursor)

    cached_result = data
    cache.set(key_cache, cached_result)
    fo2logger.info('calculated '+key_cache)
    return cached_result
