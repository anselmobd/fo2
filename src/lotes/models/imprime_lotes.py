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
        , CASE COUNT(ll.OC)
          WHEN 1 THEN NULL
          WHEN 2 THEN MAX(ll.OC)
          WHEN 3 THEN AVG(ll.OC)
          END OC2
        , CASE WHEN COUNT(ll.OC) = 3
          THEN MAX(ll.OC)
          ELSE NULL
          END OC3
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
