from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower


def query(cursor, ano, mes=None, tipo='total', empresa=1, ref=None):
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
        filtra_ref = f"AND inf.CODITEM_GRUPO = '{ref}'"

    sql = """
        SELECT
    """
    if tipo == 'total':
        sql += """
              to_char(fe.DATA_TRANSACAO, 'MM/YYYY') MES
        """
    elif tipo == 'cliente':
        sql += """
              c.NOME_CLIENTE CLIENTE
        """
    elif tipo == 'referencia':
        sql += """
              fe.DOCUMENTO NF
            , fe.DATA_TRANSACAO DATA
            , c.NOME_CLIENTE
              || ' (' || lpad(c.CGC_9, 8, '0')
              || '/' || lpad(c.CGC_4, 4, '0')
              || '-' || lpad(c.CGC_2, 2, '0')
              || ')' CLIENTE
            , n.COD_NATUREZA NAT
            , n.DIVISAO_NATUR DIV
            , inf.CODITEM_GRUPO REF
        """
    else:
        sql += """
              fe.DOCUMENTO NF
            , fe.DATA_TRANSACAO DATA
            , c.NOME_CLIENTE
              || ' (' || lpad(c.CGC_9, 8, '0')
              || '/' || lpad(c.CGC_4, 4, '0')
              || '-' || lpad(c.CGC_2, 2, '0')
              || ')' CLIENTE
            , n.COD_NATUREZA NAT
            , n.DIVISAO_NATUR DIV
        """
    sql += f"""
        , sum(inf.VALOR_TOTAL-inf.VALOR_DESC) VALOR
        , sum(inf.QUANTIDADE) QTD
        FROM OBRF_010 fe -- capa de nota de entrada
        LEFT JOIN OBRF_015 inf
          ON inf.CAPA_ENT_FORCLI9 = fe.CGC_CLI_FOR_9
        AND inf.CAPA_ENT_FORCLI4 = fe.CGC_CLI_FOR_4
        AND inf.CAPA_ENT_FORCLI2 = fe.CGC_CLI_FOR_2
        AND inf.CAPA_ENT_NRDOC = fe.DOCUMENTO
        AND inf.CAPA_ENT_SERIE = fe.SERIE
        JOIN PEDI_080 n -- natureza de operação
          ON n.NATUR_OPERACAO = fe.NATOPER_NAT_OPER
         AND n.ESTADO_NATOPER = fe.NATOPER_EST_OPER
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = fe.CGC_CLI_FOR_9
         AND c.CGC_4 = fe.CGC_CLI_FOR_4
         AND c.CGC_2 = fe.CGC_CLI_FOR_2
        --WHERE fe.DOCUMENTO = 208240
        JOIN ESTQ_005 tre -- transações de estoque
          ON tre.CODIGO_TRANSACAO = fe.CODIGO_TRANSACAO
        LEFT JOIN FATU_050 f
          ON f.CGC_9 = fe.CGC_CLI_FOR_9
         AND f.CGC_4 = fe.CGC_CLI_FOR_4
         AND f.CGC_2 = fe.CGC_CLI_FOR_2
         AND f.SERIE_NOTA_FISC = fe.SERIE_DEV
         AND f.NUM_NOTA_FISCAL = fe.NOTA_DEV
        WHERE 1=1
          AND fe.LOCAL_ENTREGA = {empresa}
          {filtra_ref} -- filtra_ref
          -- filtro de devolvidos baseado na view Faturados_X_Devolvidos
          -- filtrando faturamento_Sim_Nao = "Sim" e por data
          -- situacao
          --   1 (nota própria não cancelada)
          --   2 (nota própria cancelada)
          --   4 (nota de terceiros)
          AND fe.SITUACAO_ENTRADA <> 2
          -- transação de estoque de Devolução
          AND tre.TIPO_TRANSACAO = 'D'
          -- não é nota de conhecimento
          AND fe.TIPO_CONHECIMENTO <> 1
          -- filtra data
          AND fe.DATA_TRANSACAO >=
              DATE '{ano}-{mes}-01'
          AND fe.DATA_TRANSACAO <
              DATE '{prox_ano}-{prox_mes}-01'
          -- se for devolução, nao pode ser devodução especial
          AND ( f.NUMERO_CAIXA_ECF IS NULL OR f.NUMERO_CAIXA_ECF = 0 )
    """
    if tipo == 'total':
        sql += """
            GROUP BY
              to_char(fe.DATA_TRANSACAO, 'MM/YYYY')
            ORDER BY
              to_char(fe.DATA_TRANSACAO, 'MM/YYYY')
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
              fe.DOCUMENTO
            , fe.DATA_TRANSACAO
            , c.NOME_CLIENTE
            , c.CGC_9
            , c.CGC_4
            , c.CGC_2
            , n.COD_NATUREZA
            , n.DIVISAO_NATUR
            , inf.CODITEM_GRUPO
            ORDER BY
              fe.DOCUMENTO
            , inf.CODITEM_GRUPO
        """
    else:
        sql += """
            GROUP BY
              fe.DOCUMENTO
            , fe.DATA_TRANSACAO
            , c.NOME_CLIENTE
            , c.CGC_9
            , c.CGC_4
            , c.CGC_2
            , n.COD_NATUREZA
            , n.DIVISAO_NATUR
            ORDER BY
              fe.DOCUMENTO
        """
    cursor.execute(sql)
    return dictlist_lower(cursor)
