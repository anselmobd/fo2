from pprint import pprint

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


def get_ref_colecao(cursor, ref):
    sql = '''
        SELECT
          r.COLECAO
        FROM BASI_030 r
        WHERE r.NIVEL_ESTRUTURA = 1
          AND r.REFERENCIA = %s
    '''
    cursor.execute(sql, [ref])
    data = rows_to_dict_list_lower(cursor)
    return data


def get_imprime_caixas_op_3lotes(cursor, op):
    sql = '''
        WITH Table_qtd_lotes AS (
        SELECT
          ll.OP
        , ll.COR
        , ll.TAM
        , ll.PACOTE
        , MIN(ll.LOTE) LOTE1
        , COUNT(ll.LOTE) LOTE_COUNT
        , MAX(ll.LOTE) LOTE_MAX
        FROM (
        SELECT DISTINCT
          TRUNC( (
            row_number()
              over(
              partition BY
                os.PROCONF_ITEM
              , os.PROCONF_SUBGRUPO
              order BY
                (os.PERIODO_PRODUCAO * 100000) + os.ORDEM_CONFECCAO
              )
            - 1 )/ (
                      CASE WHEN r.COLECAO = 5 -- camisa
                      THEN 2
                      ELSE 3
                      END
                   ) ) + 1 PACOTE
        , os.ORDEM_PRODUCAO OP
        , os.PROCONF_ITEM COR
        , os.PROCONF_SUBGRUPO TAM
        , (os.PERIODO_PRODUCAO * 100000) + os.ORDEM_CONFECCAO LOTE
        FROM PCPC_040 os
        JOIN BASI_030 r
          ON r.REFERENCIA = os.PROCONF_GRUPO
        WHERE os.ORDEM_PRODUCAO = %s
        GROUP BY
          os.ORDEM_PRODUCAO
        , r.COLECAO
        , os.PROCONF_ITEM
        , os.PROCONF_SUBGRUPO
        , (os.PERIODO_PRODUCAO * 100000) + os.ORDEM_CONFECCAO
        ) ll
        GROUP BY
          ll.OP
        , ll.COR
        , ll.TAM
        , ll.PACOTE
        ORDER BY
          ll.OP
        , ll.COR
        , ll.TAM
        , ll.PACOTE
        )
        SELECT
          tb.*
        --
        , CASE tb.LOTE_COUNT
          WHEN 1 THEN NULL
          WHEN 2 THEN tb.LOTE_MAX
          WHEN 3 THEN
          (
            SELECT
              (os_avg.PERIODO_PRODUCAO * 100000) + os_avg.ORDEM_CONFECCAO
            FROM PCPC_040 os_avg
            WHERE os_avg.ORDEM_PRODUCAO = tb.OP
              AND os_avg.PROCONF_ITEM = tb.COR
              AND os_avg.PROCONF_SUBGRUPO = tb.TAM
              AND os_avg.PERIODO_PRODUCAO >= trunc(tb.LOTE1 / 100000)
              AND os_avg.ORDEM_CONFECCAO > mod(tb.LOTE1, 100000)
              AND os_avg.PERIODO_PRODUCAO <= trunc(tb.LOTE_MAX / 100000)
              AND os_avg.ORDEM_CONFECCAO < mod(tb.LOTE_MAX, 100000)
              AND rownum = 1
          )
          END LOTE2
        --
        , CASE WHEN tb.LOTE_COUNT = 3
          THEN tb.LOTE_MAX
          ELSE NULL
          END LOTE3
        --
        , ( SELECT
              max( os.QTDE_PECAS_PROG )
            FROM PCPC_040 os
            WHERE os.PERIODO_PRODUCAO = trunc(tb.LOTE1 / 100000)
              AND os.ORDEM_CONFECCAO = mod(tb.LOTE1, 100000)
          )    QTD1
        --
        , CASE tb.LOTE_COUNT
          WHEN 1 THEN NULL
          WHEN 2 THEN
          ( SELECT
              max( os.QTDE_PECAS_PROG )
            FROM PCPC_040 os
            WHERE os.PERIODO_PRODUCAO = trunc(tb.LOTE_MAX / 100000)
              AND os.ORDEM_CONFECCAO = mod(tb.LOTE_MAX, 100000)
          )
          ELSE
          ( SELECT
              max( os.QTDE_PECAS_PROG )
            FROM PCPC_040 os
            WHERE os.PERIODO_PRODUCAO = trunc((
                SELECT
                  (os_avg.PERIODO_PRODUCAO * 100000) + os_avg.ORDEM_CONFECCAO
                FROM PCPC_040 os_avg
                WHERE os_avg.ORDEM_PRODUCAO = tb.OP
                  AND os_avg.PROCONF_ITEM = tb.COR
                  AND os_avg.PROCONF_SUBGRUPO = tb.TAM
                  AND os_avg.PERIODO_PRODUCAO >= trunc(tb.LOTE1 / 100000)
                  AND os_avg.ORDEM_CONFECCAO > mod(tb.LOTE1, 100000)
                  AND os_avg.PERIODO_PRODUCAO <= trunc(tb.LOTE_MAX / 100000)
                  AND os_avg.ORDEM_CONFECCAO < mod(tb.LOTE_MAX, 100000)
                  AND rownum = 1
              ) / 100000)
              AND os.ORDEM_CONFECCAO = mod((
                SELECT
                  (os_avg.PERIODO_PRODUCAO * 100000) + os_avg.ORDEM_CONFECCAO
                FROM PCPC_040 os_avg
                WHERE os_avg.ORDEM_PRODUCAO = tb.OP
                  AND os_avg.PROCONF_ITEM = tb.COR
                  AND os_avg.PROCONF_SUBGRUPO = tb.TAM
                  AND os_avg.PERIODO_PRODUCAO >= trunc(tb.LOTE1 / 100000)
                  AND os_avg.ORDEM_CONFECCAO > mod(tb.LOTE1, 100000)
                  AND os_avg.PERIODO_PRODUCAO <= trunc(tb.LOTE_MAX / 100000)
                  AND os_avg.ORDEM_CONFECCAO < mod(tb.LOTE_MAX, 100000)
                  AND rownum = 1
              ), 100000)
          )
          END QTD2
        --
        , CASE WHEN tb.LOTE_COUNT = 3
          THEN
          ( SELECT
              max( os.QTDE_PECAS_PROG )
            FROM PCPC_040 os
            WHERE os.PERIODO_PRODUCAO = trunc(tb.LOTE_MAX / 100000)
              AND os.ORDEM_CONFECCAO = mod(tb.LOTE_MAX, 100000)
          )
          ELSE NULL
          END QTD3
        --
        , o.SITUACAO
        , o.REFERENCIA_PECA REF
        , o.DATA_ENTRADA_CORTE
        , t.ORDEM_TAMANHO TAMORD
        , r.NARRATIVA
        , ref.DESCR_REFERENCIA
        , tam.DESCR_TAM_REFER DESCR_TAMANHO
        , r.DESCRICAO_15 DESCR_COR
        from Table_qtd_lotes tb
        JOIN PCPC_020 o -- OP capa
          ON o.ORDEM_PRODUCAO = tb.OP
        JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = tb.TAM
        JOIN BASI_030 ref
          ON ref.NIVEL_ESTRUTURA = 1
         AND ref.REFERENCIA = o.REFERENCIA_PECA
        JOIN BASI_020 tam
          ON tam.BASI030_NIVEL030 = 1
         AND tam.BASI030_REFERENC = o.REFERENCIA_PECA
         AND tam.TAMANHO_REF = tb.TAM
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

    for row in data:
        row['oc1'] = row['lote1'] % 100000
        row['oc_count'] = row['lote_count'] % 100000
        row['oc_max'] = row['lote_max'] % 100000
        row['lote1'] = str(row['lote1'])

        if row['lote2']:
            row['oc2'] = row['lote2'] % 100000
            row['lote2'] = str(row['lote2'])
        else:
            row['oc2'] = None
            row['lote2'] = ' '

        if row['lote3']:
            row['oc3'] = row['lote3'] % 100000
            row['lote3'] = str(row['lote3'])
        else:
            row['oc3'] = None
            row['lote3'] = ' '

    return data
