from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def query(cursor):
    sql = f"""
            SELECT 
            lp.ORDEM_CONFECCAO lote
            , l.PROCONF_GRUPO ref
            , --
                COALESCE(
                  ( SELECT
                      LISTAGG(DISTINCT COALESCE(TO_CHAR(sl.SOLICITACAO), '#'), ', ')
                      WITHIN GROUP (ORDER BY sl.SOLICITACAO) colicitacoes
                    FROM pcpc_044 sl -- solicitação / lote 
                    WHERE 1=1
                      AND sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                      AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO 
                      AND sl.ORDEM_CONFECCAO <> 0 
                      AND sl.GRUPO_DESTINO <> '0'
                      AND sl.SITUACAO IN (1, 2, 3, 4)
                  ),
                '-'
                )
             solicitacoes
            , --
                COALESCE(
                  ( SELECT
                      SUM(sl.QTDE) qtd_sol
                    FROM pcpc_044 sl -- solicitação / lote 
                    WHERE 1=1
                      AND sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                      AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO 
                      AND sl.ORDEM_CONFECCAO <> 0 
                      AND sl.GRUPO_DESTINO <> '0'
                      AND sl.SITUACAO IN (1, 2, 3, 4)
                      AND sl.SOLICITACAO IS NULL
                  ),
                0
                )
             qtd_emp
            , --
                COALESCE(
                  ( SELECT
                      SUM(sl.QTDE) qtd_sol
                    FROM pcpc_044 sl -- solicitação / lote 
                    WHERE 1=1
                      AND sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                      AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO 
                      AND sl.ORDEM_CONFECCAO <> 0 
                      AND sl.GRUPO_DESTINO <> '0'
                      AND sl.SITUACAO IN (1, 2, 3, 4)
                      AND sl.SOLICITACAO IS NOT NULL
                  ),
                0
                )
             qtd_sol
            , tam.ORDEM_TAMANHO ordem_tam
            , l.QTDE_DISPONIVEL_BAIXA qtd_dbaixa
            , l.QTDE_PECAS_PROG qtd_prog
            , l.ORDEM_PRODUCAO op
            , l.PROCONF_ITEM cor
            , l.PROCONF_SUBGRUPO tam
            , --
                CASE
                  WHEN lp.COD_CONTAINER IS NOT NULL
                   AND lp.COD_CONTAINER <> '0'
                  THEN lp.COD_CONTAINER
                  ELSE '-'
                END
             palete
            , COALESCE(ec.COD_ENDERECO, '-') endereco
            , COALESCE(e.ROTA, '-') rota
            , COALESCE(l.CODIGO_ESTAGIO, 999) estagio
            , 
                ( SELECT
                    MOD(( SELECT 
                            MAX(
                              CASE WHEN l2.CODIGO_ESTAGIO = 63 THEN 163
                              ELSE l2.CODIGO_ESTAGIO
                              END
                            )
                          FROM pcpc_040 l2
                          WHERE 1=1
                            AND l2.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                            AND l2.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                            AND l2.QTDE_DISPONIVEL_BAIXA > 0
                        )
                    , 100
                    )
                  FROM dual
                )
             est_sol -- fields
            --
                , +l.QTDE_DISPONIVEL_BAIXA qtd
             -- field_qtd
            FROM ENDR_014 lp
            JOIN PCPC_040 l
              ON l.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO 
             AND l.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000)
            LEFT JOIN ENDR_015 ec -- endereço/container 
              ON ec.COD_CONTAINER = lp.COD_CONTAINER
            LEFT JOIN ENDR_013 e -- endereço
              ON e.COD_ENDERECO = ec.COD_ENDERECO
             -- tipo_join
             -- join_para_colecao
            LEFT JOIN BASI_220 tam -- cadastro de tamanhos
              ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
            WHERE 1=1
             -- filtra_estagio
            --
                AND l.QTDE_DISPONIVEL_BAIXA > 0
             -- tipo_filter
            AND l.PROCONF_GRUPO in ('0156M') -- filter_ref
             -- filter_colecao
             -- filter_lote
             -- filter_endereco
             -- filter_op
            AND l.PROCONF_ITEM = '0000AJ' -- filter_cor
             -- filter_tam        
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
