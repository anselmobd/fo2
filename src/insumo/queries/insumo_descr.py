from pprint import pprint

from utils.functions.models import rows_to_dict_list


def insumo_descr(cursor, nivel, ref, cor, tam):
    sql = f"""
        WITH item AS
        ( SELECT
            i.*
          FROM BASI_010 i -- item
          WHERE 1=1
            AND i.NIVEL_ESTRUTURA = {nivel}
            AND i.GRUPO_ESTRUTURA = '{ref}'
            AND i.SUBGRU_ESTRUTURA = '{tam}'
            AND i.ITEM_ESTRUTURA = '{cor}'
        )
        , parm AS
        ( SELECT
            p1.*
          FROM
          ( SELECT
              p.*
            FROM BASI_015 p
            JOIN item i
              ON i.NIVEL_ESTRUTURA = p.NIVEL_ESTRUTURA
             AND i.GRUPO_ESTRUTURA = p.GRUPO_ESTRUTURA
             AND i.SUBGRU_ESTRUTURA = p.SUBGRU_ESTRUTURA
             AND i.ITEM_ESTRUTURA = p.ITEM_ESTRUTURA
            WHERE ( p.ESTOQUE_MINIMO > 0
                  OR p.CODIGO_EMPRESA = 1
                  )
            ORDER BY
              p.ESTOQUE_MINIMO DESC
          ) p1
          WHERE rownum = 1
        )
        , estoque AS
        (
          SELECT
            sum(e.QTDE_ESTOQUE_ATU) QUANT
          , max(e.DATA_ULT_ENTRADA) ULT_ENTRADA
          , max(e.DATA_ULT_SAIDA) ULT_SAIDA
          , max(e.DT_INVENTARIO) DT_INVENTARIO
          FROM item ic
          JOIN BASI_030 i -- insumo
            ON i.NIVEL_ESTRUTURA = ic.NIVEL_ESTRUTURA
           AND i.REFERENCIA = ic.GRUPO_ESTRUTURA
          LEFT JOIN ESTQ_040 e -- estoque por depósito
            ON e.CDITEM_NIVEL99 = ic.NIVEL_ESTRUTURA
           AND e.CDITEM_GRUPO = ic.GRUPO_ESTRUTURA
           AND e.CDITEM_SUBGRUPO = ic.SUBGRU_ESTRUTURA
           AND e.CDITEM_ITEM = ic.ITEM_ESTRUTURA
           AND e.DEPOSITO =
               CASE WHEN i.NIVEL_ESTRUTURA = 2 THEN 202
               ELSE -- i.NIVEL_ESTRUTURA = 9
                 CASE WHEN i.CONTA_ESTOQUE = 22 THEN 212
                 WHEN i.CONTA_ESTOQUE = 77 THEN 731
                 ELSE 231
                 END
               END
        )
        SELECT
          i.NIVEL_ESTRUTURA NIVEL
        , i.REFERENCIA REF
        , i.DESCR_REFERENCIA DESCR
        , ic.ITEM_ESTRUTURA COR
        , ic.DESCRICAO_15 DESCR_COR
        , it.TAMANHO_REF TAM
        , it.DESCR_TAM_REFER DESCR_TAM
        , coalesce(parm.ESTOQUE_MINIMO, 0) STQ_MIN
        , coalesce(parm.TEMPO_REPOSICAO, 0) REPOSICAO
        , coalesce(parm.LOTE_MULTIPLO, 0) LOTE_MULTIPLO
        , i.UNIDADE_MEDIDA UNID
        , COALESCE(e.QUANT, 0) QUANT
        , e.ULT_ENTRADA
        , e.ULT_SAIDA
        , e.DT_INVENTARIO
        FROM item ic
        JOIN parm ON 1=1
        JOIN estoque e ON 1=1
        JOIN BASI_020 it -- insumo tamanho
          ON it.BASI030_NIVEL030 = ic.NIVEL_ESTRUTURA
         AND it.BASI030_REFERENC = ic.GRUPO_ESTRUTURA
         AND it.TAMANHO_REF = ic.SUBGRU_ESTRUTURA
        JOIN BASI_030 i -- insumo
          ON i.NIVEL_ESTRUTURA = ic.NIVEL_ESTRUTURA
         AND i.REFERENCIA = ic.GRUPO_ESTRUTURA
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
