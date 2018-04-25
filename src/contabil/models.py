from django.db import models

from fo2.models import rows_to_dict_list


def infadprod_pro_pedido(cursor, pedido):
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
        , coalesce( ip.REF_CLIENTE, '-') INFADPROD
        , coalesce( rtc.CODIGO_BARRAS, ' ') EAN
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
    cursor.execute(sql, [pedido])
    return rows_to_dict_list(cursor)


def reme_indu(cursor, data_de, data_ate):
    sql = '''
        SELECT
          1
        FROM DUAL
        WHERE 1=2
          AND %s=%s
    '''
    cursor.execute(sql, [data_de, data_ate])
    return rows_to_dict_list(cursor)
