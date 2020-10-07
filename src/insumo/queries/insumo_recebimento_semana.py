from pprint import pprint

from utils.functions.models import rows_to_dict_list


def insumo_recebimento_semana(
        cursor, nivel, ref, cor, tam, dtini=None, nsem=None):

    try:
        filtra_DATA_PREV_ENTR = \
            "AND x.DATA_PREV_ENTR < " \
            "(TO_DATE('{dtini}','YYYYMMDD')+6+7*{nsem})".format(
                dtini=dtini, nsem=int(nsem)-1)
    except Exception:
        filtra_DATA_PREV_ENTR = ''

    sql = """
        SELECT
          TRUNC(x.DATA_PREV_ENTR, 'iw') SEMANA_ENTREGA
        , sum(
            GREATEST(
              CASE WHEN pc.COD_CANCELAMENTO = 0
                THEN x.QTDE_SALDO_ITEM
                ELSE 0 END
            , 0)
          ) QTD_A_RECEBER
        FROM SUPR_100 x -- item de pedido de compra
        JOIN SUPR_090 pc -- pedido de compra
          ON pc.PEDIDO_COMPRA = x.NUM_PED_COMPRA
        JOIN basi_030 r -- referencia
          ON r.NIVEL_ESTRUTURA = x.ITEM_100_NIVEL99
         AND r.REFERENCIA = x.ITEM_100_GRUPO
        WHERE 1=1
          AND x.ITEM_100_NIVEL99 = {nivel}
          AND x.ITEM_100_GRUPO = '{ref}'
          AND x.ITEM_100_SUBGRUPO = '{tam}'
          AND x.ITEM_100_ITEM = '{cor}'
          {filtra_DATA_PREV_ENTR} -- filtra_DATA_PREV_ENTR
        GROUP BY
          x.ITEM_100_NIVEL99
        , x.ITEM_100_GRUPO
        , x.ITEM_100_SUBGRUPO
        , x.ITEM_100_ITEM
        , TRUNC(x.DATA_PREV_ENTR, 'iw')
        HAVING
          ROUND(
            sum(
              GREATEST(
                CASE WHEN pc.COD_CANCELAMENTO = 0
                  THEN x.QTDE_SALDO_ITEM
                  ELSE 0 END
              , 0)
            ) / sum(x.QTDE_PEDIDA_ITEM) * 100
          , 1) >= 5
        ORDER BY
          1
    """.format(
        nivel=nivel,
        ref=ref,
        cor=cor,
        tam=tam,
        filtra_DATA_PREV_ENTR=filtra_DATA_PREV_ENTR
    )
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
