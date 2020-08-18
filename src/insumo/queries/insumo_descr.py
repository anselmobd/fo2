from pprint import pprint

from utils.functions.models import rows_to_dict_list


def insumo_descr(cursor, nivel, ref, cor, tam):
    sql = f"""
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
        , COALESCE(e.QTDE_ESTOQUE_ATU, 0) QUANT
        , e.DATA_ULT_ENTRADA ULT_ENTRADA
        , e.DATA_ULT_SAIDA ULT_SAIDA
        , e.DT_INVENTARIO
        FROM BASI_010 ic -- insumo cor
        JOIN BASI_020 it -- insumo tamanho
          ON it.BASI030_NIVEL030 = ic.NIVEL_ESTRUTURA
         AND it.BASI030_REFERENC = ic.GRUPO_ESTRUTURA
         AND it.TAMANHO_REF = ic.SUBGRU_ESTRUTURA
        JOIN BASI_030 i -- insumo
          ON i.NIVEL_ESTRUTURA = ic.NIVEL_ESTRUTURA
         AND i.REFERENCIA = ic.GRUPO_ESTRUTURA
        LEFT JOIN BASI_015 parm -- parâmetros de item
          ON parm.NIVEL_ESTRUTURA = ic.NIVEL_ESTRUTURA
         AND parm.GRUPO_ESTRUTURA = ic.GRUPO_ESTRUTURA
         AND parm.SUBGRU_ESTRUTURA = ic.SUBGRU_ESTRUTURA
         AND parm.ITEM_ESTRUTURA = ic.ITEM_ESTRUTURA
         AND parm.CODIGO_EMPRESA = 1
        LEFT JOIN ESTQ_040 e -- estoque por depósito
          ON e.CDITEM_NIVEL99 = ic.NIVEL_ESTRUTURA
         AND e.CDITEM_GRUPO = ic.GRUPO_ESTRUTURA
         AND e.CDITEM_SUBGRUPO = ic.SUBGRU_ESTRUTURA
         AND e.CDITEM_ITEM = ic.ITEM_ESTRUTURA
         -- vvv não tenho certeza disso, mas evita aparecer mais de um registro
         AND e.LOTE_ACOMP = 0
         AND e.DEPOSITO =
             CASE WHEN i.NIVEL_ESTRUTURA = 2 THEN 202
             ELSE -- i.NIVEL_ESTRUTURA = 9
               CASE WHEN i.CONTA_ESTOQUE = 22 THEN 212
               ELSE 231
               END
             END
        WHERE ic.NIVEL_ESTRUTURA = {nivel}
          AND ic.GRUPO_ESTRUTURA = '{ref}'
          AND ic.ITEM_ESTRUTURA = '{cor}'
          AND ic.SUBGRU_ESTRUTURA = '{tam}'
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)
