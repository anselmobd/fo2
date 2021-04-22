from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def faturamento_para_meta(
        cursor, ano, mes=None, tipo='total', empresa=1,
        ref=None, ordem='apresentacao', cliente=None):
    '''
        tipo:
            total - totaliza por mês
            cliente - totaliza por cliente
            nota - mostra por nota
            nota_referencia - mostra por nota e referência
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

    filtra_ref = ""
    if ref:
        filtra_ref = f"AND fi.GRUPO_ESTRUTURA = '{ref}'"

    filtro_cliente = ''
    if cliente is not None and cliente != '':
        filtro_cliente = f'''--
            AND c.NOME_CLIENTE
              || ' (' || lpad(c.CGC_9, 8, '0')
              || '/' || lpad(c.CGC_4, 4, '0')
              || '-' || lpad(c.CGC_2, 2, '0')
              || ')' like '%{cliente}%' '''

    sql_tipo = {
        'total': {
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
            """,
            'group': """--
                GROUP BY
                  fi.NIVEL_ESTRUTURA
                , fi.GRUPO_ESTRUTURA
            """,
            'order': """--
                ORDER BY
                  fi.NIVEL_ESTRUTURA
                , fi.GRUPO_ESTRUTURA
            """
        },
        'modelo': {
            'fields': """--
                , TO_NUMBER(
                    REGEXP_REPLACE(fi.GRUPO_ESTRUTURA, '[^0-9]', '')
                  ) MODELO
            """,
            'group': """--
                GROUP BY
                  TO_NUMBER(
                    REGEXP_REPLACE(fi.GRUPO_ESTRUTURA, '[^0-9]', '')
                  )
            """,
            'order': """--
                ORDER BY
                  TO_NUMBER(
                    REGEXP_REPLACE(fi.GRUPO_ESTRUTURA, '[^0-9]', '')
                  )
            """
        },
    }

    if ordem == 'apresentacao':
        sql_order = sql_tipo[tipo]['order']
    else:
        sql_order = """
            ORDER BY
              1 DESC
        """

    sql = f"""
        SELECT
          sum(fi.VALOR_FATURADO +  fi.RATEIO_DESPESA) VALOR
        , sum(fi.QTDE_ITEM_FATUR) QTD
        {sql_tipo[tipo]['fields']} -- fields
        FROM FATU_050 f
        JOIN fatu_060 fi
          ON fi.ch_it_nf_cd_empr = f.codigo_empresa
         and fi.ch_it_nf_num_nfis = f.num_nota_fiscal
         and fi.ch_it_nf_ser_nfis = f.serie_nota_fisc
        JOIN estq_005 t
          ON t.CODIGO_TRANSACAO = fi.TRANSACAO
        JOIN PEDI_080 n
          ON n.NATUR_OPERACAO = f.NATOP_NF_NAT_OPER
         AND n.ESTADO_NATOPER = f.NATOP_NF_EST_OPER
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = f.CGC_9
         AND c.CGC_4 = f.CGC_4
        LEFT JOIN PEDI_100 ped -- pedido de venda  
          ON f.PEDIDO_VENDA > 0
         AND ped.PEDIDO_VENDA = f.PEDIDO_VENDA
        WHERE 1=1
          AND f.CODIGO_EMPRESA = {empresa}
          {filtra_ref} -- filtra_ref
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
          -- filtra data
          AND f.DATA_EMISSAO >=
              TIMESTAMP '{ano}-{mes}-01 00:00:00.000'
          AND f.DATA_EMISSAO <
              TIMESTAMP '{prox_ano}-{prox_mes}-01 00:00:00.000'
        {sql_tipo[tipo]['group']} -- group
        {sql_order} -- order
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def faturamento_para_meta_old(cursor, ano, mes=None, tipo='total', empresa=1, ref=None):
    '''
        tipo:
            total - totaliza por mês
            cliente - totaliza por cliente
            detalhe - mostra por nota
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

    filtra_ref = ""
    if ref:
        filtra_ref = f"AND fi.GRUPO_ESTRUTURA = '{ref}'"

    sql = """
        SELECT
    """
    if tipo == 'total':
        sql += """
              to_char(f.DATA_EMISSAO, 'MM/YYYY') MES
        """
    elif tipo == 'cliente':
        sql += """
              c.NOME_CLIENTE CLIENTE
        """
    elif tipo == 'referencia':
        sql += """
              f.NUM_NOTA_FISCAL NF
            , f.DATA_EMISSAO DATA
            , c.NOME_CLIENTE
              || ' (' || lpad(c.CGC_9, 8, '0')
              || '/' || lpad(c.CGC_4, 4, '0')
              || '-' || lpad(c.CGC_2, 2, '0')
              || ')' CLIENTE
            , n.COD_NATUREZA NAT
            , n.DIVISAO_NATUR DIV
            , fi.NIVEL_ESTRUTURA NIVEL
            , fi.GRUPO_ESTRUTURA REF
        """
    else:
        sql += """
              f.NUM_NOTA_FISCAL NF
            , f.DATA_EMISSAO DATA
            , c.NOME_CLIENTE
              || ' (' || lpad(c.CGC_9, 8, '0')
              || '/' || lpad(c.CGC_4, 4, '0')
              || '-' || lpad(c.CGC_2, 2, '0')
              || ')' CLIENTE
            , n.COD_NATUREZA NAT
            , n.DIVISAO_NATUR DIV
        """
    sql += f"""
        , sum(fi.VALOR_FATURADO +  fi.RATEIO_DESPESA) VALOR
        , sum(fi.QTDE_ITEM_FATUR) QTD
        FROM FATU_050 f
        JOIN fatu_060 fi
          ON fi.ch_it_nf_cd_empr = f.codigo_empresa
         and fi.ch_it_nf_num_nfis = f.num_nota_fiscal
         and fi.ch_it_nf_ser_nfis = f.serie_nota_fisc
        JOIN estq_005 t
          ON t.CODIGO_TRANSACAO = fi.TRANSACAO
        JOIN PEDI_080 n
          ON n.NATUR_OPERACAO = f.NATOP_NF_NAT_OPER
         AND n.ESTADO_NATOPER = f.NATOP_NF_EST_OPER
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = f.CGC_9
         AND c.CGC_4 = f.CGC_4
        WHERE 1=1
          AND f.CODIGO_EMPRESA = {empresa}
          {filtra_ref} -- filtra_ref
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
          -- filtra data
          AND f.DATA_EMISSAO >=
              TIMESTAMP '{ano}-{mes}-01 00:00:00.000'
          AND f.DATA_EMISSAO <
              TIMESTAMP '{prox_ano}-{prox_mes}-01 00:00:00.000'
    """
    if tipo == 'total':
        sql += """
            GROUP BY
              to_char(f.DATA_EMISSAO, 'MM/YYYY')
            ORDER BY
              to_char(f.DATA_EMISSAO, 'MM/YYYY')
        """
    elif tipo == 'cliente':
        sql += """
            GROUP BY
              c.NOME_CLIENTE
            ORDER BY
              c.NOME_CLIENTE
        """
    elif tipo == 'referencia':
        sql += """
            GROUP BY
              f.NUM_NOTA_FISCAL
            , f.DATA_EMISSAO
            , c.NOME_CLIENTE
            , c.CGC_9
            , c.CGC_4
            , c.CGC_2
            , n.COD_NATUREZA
            , n.DIVISAO_NATUR
            , fi.NIVEL_ESTRUTURA
            , fi.GRUPO_ESTRUTURA
            ORDER BY
              f.NUM_NOTA_FISCAL
            , fi.GRUPO_ESTRUTURA
        """
    else:
        sql += """
            GROUP BY
              f.NUM_NOTA_FISCAL
            , f.DATA_EMISSAO
            , c.NOME_CLIENTE
            , c.CGC_9
            , c.CGC_4
            , c.CGC_2
            , n.COD_NATUREZA
            , n.DIVISAO_NATUR
            ORDER BY
              f.NUM_NOTA_FISCAL
        """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
