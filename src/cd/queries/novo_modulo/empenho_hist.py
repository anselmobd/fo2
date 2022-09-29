from pprint import pprint, pformat

from utils.functions.queries import debug_cursor_execute


def insere_hist(
    cursor,
    usuario,
    alteracao,
    ordem_producao,
    ordem_confeccao,
    pedido_destino,
    op_destino,
    oc_destino,
    dep_destino,
    grupo_destino,
    alter_destino,
    sub_destino,
    cor_destino,
):
    field = ':'.join(alteracao.keys())
    field = f":{field}:"
    olds = []
    news = []
    for key in alteracao:
        olds.append(pformat(alteracao[key]['old']))
        news.append(pformat(alteracao[key]['new']))
    old = ':'.join(olds)
    new = ':'.join(news)

    sql = f"""
        INSERT INTO PCPC_044_HIST_DUOMO (
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
        , CAMPO_ALTERADO
        , ANTIGO_VALOR
        , NOVO_VALOR
        , USUARIO_SYSTEXTIL
        )
        SELECT
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
        , '{field}'
        , '{old}'
        , '{new}'
        , '{usuario}'
        FROM PCPC_044  -- empenhos
        WHERE 1=1
          AND ORDEM_PRODUCAO = {ordem_producao}
          AND ORDEM_CONFECCAO = {ordem_confeccao}
          AND PEDIDO_DESTINO = {pedido_destino}
          AND OP_DESTINO = {op_destino}
          AND OC_DESTINO = {oc_destino}
          AND DEP_DESTINO = {dep_destino}
          AND GRUPO_DESTINO = '{grupo_destino}'
          AND ALTER_DESTINO = {alter_destino}
          AND SUB_DESTINO = '{sub_destino}'
          AND COR_DESTINO = '{cor_destino}'
    """
    try:
        debug_cursor_execute(cursor, sql)
        return cursor.rowcount
    except Exception as e:
        return -1
