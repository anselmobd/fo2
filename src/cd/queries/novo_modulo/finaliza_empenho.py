from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def exec(
    cursor,
    executa=False,
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

    sql = f"""--
        SELECT
          sl.ORDEM_PRODUCAO
        , sl.ORDEM_CONFECCAO
        , sl.PEDIDO_DESTINO
        , sl.OP_DESTINO
        , sl.OC_DESTINO
        , sl.DEP_DESTINO
        , sl.GRUPO_DESTINO
        , sl.ALTER_DESTINO
        , sl.SUB_DESTINO
        , sl.COR_DESTINO
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
          AND sl.SITUACAO <> 5
          {filtra_op} -- filtra_op
          {filtra_oc} -- filtra_oc
          {filtra_pedido_destino} -- filtra_pedido_destino
          {filtra_ref_destino} -- filtra_ref_destino
    """
    if executa:
        sql = f"""
            UPDATE SYSTEXTIL.PCPC_044
            SET 
              SITUACAO = 5
            WHERE (
              ORDEM_PRODUCAO
            , ORDEM_CONFECCAO
            , PEDIDO_DESTINO
            , OP_DESTINO
            , OC_DESTINO
            , DEP_DESTINO
            , GRUPO_DESTINO
            , ALTER_DESTINO
            , SUB_DESTINO
            , COR_DESTINO
            )
            IN (
              {sql} --sql
            )
        """
    result = debug_cursor_execute(cursor, sql)
    if executa:
        return result
    else:
        dados = dictlist_lower(cursor)
        return dados
