from fo2.models import rows_to_dict_list

from lotes.models.base import *


def get_imprime_lotes(cursor, op, tam, cor, order, oc_ini, oc_fim,
                      pula, qtd_lotes):
    # get dados de lotes
    return get_lotes(cursor, op=op, tam=tam, cor=cor, order=order,
                     oc_ini=oc_ini, oc_fim=oc_fim,
                     pula=pula, qtd_lotes=qtd_lotes)


def get_imprime_pocote3lotes(cursor, op, tam, cor, pula, qtd_lotes):
    # Lotes ordenados por OP + OS + referência + estágio
    if pula is None:
        pula = 0
    if qtd_lotes is None:
        qtd_lotes = 100000
    sql = '''
        WITH Table_qtd_lotes AS (
        SELECT
          ll.OP
        , ll.SITUACAO
        , ll.PERIODO
        , ll.REF
        , ll.COR
        , ll.TAM
        , ll.NARRATIVA
        , ll.pacote
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
              , t.ORDEM_TAMANHO
              order BY
                os.ORDEM_CONFECCAO
              )
            + 2 )/ 3 ) PACOTE
        , os.ORDEM_PRODUCAO OP
        , op.SITUACAO
        , os.PERIODO_PRODUCAO PERIODO
        , os.PROCONF_GRUPO REF
        , os.PROCONF_ITEM COR
        , t.ORDEM_TAMANHO TAMORD
        , os.PROCONF_SUBGRUPO TAM
        , os.ORDEM_CONFECCAO OC
        , r.NARRATIVA
        FROM PCPC_040 os
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = os.PROCONF_SUBGRUPO
        JOIN PCPC_020 op -- OP capa
          ON op.ordem_producao = os.ORDEM_PRODUCAO
        JOIN BASI_010 r
          ON r.NIVEL_ESTRUTURA = 1
         AND r.GRUPO_ESTRUTURA = os.PROCONF_GRUPO
         AND r.SUBGRU_ESTRUTURA = os.PROCONF_SUBGRUPO
         AND r.ITEM_ESTRUTURA = os.PROCONF_ITEM
        WHERE 1=1
          AND (os.ORDEM_PRODUCAO = %s or %s IS NULL)
          AND (os.PROCONF_SUBGRUPO = %s OR %s IS NULL)
          AND (os.PROCONF_ITEM = %s OR %s IS NULL)
        GROUP BY
          os.ORDEM_PRODUCAO
        , op.SITUACAO
        , os.PERIODO_PRODUCAO
        , os.PROCONF_GRUPO
        , os.PROCONF_ITEM
        , t.ORDEM_TAMANHO
        , os.PROCONF_SUBGRUPO
        , os.ORDEM_CONFECCAO
        , r.NARRATIVA
        ) ll
        GROUP BY
          ll.OP
        , ll.SITUACAO
        , ll.PERIODO
        , ll.REF
        , ll.COR
        , ll.TAMORD
        , ll.TAM
        , ll.NARRATIVA
        , ll.pacote
        ORDER BY
          ll.OP
        , ll.SITUACAO
        , ll.PERIODO
        , ll.REF
        , ll.COR
        , ll.TAMORD
        , ll.NARRATIVA
        , ll.pacote
        )
        select * from Table_qtd_lotes where rownum <= %s
    '''

    qtd_rows = pula + qtd_lotes
    cursor.execute(
        sql, [op, op, tam, tam, cor, cor, qtd_rows])
    data = rows_to_dict_list(cursor)
    for i in range(0, pula):
        if len(data) != 0:
            del(data[0])
    return data
