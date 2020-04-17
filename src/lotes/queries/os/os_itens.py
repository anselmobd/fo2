from utils.functions.models import rows_to_dict_list


def os_itens(cursor, os):
    # Itens para nota de OS
    sql = """
        SELECT
          s.PRODSAI_NIVEL99 NIVEL
        , s.PRODSAI_GRUPO REF
        , s.PRODSAI_ITEM COR
        , s.PRODSAI_SUBGRUPO TAM
        , i.NARRATIVA
        , r.UNIDADE_MEDIDA UN
        , s.VALOR_PRODUTO VALOR_UN
        , s.QTDE_ESTRUTURA QTD_ESTR
        , s.QTDE_ENVIADA QTD_ENV
        , s.NUM_NF_SAI NF
        , nf.DATA_EMISSAO DATA_NF
        , ce.DATA_EMISSAO - nf.DATA_EMISSAO DIAS
        , ie.CAPA_ENT_NRDOC NF_RETORNO
        , ce.DATA_EMISSAO DATA_RETORNO
        , ie.QUANTIDADE QTD_RETORNO
        , CASE
          WHEN ie.QUANTIDADE = s.QTDE_ENVIADA THEN 'Total'
          WHEN ie.QUANTIDADE < s.QTDE_ENVIADA THEN 'Parcial'
          ELSE 'Verificar'
          END RETORNO
        , CASE WHEN s.PRODSAI_NIVEL99 = 1 THEN
            CASE
            WHEN ce.NATOPER_NAT_OPER = 22 THEN 'Sim'
            WHEN ce.NATOPER_NAT_OPER = 23 THEN 'Não'
            ELSE 'Verificar'
            END
          ELSE '-'
          END APLICADO
        FROM OBRF_082 s
        JOIN BASI_010 i
          ON i.NIVEL_ESTRUTURA = s.PRODSAI_NIVEL99
         AND i.GRUPO_ESTRUTURA = s.PRODSAI_GRUPO
         AND i.SUBGRU_ESTRUTURA = s.PRODSAI_SUBGRUPO
         AND i.ITEM_ESTRUTURA = s.PRODSAI_ITEM
        JOIN BASI_030 r
          ON r.NIVEL_ESTRUTURA = s.PRODSAI_NIVEL99
         AND r.REFERENCIA = s.PRODSAI_GRUPO
        LEFT JOIN BASI_220 tam
          ON tam.TAMANHO_REF = s.PRODSAI_SUBGRUPO
        LEFT JOIN FATU_050 nf -- nota fiscal da Tussor
          ON nf.NUM_NOTA_FISCAL = s.NUM_NF_SAI
        LEFT JOIN OBRF_015 ie -- item de nota fiscal de entrada
          ON s.NUM_NF_SAI <> 0
         AND ie.NUM_NOTA_ORIG = s.NUM_NF_SAI
         AND ie.CODITEM_NIVEL99 = s.PRODSAI_NIVEL99
         AND ie.CODITEM_GRUPO = s.PRODSAI_GRUPO
         AND ie.CODITEM_SUBGRUPO = s.PRODSAI_SUBGRUPO
         AND ie.CODITEM_ITEM = s.PRODSAI_ITEM
        LEFT JOIN OBRF_010 ce -- capa de nota fiscal de entrada
          ON ce.DOCUMENTO = ie.CAPA_ENT_NRDOC
         AND ce.CGC_CLI_FOR_9 = ie.CAPA_ENT_FORCLI9
         AND ce.CGC_CLI_FOR_4 = ie.CAPA_ENT_FORCLI4
        WHERE s.NUMERO_ORDEM = %s
        ORDER BY
          s.PRODSAI_NIVEL99
        , s.PRODSAI_GRUPO
        , s.PRODSAI_ITEM
        , tam.ORDEM_TAMANHO
    """
    cursor.execute(sql, [os])
    return rows_to_dict_list(cursor)
