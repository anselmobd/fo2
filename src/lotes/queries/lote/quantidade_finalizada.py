from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor, periodo, ordem_confeccao):
    sql = f"""
        SELECT
          l.QTDE_PECAS_PROD QTD
        , l.CODIGO_ESTAGIO ULTIMO_ESTAGIO
        , l.SEQUENCIA_ESTAGIO ULTIMA_SEQUENCIA
        FROM PCPC_040 l
          ON l.PERIODO_PRODUCAO = {periodo}
         AND l.ORDEM_CONFECCAO = {ordem_confeccao}
        WHERE l.SEQUENCIA_ESTAGIO
              = (
                SELECT
                  max(ms.SEQUENCIA_ESTAGIO)
                FROM PCPC_040 ms
                WHERE ms.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                  AND ms.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
              )
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
