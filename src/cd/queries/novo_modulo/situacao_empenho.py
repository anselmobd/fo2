from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def finaliza(cursor, **kwargs):
    return exec(cursor, finaliza=True, **kwargs)


def cancela(cursor, **kwargs):
    return exec(cursor, cancela=True, **kwargs)


def consulta(cursor, **kwargs):
    return exec(cursor, consulta=True, **kwargs)


def exec(
    cursor,
    finaliza=False,
    cancela=False,
    consulta=False,
    ordem_producao=None,
    ordem_confeccao=None,
    pedido_destino=None,
    op_destino=None,
    oc_destino=None,  # atualmente não utilizado
    dep_destino=None,  # atualmente não utilizado
    grupo_destino=None,
    alter_destino=None,
    sub_destino=None,
    cor_destino=None,
    solicitacao=None,
    exec=True,
):

    if sum([finaliza, cancela, consulta]) != 1:
        raise AttributeError(
            "Defina uma ação. Indique finaliza ou cancela como True nos kwargs")

    filtra_ordem_producao = "" if ordem_producao is None else f"""--
        AND sl.ORDEM_PRODUCAO = {ordem_producao}
    """

    filtra_ordem_confeccao = "" if ordem_confeccao is None else f"""--
        AND sl.ORDEM_CONFECCAO = {ordem_confeccao}
    """

    filtra_pedido_destino = "" if pedido_destino is None else f"""--
        AND sl.PEDIDO_DESTINO = {pedido_destino}
    """

    filtra_op_destino = "" if op_destino is None else f"""--
        AND sl.OP_DESTINO = {op_destino}
    """

    filtra_oc_destino = "" if oc_destino is None else f"""--
        AND sl.OC_DESTINO = {oc_destino}
    """

    filtra_dep_destino = "" if dep_destino is None else f"""--
        AND sl.DEP_DESTINO = {dep_destino}
    """

    filtra_grupo_destino = "" if grupo_destino is None else f"""--
        AND
          CASE WHEN sl.GRUPO_DESTINO = '00000'
          THEN l.PROCONF_GRUPO
          ELSE sl.GRUPO_DESTINO
          END = '{grupo_destino}'
    """

    filtra_alter_destino = "" if alter_destino is None else f"""--
        AND sl.ALTER_DESTINO = {alter_destino}
    """

    filtra_sub_destino = "" if sub_destino is None else f"""--
        AND sl.SUB_DESTINO = {sub_destino}
    """

    filtra_cor_destino = "" if cor_destino is None else f"""--
        AND sl.COR_DESTINO = {cor_destino}
    """

    filtra_solicitacao = "" if solicitacao is None else f"""--
        AND sl.SOLICITACAO = {solicitacao}
    """

    sql = f"""--
        SELECT
          -- PK fields
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
          -- other fields
        , sl.SOLICITACAO
        , sl.SITUACAO
        , sl.QTDE
        , sl.PERIODO_OC
        , sl.INCLUSAO
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
          AND sl.SITUACAO not in (5, 9)
          {filtra_ordem_producao} -- filtra_ordem_producao
          {filtra_ordem_confeccao} -- filtra_ordem_confeccao
          {filtra_pedido_destino} -- filtra_pedido_destino
          {filtra_op_destino} -- filtra_op_destino
          {filtra_oc_destino} -- filtra_oc_destino
          {filtra_dep_destino} --filtra_dep_destino
          {filtra_grupo_destino} -- filtra_grupo_destino
          {filtra_alter_destino} -- filtra_alter_destino
          {filtra_sub_destino} -- filtra_sub_destino
          {filtra_cor_destino} -- filtra_cor_destino
          {filtra_solicitacao} -- filtra_solicitacao
    """
    if finaliza or cancela:
        situacao = 5 if finaliza else 9
        sql = f"""
            UPDATE SYSTEXTIL.PCPC_044
            SET
              SITUACAO = {situacao}
            WHERE (
              -- PK fields
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
    debug_cursor_execute(cursor, sql, exec=exec)
    if finaliza or cancela:
        return cursor.rowcount
    else:
        dados = dictlist_lower(cursor)
        return dados
