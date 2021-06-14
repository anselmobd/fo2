from utils.functions.models import rows_to_dict_list


def ref_estrutura_comp(cursor, ref, alt):
    # Detalhando Estruturas
    sql = f"""
        SELECT DISTINCT
          e.SEQUENCIA
        , (
          SELECT
            LISTAGG(ee.ITEM_ITEM, ', ')
              WITHIN GROUP (ORDER BY ee.ITEM_ITEM)
          FROM BASI_050 ee
          WHERE ee.SEQUENCIA = e.SEQUENCIA
            AND ee.NIVEL_ITEM = e.NIVEL_ITEM
            AND ee.GRUPO_ITEM = e.GRUPO_ITEM
            AND ee.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
            AND ee.NIVEL_COMP = e.NIVEL_COMP
            AND ee.GRUPO_COMP = e.GRUPO_COMP
            AND ee.SUB_COMP = e.SUB_COMP
            AND ee.ITEM_COMP = e.ITEM_COMP
            AND ee.ALTERNATIVA_COMP = e.ALTERNATIVA_COMP
            AND ee.CONSUMO = e.CONSUMO
            AND ee.ESTAGIO = e.ESTAGIO
          ) COR_REF
        , e.NIVEL_COMP NIVEL
        , e.GRUPO_COMP REF
        , r.DESCR_REFERENCIA DESCR
        , e.SUB_COMP TAM
        , e.SUB_COMP ||
          CASE WHEN rsub.DESCR_TAM_REFER is not null
                AND rsub.DESCR_TAM_REFER <> 'UNICO'
                AND e.SUB_COMP <> rsub.DESCR_TAM_REFER
          THEN ' [' || rsub.DESCR_TAM_REFER || ']'
          ELSE ''
          END
          TAM_DESCR
        , CASE WHEN cocv.SUB_ITEM IS NULL
          THEN
            CASE WHEN e.ITEM_COMP = '000000'
            THEN '= ='
            ELSE e.ITEM_COMP ||
              CASE WHEN ritem.DESCRICAO_15 is not null
                    AND ritem.DESCRICAO_15 <> '.'
                    AND e.ITEM_COMP <> ritem.DESCRICAO_15
              THEN ' [' || ritem.DESCRICAO_15 || ']'
              ELSE ''
              END
            END
          ELSE
            CASE WHEN
              ( SELECT
                  count(DISTINCT coc1.ITEM_COMP)
                FROM BASI_040 coc1 -- comb. cor - verifica se é sempre a mesma
                WHERE e.ITEM_COMP = '000000'
                  AND coc1.SUB_ITEM = '000'
                  AND coc1.GRUPO_ITEM = e.GRUPO_ITEM
                  AND coc1.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
                  AND coc1.SEQUENCIA = e.SEQUENCIA
              ) = 1
            THEN '= ' ||
              CASE WHEN coc.ITEM_COMP = '000000'
              THEN '?'
              ELSE coc.ITEM_COMP
              END
            ELSE
              CASE WHEN e.NIVEL_COMP = 1
              THEN coc.ITEM_ITEM
              ELSE
                ( SELECT
                    LISTAGG(coc1.ITEM_ITEM, ', ')
                      WITHIN GROUP (ORDER BY coc1.ITEM_ITEM)
                  FROM BASI_040 coc1 -- comb. cor - com mesma tratucao
                  WHERE e.ITEM_COMP = '000000'
                    AND coc1.SUB_ITEM = '000'
                    AND coc1.GRUPO_ITEM = e.GRUPO_ITEM
                    AND coc1.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
                    AND coc1.SEQUENCIA = e.SEQUENCIA
                    AND coc1.ITEM_COMP = coc.ITEM_COMP
                )
              END
              || ' -> ' ||
              CASE WHEN coc.ITEM_COMP = '000000'
              THEN '?'
              ELSE coc.ITEM_COMP
              END
            END
          END COR
        , e.ALTERNATIVA_COMP ALTERN
        , e.CONSUMO
        , e.ESTAGIO || '-' || es.DESCRICAO ESTAGIO
        FROM BASI_050 e
        LEFT JOIN basi_030 r
          ON r.NIVEL_ESTRUTURA = e.NIVEL_COMP
         AND r.REFERENCIA = e.GRUPO_COMP
        LEFT JOIN BASI_010 ritem
          ON ritem.NIVEL_ESTRUTURA = e.NIVEL_COMP
         AND ritem.GRUPO_ESTRUTURA = e.GRUPO_COMP
         AND ritem.SUBGRU_ESTRUTURA = e.SUB_COMP
         AND ritem.ITEM_ESTRUTURA = e.ITEM_COMP
        LEFT JOIN BASI_020 rsub
          ON rsub.BASI030_NIVEL030 = e.NIVEL_COMP
         AND rsub.BASI030_REFERENC = e.GRUPO_COMP
         AND rsub.TAMANHO_REF = e.SUB_COMP
        LEFT JOIN BASI_040 cocv -- combinação cor - verifica se todos iguais
          ON e.ITEM_COMP = '000000'
         AND cocv.SUB_ITEM = '000'
         AND cocv.GRUPO_ITEM = e.GRUPO_ITEM
         AND cocv.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
         AND cocv.SEQUENCIA = e.SEQUENCIA
         AND cocv.ITEM_ITEM != cocv.ITEM_COMP
        LEFT JOIN BASI_040 coc -- combinação cor
          ON e.ITEM_COMP = '000000'
         AND cocv.SUB_ITEM IS NOT NULL
         AND coc.SUB_ITEM = '000'
         AND coc.GRUPO_ITEM = e.GRUPO_ITEM
         AND coc.ALTERNATIVA_ITEM = e.ALTERNATIVA_ITEM
         AND coc.SEQUENCIA = e.SEQUENCIA
        LEFT JOIN MQOP_005 es
          ON es.CODIGO_ESTAGIO = e.ESTAGIO
        WHERE e.NIVEL_ITEM = 1
          AND e.GRUPO_ITEM = '{ref}'
          AND e.ALTERNATIVA_ITEM = {alt}
        ORDER BY
          e.SEQUENCIA
        , 2
        , 7
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
