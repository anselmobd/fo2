from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


SQL_TIPO_FAT_META = {
    'mes': {
        'fields': """--
            , to_char(f.DATA_EMISSAO, 'MM/YYYY') MES
        """,
        'group': """--
            GROUP BY
              to_char(f.DATA_EMISSAO, 'MM/YYYY')
        """,
        'order': """--
            ORDER BY
              to_char(f.DATA_EMISSAO, 'MM/YYYY')
        """
    },
    'cliente': {
        'fields': """--
            , max(c.NOME_CLIENTE)
              || ' (' || lpad(c.CGC_9, 8, '0')
              || '/....-..)' CLIENTE
        """,
        'group': """--
            GROUP BY
              c.CGC_9
        """,
        'order': """--
            ORDER BY
              max(c.NOME_CLIENTE)
              || ' (' || lpad(c.CGC_9, 8, '0')
              || '/....-..)'
        """
    },
    'nota': {
        'fields': """--
            , f.NUM_NOTA_FISCAL NF
            , f.DATA_EMISSAO DATA
            , c.NOME_CLIENTE
              || ' (' || lpad(c.CGC_9, 8, '0')
              || '/' || lpad(c.CGC_4, 4, '0')
              || '-' || lpad(c.CGC_2, 2, '0')
              || ')' CLIENTE
            , n.COD_NATUREZA NAT
            , n.DIVISAO_NATUR DIV
            , ped.PEDIDO_VENDA PEDIDO
            , ped.COD_PED_CLIENTE PEDIDO_CLIENTE
        """,
        'group': """--
            GROUP BY
              f.NUM_NOTA_FISCAL
            , f.DATA_EMISSAO
            , c.NOME_CLIENTE
            , c.CGC_9
            , c.CGC_4
            , c.CGC_2
            , n.COD_NATUREZA
            , n.DIVISAO_NATUR
            , ped.PEDIDO_VENDA
            , ped.COD_PED_CLIENTE
        """,
        'order': """--
            ORDER BY
              f.NUM_NOTA_FISCAL
        """
    },
    'nota_referencia': {
        'fields': """--
            , f.NUM_NOTA_FISCAL NF
            , f.DATA_EMISSAO DATA
            , c.NOME_CLIENTE
              || ' (' || lpad(c.CGC_9, 8, '0')
              || '/' || lpad(c.CGC_4, 4, '0')
              || '-' || lpad(c.CGC_2, 2, '0')
              || ')' CLIENTE
            , n.COD_NATUREZA NAT
            , n.DIVISAO_NATUR DIV
            , ped.PEDIDO_VENDA PEDIDO
            , ped.COD_PED_CLIENTE PEDIDO_CLIENTE
            , fi.NIVEL_ESTRUTURA NIVEL
            , fi.GRUPO_ESTRUTURA REF
        """,
        'group': """--
            GROUP BY
              f.NUM_NOTA_FISCAL
            , f.DATA_EMISSAO
            , c.NOME_CLIENTE
            , c.CGC_9
            , c.CGC_4
            , c.CGC_2
            , n.COD_NATUREZA
            , n.DIVISAO_NATUR
            , ped.PEDIDO_VENDA
            , ped.COD_PED_CLIENTE
            , fi.NIVEL_ESTRUTURA
            , fi.GRUPO_ESTRUTURA
        """,
        'order': """--
            ORDER BY
              f.NUM_NOTA_FISCAL
            , fi.GRUPO_ESTRUTURA
        """
    },
    'referencia': {
        'fields': """--
            , fi.NIVEL_ESTRUTURA NIVEL
            , fi.GRUPO_ESTRUTURA REF
            , co.COLECAO || '-' || co.DESCR_COLECAO COLECAO
        """,
        'group': """--
            GROUP BY
              fi.NIVEL_ESTRUTURA
            , fi.GRUPO_ESTRUTURA
            , co.COLECAO
            , co.DESCR_COLECAO
        """,
        'order': """--
            ORDER BY
              fi.NIVEL_ESTRUTURA
            , fi.GRUPO_ESTRUTURA
        """
    },
    'modelo': {
        'fields': """--
            , CASE WHEN fi.NIVEL_ESTRUTURA = 1 THEN
                TO_NUMBER(
                  REGEXP_REPLACE(fi.GRUPO_ESTRUTURA, '[^0-9]', '')
                )
              ELSE 0
              END
              MODELO
            , co.COLECAO || '-' || co.DESCR_COLECAO COLECAO
        """,
        'group': """--
            GROUP BY
              CASE WHEN fi.NIVEL_ESTRUTURA = 1 THEN
                TO_NUMBER(
                  REGEXP_REPLACE(fi.GRUPO_ESTRUTURA, '[^0-9]', '')
                )
              ELSE 0
              END
            , co.COLECAO
            , co.DESCR_COLECAO
        """,
        'order': """--
            ORDER BY
              CASE WHEN fi.NIVEL_ESTRUTURA = 1 THEN
                TO_NUMBER(
                  REGEXP_REPLACE(fi.GRUPO_ESTRUTURA, '[^0-9]', '')
                )
              ELSE 0
              END
            , co.COLECAO
        """
    },
    'colecao': {
        'fields': """--
            , co.COLECAO || '-' || co.DESCR_COLECAO COLECAO
        """,
        'group': """--
            GROUP BY
              co.COLECAO
            , co.DESCR_COLECAO
        """,
        'order': """--
            ORDER BY
              co.COLECAO
        """
    },
}


def faturamento_para_meta(
        cursor, ano, mes=None, tipo='mes', empresa=1,
        ref=None, ordem='apresentacao', cliente=None,
        colecao=None, verifica_devolucao=False):
    '''
        tipo: 
            mes - totaliza por mês
            cliente - totaliza por cliente
            nota - mostra por nota
            nota_referencia - mostra por nota e referência
            referencia - totaliza por referência
            modelo - totaliza por modelo
            colecao - totaliza por colecao
    '''
    ano = str(ano)
    if mes is None:
        prox_ano = str(int(ano) + 1)
        mes = '01'
        prox_mes = '01'
    else:
        mes = int(mes)
        if mes == 12:
            prox_mes = 1
            prox_ano = str(int(ano) + 1)
        else:
            prox_mes = mes + 1
            prox_ano = ano
        mes = f"{mes:02}"
        prox_mes = f"{prox_mes:02}"

    filtra_emissao = f"""
        AND f.DATA_EMISSAO >=
            TIMESTAMP '{ano}-{mes}-01 00:00:00.000'
        AND f.DATA_EMISSAO <
            TIMESTAMP '{prox_ano}-{prox_mes}-01 00:00:00.000'
    """

    filtra_ref = ""
    if ref:
        filtra_ref = f"AND fi.GRUPO_ESTRUTURA = '{ref}'"

    filtra_colecao = ""
    if colecao is not None:
        filtra_colecao = f"AND r.COLECAO = '{colecao}'"

    filtro_cliente = ''
    if cliente is not None and cliente != '':
        filtro_cliente = f'''--
            AND c.NOME_CLIENTE
              || ' (' || lpad(c.CGC_9, 8, '0')
              || '/' || lpad(c.CGC_4, 4, '0')
              || '-' || lpad(c.CGC_2, 2, '0')
              || ')' like '%{cliente}%' '''

    filtra_devolvidas = ''
    if verifica_devolucao:
        filtra_devolvidas = """
            -- sem nota de devolução
            AND fe.DOCUMENTO IS NULL
        """

    sql_fields = SQL_TIPO_FAT_META[tipo]['fields']
    sql_group = SQL_TIPO_FAT_META[tipo]['group']
    if ordem == 'apresentacao':
        sql_order = SQL_TIPO_FAT_META[tipo]['order']
    elif ordem == 'valor':
        sql_order = """
            ORDER BY
              1 DESC
        """
    else:  # ordem == 'qtd':
        sql_order = """
            ORDER BY
              2 DESC
        """

    sql = f"""
        SELECT
          sum(fi.VALOR_FATURADO +  fi.RATEIO_DESPESA) VALOR
        , sum(fi.QTDE_ITEM_FATUR) QTD
        {sql_fields} -- fields
        FROM FATU_050 f
        JOIN fatu_060 fi
          ON fi.ch_it_nf_cd_empr = f.codigo_empresa
         and fi.ch_it_nf_num_nfis = f.num_nota_fiscal
         and fi.ch_it_nf_ser_nfis = f.serie_nota_fisc
         AND fi.NR_CAIXA = 0
        JOIN BASI_030 r
          ON r.NIVEL_ESTRUTURA = fi.NIVEL_ESTRUTURA 
        JOIN BASI_140 co
          ON co.COLECAO = r.COLECAO 
        AND r.REFERENCIA = fi.GRUPO_ESTRUTURA 
        JOIN estq_005 t
          ON t.CODIGO_TRANSACAO = fi.TRANSACAO
        JOIN PEDI_080 n
          ON n.NATUR_OPERACAO = f.NATOP_NF_NAT_OPER
         AND n.ESTADO_NATOPER = f.NATOP_NF_EST_OPER
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = f.CGC_9
         AND c.CGC_4 = f.CGC_4
         AND c.CGC_2 = f.CGC_2
        LEFT JOIN PEDI_100 ped -- pedido de venda  
          ON f.PEDIDO_VENDA > 0
         AND ped.PEDIDO_VENDA = f.PEDIDO_VENDA
        LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
          ON fe.NOTA_DEV = f.NUM_NOTA_FISCAL
         AND fe.SITUACAO_ENTRADA = 1 -- ativa
        WHERE 1=1
          AND f.CODIGO_EMPRESA = {empresa}
          {filtra_ref} -- filtra_ref
          {filtra_colecao} -- filtra_colecao
          {filtro_cliente} -- filtro_cliente
          -- ou o faturamento tem uma transação de venda
          -- ou é o caso especial de remessa de residuo
          AND ( t.TIPO_TRANSACAO = 'V'
              OR f.NATOP_NF_NAT_OPER = 900
              )
          -- filtro de faturamento baseado na view Faturados_X_Devolvidos
          -- filtrando faturamento_Sim_Nao = "Sim" e por data
          -- não cancelada
          AND f.COD_CANC_NFISC = 0
          -- utilizou natureza configurada como faturamento
          AND n.faturamento = 1
          {filtra_emissao} -- filtra_emissao
          {filtra_devolvidas} -- filtra_devolvidas
        {sql_group} -- group
        {sql_order} -- order
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
