from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


__all__ = ['palete_solicitacao_query']


def palete_solicitacao_query(cursor, solicitacao=None):
    filtra_solicitacao = f"""--
        AND sl.SOLICITACAO = {solicitacao}
        AND sl.GRUPO_DESTINO <> '0'
        AND sl.SITUACAO IN (1, 2, 3, 4)
        AND sl.QTDE <> 0
    """ if solicitacao else ''

    sql = f"""
        WITH
          paletes AS 
        ( SELECT DISTINCT
            lp.COD_CONTAINER palete
          , COALESCE(ec.COD_ENDERECO, '-') endereco
          FROM ENDR_014 lp
          LEFT JOIN ENDR_015 ec -- endereço/container 
            ON ec.COD_CONTAINER = lp.COD_CONTAINER
          LEFT JOIN pcpc_044 sl -- solicitação / lote
            ON sl.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000)
           AND sl.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO
          WHERE lp.COD_CONTAINER IS NOT NULL
            AND lp.COD_CONTAINER <> '0'
            {filtra_solicitacao} -- filtra_solicitacao
        )
        SELECT 
          pa.*
        , ( SELECT 
                COUNT(DISTINCT COALESCE(TO_CHAR(sl.SOLICITACAO), '#'))
            FROM ENDR_014 lp
            JOIN pcpc_044 sl -- solicitação / lote
              ON sl.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000)
             AND sl.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO
            WHERE 1=1
              AND sl.PEDIDO_DESTINO < 999000000
              AND lp.COD_CONTAINER = pa.palete
              AND sl.GRUPO_DESTINO <> '0'
              AND sl.SITUACAO IN (1, 2, 3, 4)
              AND sl.QTDE <> 0
          ) qpedsol
        , COALESCE(
            ( SELECT
                LISTAGG(DISTINCT COALESCE(TO_CHAR(sl.SOLICITACAO), '#'), ', ')
                WITHIN GROUP (ORDER BY sl.SOLICITACAO)
              FROM ENDR_014 lp
              JOIN pcpc_044 sl -- solicitação / lote
                ON sl.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000)
               AND sl.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO
              WHERE 1=1
                AND sl.PEDIDO_DESTINO < 999000000
                AND lp.COD_CONTAINER = pa.palete
                AND sl.GRUPO_DESTINO <> '0'
                AND sl.SITUACAO IN (1, 2, 3, 4)
                AND sl.QTDE <> 0
            )
          , '-'
          ) pedsol
        , ( SELECT 
                COUNT(DISTINCT COALESCE(TO_CHAR(sl.SOLICITACAO), '#'))
            FROM ENDR_014 lp
            JOIN pcpc_044 sl -- solicitação / lote
              ON sl.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000)
             AND sl.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO
            WHERE 1=1
              AND sl.PEDIDO_DESTINO >= 999000000
              AND lp.COD_CONTAINER = pa.palete
              AND sl.GRUPO_DESTINO <> '0'
              AND sl.SITUACAO IN (1, 2, 3, 4)
              AND sl.QTDE <> 0
          ) qagrupsol
        , COALESCE(
            ( SELECT
                LISTAGG(DISTINCT COALESCE(TO_CHAR(sl.SOLICITACAO), '#'), ', ')
                WITHIN GROUP (ORDER BY sl.SOLICITACAO)
              FROM ENDR_014 lp
              JOIN pcpc_044 sl -- solicitação / lote
                ON sl.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000)
               AND sl.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO
              WHERE 1=1
                AND sl.PEDIDO_DESTINO >= 999000000
                AND lp.COD_CONTAINER = pa.palete
                AND sl.GRUPO_DESTINO <> '0'
                AND sl.SITUACAO IN (1, 2, 3, 4)
                AND sl.QTDE <> 0
            )
          , '-'
          ) agrupsol
        FROM paletes pa
        WHERE 1=1
        --  AND pa.palete = 'PLT0001J'
        ORDER BY 
           3 DESC 
        ,  5 DESC
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    return dados
