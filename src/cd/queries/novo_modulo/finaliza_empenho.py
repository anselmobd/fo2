from pprint import pprint
from typing import Iterable

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def exec(
    cursor,
    op=None,
    oc=None,
    ped=None,
    ref=None,
):
    filtra_op = f"""--
        AND sl.ORDEM_PRODUCAO = {op}
    """ if op else ''

    filtra_oc = f"""--
        AND sl.ORDEM_CONFECCAO = {oc}
    """ if oc else ''

    filtra_pedido_destino = f"""--
        AND sl.PEDIDO_DESTINO = {ped}
    """ if ped else ''

    filtra_ref_destino = f"""--
        AND
          CASE WHEN sl.GRUPO_DESTINO = '00000'
          THEN l.PROCONF_GRUPO
          ELSE sl.GRUPO_DESTINO
          END = '{ref}'
    """ if ref else ''

    sql = f"""
        SELECT
          sl.*
        FROM pcpc_044 sl -- solicitação / lote 
        -- Na tabela de solicitações aparece a OP de expedição também como
        -- reservada, com situação 4. Para tentar evitar isso, não listo
        -- lotes que pertençam a OP que não tem estágio 63
        -- (OPs de expedição não tem 63)
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND l.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
         AND l.CODIGO_ESTAGIO = 63
        WHERE 1=1
          {filtra_op} -- filtra_op
          {filtra_oc} -- filtra_oc
          {filtra_pedido_destino} -- filtra_pedido_destino
          {filtra_ref_destino} -- filtra_ref_destino
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)
    return dados
