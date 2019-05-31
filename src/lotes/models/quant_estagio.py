from fo2.models import rows_to_dict_list


def quant_estagio(cursor, estagio):
    sql = """
        SELECT
          l.CODIGO_ESTAGIO ESTAGIO
        , l.PROCONF_NIVEL99 NIVEL
        , l.PROCONF_GRUPO REF
        , l.PROCONF_SUBGRUPO TAM
        , l.PROCONF_ITEM COR
        , sum(
            CASE WHEN l.QTDE_EM_PRODUCAO_PACOTE > 0
            THEN 1
            ELSE 0
            END
          ) LOTES
        , sum(l.QTDE_EM_PRODUCAO_PACOTE) QUANT
        FROM PCPC_040 l
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE 1=1
        --  AND l.PERIODO_PRODUCAO = 1921
        --  AND l.ORDEM_CONFECCAO = 01866
          AND l.CODIGO_ESTAGIO = %s
        GROUP BY
          l.CODIGO_ESTAGIO
        , l.PROCONF_NIVEL99
        , l.PROCONF_GRUPO
        , t.ORDEM_TAMANHO
        , l.PROCONF_SUBGRUPO
        , l.PROCONF_ITEM
        HAVING
          sum(l.QTDE_EM_PRODUCAO_PACOTE) > 0
        ORDER BY
          l.CODIGO_ESTAGIO
        , l.PROCONF_NIVEL99
        , l.PROCONF_GRUPO
        , t.ORDEM_TAMANHO
        , l.PROCONF_ITEM
    """
    cursor.execute(sql, [estagio])
    return rows_to_dict_list(cursor)


def totais_estagios(cursor):
    sql = """
        SELECT
          l.CODIGO_ESTAGIO || ' - ' || e.DESCRICAO ESTAGIO
        , sum(
            CASE WHEN l.PROCONF_GRUPO <= '99999'
              AND l.QTDE_EM_PRODUCAO_PACOTE > 0
            THEN 1 ELSE 0 END
          ) LOTES_PA
        , sum(
            CASE WHEN l.PROCONF_GRUPO <= '99999'
            THEN l.QTDE_EM_PRODUCAO_PACOTE
            ELSE 0
            END
          ) QUANT_PA
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'A%'
              AND l.QTDE_EM_PRODUCAO_PACOTE > 0
            THEN 1 ELSE 0 END
          ) LOTES_PG
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'A%'
            THEN l.QTDE_EM_PRODUCAO_PACOTE
            ELSE 0
            END
          ) QUANT_PG
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'B%'
              AND l.QTDE_EM_PRODUCAO_PACOTE > 0
            THEN 1 ELSE 0 END
          ) LOTES_PB
        , sum(
            CASE WHEN l.PROCONF_GRUPO LIKE 'B%'
            THEN l.QTDE_EM_PRODUCAO_PACOTE
            ELSE 0
            END
          ) QUANT_PB
        , sum(
            CASE WHEN l.PROCONF_GRUPO >= 'C0000'
              AND l.QTDE_EM_PRODUCAO_PACOTE > 0
            THEN 1 ELSE 0 END
          ) LOTES_MD
        , sum(
            CASE WHEN l.PROCONF_GRUPO >= 'C0000'
            THEN l.QTDE_EM_PRODUCAO_PACOTE
            ELSE 0
            END
          ) QUANT_MD
        , sum(
            CASE WHEN l.QTDE_EM_PRODUCAO_PACOTE > 0
            THEN 1
            ELSE 0
            END
          ) LOTES
        , sum(l.QTDE_EM_PRODUCAO_PACOTE) QUANT
        FROM PCPC_040 l
        JOIN MQOP_005 e
          ON e.CODIGO_ESTAGIO = l.CODIGO_ESTAGIO
        GROUP BY
          l.CODIGO_ESTAGIO
        , e.DESCRICAO
        HAVING
          sum(l.QTDE_EM_PRODUCAO_PACOTE) > 0
        ORDER BY
          l.CODIGO_ESTAGIO
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
