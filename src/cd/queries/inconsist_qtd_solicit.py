from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute


def query(cursor):
    sql = f"""
        SELECT
          sl.ORDEM_PRODUCAO op
        , sl.ORDEM_CONFECCAO oc
        , l_63.QTDE_A_PRODUZIR_PACOTE qtd_lote
        , l_63.PERIODO_PRODUCAO per
        , l_63.PERIODO_PRODUCAO*100000+sl.ORDEM_CONFECCAO lote
        , sum(COALESCE(sl.QTDE, 0)) qtd_sols
        , LISTAGG(DISTINCT COALESCE(TO_CHAR(sl.SOLICITACAO), '#'), ', ')
          WITHIN GROUP (ORDER BY sl.SOLICITACAO) sols
        FROM PCPC_044 sl
        JOIN PCPC_040 l_63
          ON l_63.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND l_63.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO -- joins
        WHERE l_63.CODIGO_ESTAGIO = 63 -- WHERE
          AND sl.ORDEM_CONFECCAO <> 0 
          AND sl.GRUPO_DESTINO NOT IN ('0', '00000')
          AND sl.SITUACAO IN (1, 2, 3, 4)
          -- AND l_63.PROCONF_GRUPO like 'B0002'
        HAVING 
          l_63.QTDE_A_PRODUZIR_PACOTE < sum(sl.QTDE)
        GROUP BY 
          sl.ORDEM_PRODUCAO
        , sl.ORDEM_CONFECCAO
        , l_63.QTDE_A_PRODUZIR_PACOTE
        , l_63.PERIODO_PRODUCAO
        ORDER BY
          sl.ORDEM_PRODUCAO
        , sl.ORDEM_CONFECCAO
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
