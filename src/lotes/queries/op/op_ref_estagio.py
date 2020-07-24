from utils.functions.models import rows_to_dict_list


def op_ref_estagio(cursor, op):
    # Totais por referência + estágio
    sql = '''
        SELECT
          lote.REF
        , lote.TAM
        , lote.COR
        , lote.EST
        , count(*) LOTES
        , sum(lote.QTD) QTD
        FROM (
          SELECT
            l.PROCONF_GRUPO REF
          , l.PROCONF_SUBGRUPO TAM
          , l.PROCONF_ITEM COR
          , COALESCE(
              ( SELECT
                  LISTAGG(le.CODIGO_ESTAGIO || ' - ' || ed.DESCRICAO, ' & ')
                  WITHIN GROUP (ORDER BY le.CODIGO_ESTAGIO)
                FROM PCPC_040 le
                JOIN MQOP_005 ed
                  ON ed.CODIGO_ESTAGIO = le.CODIGO_ESTAGIO
                WHERE le.PERIODO_PRODUCAO = l.PERIODO_PRODUCAO
                  AND le.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                  --AND le.QTDE_EM_PRODUCAO_PACOTE <> 0
                  AND le.QTDE_DISPONIVEL_BAIXA + le.QTDE_CONSERTO <> 0
              )
            , 'FINALIZADO'
            ) EST
          , l.QTDE_PECAS_PROG QTD
          FROM (
            SELECT
              os.PROCONF_GRUPO
            , os.PROCONF_SUBGRUPO
            , os.PROCONF_ITEM
            , os.PERIODO_PRODUCAO
            , os.ORDEM_CONFECCAO
            , max( os.NUMERO_ORDEM ) NUMERO_ORDEM
            , max( os.QTDE_PECAS_PROG ) QTDE_PECAS_PROG
            FROM PCPC_040 os
            WHERE os.ORDEM_PRODUCAO = %s
            GROUP BY
              os.PROCONF_GRUPO
            , os.PROCONF_SUBGRUPO
            , os.PROCONF_ITEM
            , os.PERIODO_PRODUCAO
            , os.ORDEM_CONFECCAO
          ) l
        ) lote
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = lote.TAM
        GROUP BY
          lote.REF
        , lote.COR
        , t.ORDEM_TAMANHO
        , lote.TAM
        , lote.EST
        ORDER BY
          lote.REF
        , lote.COR
        , t.ORDEM_TAMANHO
        , lote.EST
    '''
    cursor.execute(sql, [op])
    return rows_to_dict_list(cursor)
