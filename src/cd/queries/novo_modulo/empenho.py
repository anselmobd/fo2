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
    try:
        debug_cursor_execute(cursor, sql)
        return cursor.rowcount
    except Exception as e:
        return -1
