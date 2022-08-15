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
        'lotes/queries/pedido/varejo_empenhado/query',
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
        field="sl.GRUPO_DESTINO",
        ref=ref,
        modelo=modelo,
        com_ped=True,
        com_pac=com_pac,
    )

    filtro_tam = ''
    if tam is not None and tam != '':
        filtro_tam = f"AND sl.SUB_DESTINO = '{tam}'"

    filtro_cor = ''
    if cor is not None and cor != '':
        filtro_cor = f"AND sl.COR_DESTINO = '{cor}'"

    sql = f"""
        WITH agrup
          AS
        ( SELECT
            sl.PEDIDO_DESTINO AGRUPADOR 
          , sl.GRUPO_DESTINO REF
          , LISTAGG(DISTINCT COALESCE(iped.PEDIDO_VENDA, 0), ', ')
            WITHIN GROUP (ORDER BY iped.PEDIDO_VENDA) PEDIDOS
          FROM pcpc_044 sl -- solicitação / lote 
          JOIN basi_030 r
            ON r.NIVEL_ESTRUTURA = 1
           AND r.REFERENCIA = sl.GRUPO_DESTINO
          JOIN PEDI_110 iped -- item de pedido de venda
            ON iped.AGRUPADOR_PRODUCAO = sl.PEDIDO_DESTINO - 999000000
          WHERE 1=1
            AND sl.PEDIDO_DESTINO >= 999000000
            AND sl.SITUACAO IN (1, 2, 3, 4)
            {filtro_colecao} -- filtro_colecao
            {filtro_ref} -- filtro_ref
            {filtro_tam} -- filtro_tam
            {filtro_cor} -- filtro_cor
          GROUP BY 
            sl.PEDIDO_DESTINO 
          , sl.GRUPO_DESTINO  
        )
        SELECT
          a.AGRUPADOR
        , a.REF
        , a.PEDIDOS
        , MIN(sl.SITUACAO) EMP_SIT_MIN
        , MAX(sl.SITUACAO) EMP_SIT_MAX
        , SUM(sl.QTDE) QTD_EMP
        FROM agrup a
        JOIN pcpc_044 sl -- solicitação / lote
          ON sl.PEDIDO_DESTINO = a.AGRUPADOR
         AND sl.GRUPO_DESTINO = a.REF
        GROUP BY 
          a.AGRUPADOR
        , a.REF
        , a.PEDIDOS
        ORDER BY 
          4 
        , 5 
        , a.AGRUPADOR 
        , a.REF  
    """

    debug_cursor_execute(cursor, sql)
    data = dictlist(cursor)

    cached_result = data
    cache.set(key_cache, cached_result)
    fo2logger.info('calculated '+key_cache)
    return cached_result
