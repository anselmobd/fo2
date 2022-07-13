from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor, sol_de, sol_ate, situacao):
    filtra_sol_de = f"""--
        AND coalesce(sl.SOLICITACAO, 0) >= {sol_de}
    """ if sol_de else ''

    filtra_sol_ate = f"""--
        AND coalesce(sl.SOLICITACAO, 0) <= {sol_ate}
    """ if sol_ate else ''

    filtra_situacao = ""
    if situacao:
        lista_sit = ', '.join(situacao)
        filtra_situacao = f"""--
            AND sl.SITUACAO in ({lista_sit})
        """

    sql = f"""
        SELECT
          coalesce(sl.SOLICITACAO, 0) sol
        , sl.PEDIDO_DESTINO ped
        , sl.ORDEM_PRODUCAO op
        , sl.ORDEM_CONFECCAO oc
        , sl.SITUACAO sit
        , sl.QTDE qtd_sol
        , l_ref.PROCONF_GRUPO ref
        , l_ref.PROCONF_SUBGRUPO tam
        , l_ref.PROCONF_ITEM cor
        , COALESCE(l.QTDE_DISPONIVEL_BAIXA, 0) qtd_63
        FROM PCPC_044 sl
        LEFT JOIN ENDR_014 lp
          ON lp.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO
         AND MOD(lp.ORDEM_CONFECCAO, 100000) = sl.ORDEM_CONFECCAO
        LEFT JOIN ENDR_015 ec -- endereço/container 
          ON ec.COD_CONTAINER = lp.COD_CONTAINER
        LEFT JOIN PCPC_040 l_ref
          ON l_ref.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO 
         AND l_ref.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
         AND l_ref.SEQUENCIA_ESTAGIO = 1
        LEFT JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = sl.ORDEM_PRODUCAO 
         AND l.ORDEM_CONFECCAO = sl.ORDEM_CONFECCAO
         AND l.CODIGO_ESTAGIO = 63
        WHERE 1=1
          AND sl.ORDEM_CONFECCAO <> 0 
          AND sl.GRUPO_DESTINO <> '0'
          AND ec.COD_ENDERECO IS NULL 
          AND COALESCE(l.QTDE_DISPONIVEL_BAIXA, 0) > 0
          {filtra_sol_de} -- filtra_sol_de
          {filtra_sol_ate} -- filtra_sol_ate
          {filtra_situacao} -- filtra_situacao
        ORDER BY 
          sl.SOLICITACAO
        , sl.PEDIDO_DESTINO
        , sl.SITUACAO
        , sl.ORDEM_PRODUCAO
        , sl.ORDEM_CONFECCAO
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
