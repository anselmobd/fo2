from fo2.models import rows_to_dict_list_lower, dict_list_to_lower

from lotes.models.base import *


def get_imprime_lotes(cursor, op, tam, cor, order, oc_ini, oc_fim,
                      pula, qtd_lotes):
    # get dados de lotes
    data = get_lotes(cursor, op=op, tam=tam, cor=cor, order=order,
                     oc_ini=oc_ini, oc_fim=oc_fim,
                     pula=pula, qtd_lotes=qtd_lotes)
    data = dict_list_to_lower(data)
    return data


def get_imprime_caixas_op_3lotes(cursor, op):
    sql = '''
        WITH Table_qtd_lotes AS (
        SELECT
          ll.OP
        , ll.COR
        , ll.TAM
        , ll.PACOTE
        , MIN(ll.OC) OC1
        , COUNT(ll.OC) OC_COUNT
        , MAX(ll.OC) OC_MAX
        FROM (
        SELECT DISTINCT
          TRUNC( (
            row_number()
              over(
              partition BY
                os.PROCONF_ITEM
              , os.PROCONF_SUBGRUPO
              order BY
                os.ORDEM_CONFECCAO
              )
            + 2 )/ 3 ) PACOTE
        , os.ORDEM_PRODUCAO OP
        , os.PROCONF_ITEM COR
        , os.PROCONF_SUBGRUPO TAM
        , os.ORDEM_CONFECCAO OC
        FROM PCPC_040 os
        WHERE os.ORDEM_PRODUCAO = %s
        GROUP BY
          os.ORDEM_PRODUCAO
        , os.PROCONF_ITEM
        , os.PROCONF_SUBGRUPO
        , os.ORDEM_CONFECCAO
        ) ll
        GROUP BY
          ll.OP
        , ll.COR
        , ll.TAM
        , ll.PACOTE
        )
        select
          tb.*
        --
        , CASE tb.OC_COUNT
          WHEN 1 THEN NULL
          WHEN 2 THEN tb.OC_MAX
          WHEN 3 THEN
          (
            SELECT
              os_avg.ORDEM_CONFECCAO
            FROM PCPC_040 os_avg
            WHERE os_avg.ORDEM_PRODUCAO = tb.OP
              AND os_avg.PROCONF_ITEM = tb.COR
              AND os_avg.PROCONF_SUBGRUPO = tb.TAM
              AND os_avg.ORDEM_CONFECCAO > tb.OC1
              AND os_avg.ORDEM_CONFECCAO < tb.OC_MAX
              AND rownum = 1
        --    ORDER BY
        --      os_avg.ORDEM_PRODUCAO
        --    , os_avg.PROCONF_ITEM
        --    , os_avg.PROCONF_SUBGRUPO
        --    , os_avg.ORDEM_CONFECCAO
          ) -- AVG(ll.OC)
          END OC2
        --
        , CASE WHEN tb.OC_COUNT = 3
          THEN tb.OC_MAX
          ELSE NULL
          END OC3
        --
        , ( SELECT
              max( os.QTDE_PECAS_PROG )
            FROM PCPC_040 os
            WHERE os.PERIODO_PRODUCAO = o.PERIODO_PRODUCAO
              AND os.ORDEM_CONFECCAO = tb.OC1
          )    QTD1
        --
        , CASE tb.OC_COUNT
          WHEN 1 THEN NULL
          WHEN 2 THEN
          ( SELECT
              max( os.QTDE_PECAS_PROG )
            FROM PCPC_040 os
            WHERE os.PERIODO_PRODUCAO = o.PERIODO_PRODUCAO
              AND os.ORDEM_CONFECCAO = tb.OC_MAX
          )
          ELSE
          ( SELECT
              max( os.QTDE_PECAS_PROG )
            FROM PCPC_040 os
            WHERE os.PERIODO_PRODUCAO = o.PERIODO_PRODUCAO
              AND os.ORDEM_CONFECCAO = (
                SELECT
                  os_avg.ORDEM_CONFECCAO
                FROM PCPC_040 os_avg
                WHERE os_avg.ORDEM_PRODUCAO = tb.OP
                  AND os_avg.PROCONF_ITEM = tb.COR
                  AND os_avg.PROCONF_SUBGRUPO = tb.TAM
                  AND os_avg.ORDEM_CONFECCAO > tb.OC1
                  AND os_avg.ORDEM_CONFECCAO < tb.OC_MAX
                  AND rownum = 1
              )
          )
          END QTD2
        --
        , CASE WHEN tb.OC_COUNT = 3
          THEN
          ( SELECT
              max( os.QTDE_PECAS_PROG )
            FROM PCPC_040 os
            WHERE os.PERIODO_PRODUCAO = o.PERIODO_PRODUCAO
              AND os.ORDEM_CONFECCAO = tb.OC_MAX
          )
          ELSE NULL
          END QTD3
        --
        , o.SITUACAO
        , o.PERIODO_PRODUCAO PERIODO
        , o.REFERENCIA_PECA REF
        , o.DATA_ENTRADA_CORTE
        , t.ORDEM_TAMANHO TAMORD
        , r.NARRATIVA
        from Table_qtd_lotes tb
        JOIN PCPC_020 o -- OP capa
          ON o.ORDEM_PRODUCAO = tb.OP
        JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = tb.TAM
        JOIN BASI_010 r
          ON r.NIVEL_ESTRUTURA = 1
         AND r.GRUPO_ESTRUTURA = o.REFERENCIA_PECA
         AND r.SUBGRU_ESTRUTURA = tb.TAM
         AND r.ITEM_ESTRUTURA = tb.COR
        ORDER BY
          tb.COR
        , t.ORDEM_TAMANHO
        , tb.PACOTE
    '''

    cursor.execute(sql, [op])
    data = rows_to_dict_list_lower(cursor)
    return data
