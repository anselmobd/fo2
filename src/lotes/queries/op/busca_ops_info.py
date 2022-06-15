from utils.functions.models.dictlist import dictlist_lower


def busca_ops_info(cursor, ops):
    filtro_op = ''
    sep = '('
    for op in ops:
        filtro_op += "{} '{}'".format(sep, op)
        sep = ','

    sql = """
        SELECT
          op.ORDEM_PRODUCAO OP
        , op.PEDIDO_VENDA PEDIDO
        FROM PCPC_020 op -- OP capa
        WHERE op.ORDEM_PRODUCAO IN
        --( 12345
        --, 12334
        {filtro_op} -- filtro_op
        )
    """.format(
        filtro_op=filtro_op,
    )

    cursor.execute(sql)
    return dictlist_lower(cursor)
