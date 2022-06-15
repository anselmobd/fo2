from pprint import pprint

from utils.functions.models.dictlist import dictlist


def infadprod_por_pedido(cursor, pedido, empresa=1):
    sql = '''
        SELECT
          p.PEDIDO_VENDA PEDIDO
        , c.NOME_CLIENTE
          || ' (' || lpad(c.CGC_9, 8, '0')
          || '/' || lpad(c.CGC_4, 4, '0')
          || '-' || lpad(c.CGC_2, 2, '0')
          || ')' CLIENTE
        , i.CD_IT_PE_NIVEL99 NIVEL
        , i.CD_IT_PE_GRUPO REF
        , i.CD_IT_PE_ITEM COR
        , i.CD_IT_PE_SUBGRUPO TAM
        , i.QTDE_PEDIDA QTD
        , i.VALOR_UNITARIO VALOR
        , coalesce( ip.REF_CLIENTE, '-') INFADPROD
        , coalesce( ip.DESCR_REF_CLIENTE, '-') DESCRCLI
        , coalesce( rtc.CODIGO_BARRAS, ' ') GTIN
        , CASE WHEN rtc.CODIGO_BARRAS IS NULL OR rtc.CODIGO_BARRAS = 'SEM GTIN'
          THEN 0
          ELSE (
            SELECT count(*)
            FROM BASI_010 gtin
            WHERE gtin.CODIGO_BARRAS = rtc.CODIGO_BARRAS
          )
          END COUNT_GTIN
        , rtc.NARRATIVA
        FROM PEDI_100 p -- pedido de venda
        LEFT JOIN PEDI_010 c
          ON c.CGC_9 = p.CLI_PED_CGC_CLI9
         AND c.CGC_4 = p.CLI_PED_CGC_CLI4
        JOIN PEDI_110 i -- item de pedido de venda
          ON i.PEDIDO_VENDA = p.PEDIDO_VENDA
        JOIN BASI_010 rtc -- item (ref+tam+cor)
          on rtc.NIVEL_ESTRUTURA = i.CD_IT_PE_NIVEL99
         AND rtc.GRUPO_ESTRUTURA = i.CD_IT_PE_GRUPO
         AND rtc.SUBGRU_ESTRUTURA = i.CD_IT_PE_SUBGRUPO
         AND rtc.ITEM_ESTRUTURA = i.CD_IT_PE_ITEM
        LEFT JOIN ESTQ_400 ip -- item - informações por cliente
          ON ip.CLIENTE9 = CLI_PED_CGC_CLI9
         AND ip.CLIENTE4 = CLI_PED_CGC_CLI4
         AND ip.NIVEL_ESTRUTURA = i.CD_IT_PE_NIVEL99
         AND ip.GRUPO_ESTRUTURA = i.CD_IT_PE_GRUPO
         AND ip.SUBGRUPO_ESTRUTURA = i.CD_IT_PE_SUBGRUPO
         AND ip.ITEM_ESTRUTURA = i.CD_IT_PE_ITEM
        LEFT JOIN BASI_220 t -- tamanhos
          ON t.TAMANHO_REF = i.CD_IT_PE_SUBGRUPO
        WHERE p.PEDIDO_VENDA = %s
          AND p.CODIGO_EMPRESA = %s
        ORDER BY
          p.PEDIDO_VENDA
        , p.CLI_PED_CGC_CLI9
        , p.CLI_PED_CGC_CLI4
        , i.CD_IT_PE_NIVEL99
        , i.CD_IT_PE_GRUPO
        , i.CD_IT_PE_ITEM
        , t.ORDEM_TAMANHO
        , i.CD_IT_PE_SUBGRUPO
    '''
    cursor.execute(sql, [pedido, empresa])
    return dictlist(cursor)
