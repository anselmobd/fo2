from utils.functions.models import dictlist_lower


def get_seq_est_op(cursor, op):
    sql = """
        SELECT DISTINCT
          l.SEQUENCIA_ESTAGIO SEQ
        , l.CODIGO_ESTAGIO EST
        FROM PCPC_040 l
        WHERE 1=1
          AND l.ORDEM_PRODUCAO = %s
        ORDER BY
          l.SEQUENCIA_ESTAGIO
        , l.CODIGO_ESTAGIO
    """
    cursor.execute(sql, [op])
    return dictlist_lower(cursor)
