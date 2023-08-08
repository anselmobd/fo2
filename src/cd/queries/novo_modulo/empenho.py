from pprint import pprint, pformat

from utils.functions.queries import debug_cursor_execute


def insere(
    cursor,
    ordem_producao,
    ordem_confeccao,
    pedido_destino,
    op_destino,
    oc_destino,
    grupo_destino,
    alter_destino,
    sub_destino,
    cor_destino,
    solicitacao,
    situacao,
    qtde,
    # dep_destino, # 0
    # periodo_oc, # NULL
    # inclusao, # automático
    exec=True,
):
    sql = f"""
        INSERT INTO SYSTEXTIL.PCPC_044 (
          ORDEM_PRODUCAO
        , ORDEM_CONFECCAO
        , PEDIDO_DESTINO
        , OP_DESTINO
        , OC_DESTINO
        , DEP_DESTINO
        , QTDE
        , SITUACAO
        , SOLICITACAO
        , PERIODO_OC
        , GRUPO_DESTINO
        , ALTER_DESTINO
        , SUB_DESTINO
        , COR_DESTINO
        --, INCLUSAO
        ) VALUES (
          {ordem_producao}
        , {ordem_confeccao}
        , {pedido_destino}
        , {op_destino}
        , {oc_destino}
        , 0
        , {qtde}
        , {situacao}
        , {solicitacao}
        , NULL
        , '{grupo_destino}'
        , {alter_destino}
        , '{sub_destino}'
        , '{cor_destino}'
        --, TIMESTAMP '2023-07-04 17:01:11.000000'
        )
    """
    debug_cursor_execute(cursor, sql, exec=exec)


def exclui(
    cursor,
    ordem_producao,
    ordem_confeccao,
    pedido_destino,
    op_destino,
    oc_destino,
    grupo_destino,
    alter_destino,
    sub_destino,
    cor_destino,
    exec=True,
):
    sql = f"""
        DELETE FROM SYSTEXTIL.PCPC_044
        WHERE 1=1
          AND ORDEM_PRODUCAO = {ordem_producao}
          AND ORDEM_CONFECCAO = {ordem_confeccao}
          AND PEDIDO_DESTINO = {pedido_destino}
          AND OP_DESTINO = {op_destino}
          AND OC_DESTINO = {oc_destino}
          AND DEP_DESTINO = 0
          AND GRUPO_DESTINO = '{grupo_destino}'
          AND ALTER_DESTINO = {alter_destino}
          AND SUB_DESTINO = '{sub_destino}'
          AND COR_DESTINO = '{cor_destino}'
    """
    debug_cursor_execute(cursor, sql, exec=exec)
