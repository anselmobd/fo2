from datetime import datetime, date, timedelta
# from firebird.base import DatabaseWrapper
from pprint import pprint

from django.db import connections
from django.core.cache import cache
from django.conf import settings

from utils.functions.models import rows_to_dict_list, rows_to_dict_list_lower
from utils.functions.data import connect_fdb
from utils.functions import dec_months, my_make_key_cache, fo2logger


def busca_clientes(cnpj):
    # conn = DatabaseWrapper(settings.DATABASES_EXTRAS['f1'])
    erros = []
    conn = connect_fdb(settings.DATABASES_EXTRAS, 'f1', erros)
    if not conn:
        pprint(erros)
        return []

    cursor = conn.cursor()
    sql = f"""
        SELECT FIRST 10000
          c.C_CGC CNPJ
        , c.C_RSOC CLIENTE
        FROM DIS_CLI c
        WHERE c.C_CGC STARTING WITH '{cnpj[:14]}'
           OR c.C_RSOC CONTAINING '{cnpj}'
        ORDER BY
          c.C_CGC
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def ficha_cliente(cnpj):
    # conn = DatabaseWrapper(settings.DATABASES_EXTRAS['f1'])
    erros = []
    conn = connect_fdb(settings.DATABASES_EXTRAS, 'f1', erros)
    if not conn:
        pprint(erros)
        return []

    cursor = conn.cursor()
    sql = f"""
        SELECT
          c.C_CGC CNPJ
        , c.C_RSOC CLIENTE
        , d.D_DUPNUM DUPLICATA
        , d.D_STAT STAT
        , d.D_PEDNUM PEDIDO
        , d.D_DFAT EMISSAO
        , d.D_DVENCORI VENC_ORI
        , d.D_DVENC VENCIMENTO
        , CASE WHEN mod(ord(d.D_AUX), 2) = 1
          THEN 'P'
          ELSE ' '
          END PRORROGADO
        , CASE WHEN d.D_VPAGO = 0 AND d.D_DVENC < 'NOW'
          THEN d.D_VALOR
          ELSE d.D_VALOR*(1-(d.D_DESC/100))
          END VALOR
        , d.D_QTD QUANT
        , d.D_QTDFAT QUANT_FAT
        , d.D_DPAGO DATA_PAGO
        , d.D_VPAGO VALOR_PAGO
        , CASE WHEN d.D_DPAGO <> '1899.12.30' THEN
            CASE WHEN d.D_DVENC >= d.D_DPAGO THEN
              0 -- ''
            ELSE
              d.D_VPAGO - d.D_VALOR
            END
          ELSE
            CASE WHEN d.D_DVENC >= 'NOW' THEN
              0 -- ''
            WHEN d.D_VPAGO <> 0 THEN
              d.D_VPAGO - d.D_VALOR
            ELSE
              d.D_VALOR
              * (d.D_JUROS * ((cast('NOW' AS DATE) - d.D_DVENC)
                              / 3000.0000))
            END
          END JUROS
        , CASE WHEN d.D_DPAGO <> '1899.12.30' THEN
            CASE WHEN d.D_DVENC >= d.D_DPAGO THEN
              0
            ELSE
              d.D_DPAGO - d.D_DVENC
            END
          ELSE
            CASE WHEN d.D_DVENC >= 'NOW' THEN
              0
            ELSE
              cast('NOW' AS DATE) - d.D_DVENC
            END
          END ATRASO
        , d.D_OP OP
        , d.D_BANCO BANCO
        , d.D_DESCONTO DESCONTO
        , d.D_OBS OBSERVACAO
        FROM DIS_DUP d
        LEFT JOIN DIS_CLI c
          ON c.C_CGC = d.D_CGC
        WHERE d.D_CGC = '{cnpj}'
          AND D.D_STAT >= '0' -- nao canceladas
          AND d.D_CODFIS IN ( '5101', '6101', '6107', '6109'
                            , '5124', '6124', '5125', '6125') -- cpof de venda
        ORDER BY
          d.D_DUPNUM
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def get_modelo_dims(cursor, modelo=None, get=None):
    select_get = ''
    group_get = ''
    order_get = ''
    if get == 'ref':
        select_get = "e.REF"
        group_get = "e.REF"
        order_get = "e.REF"
    elif get == 'cor':
        select_get = "e.COR"
        group_get = "e.COR"
        order_get = "e.COR"
    elif get == 'tam':
        select_get = "t.ORDEM_TAMANHO\n, e.TAM"
        group_get = "t.ORDEM_TAMANHO\n, e.TAM"
        order_get = "t.ORDEM_TAMANHO\n, e.TAM"

    filtra_modelo = ''
    pre_filtra_modelo = ''
    if modelo is not None:
        filtra_modelo = "AND e.MODELO = '{}'".format(modelo)
        pre_filtra_modelo = \
            "AND i.GRUPO_ESTRUTURA LIKE '%{}%'".format(modelo)

    sql = f"""
        WITH refs AS (
          SELECT
            i.NIVEL_ESTRUTURA NIVEL
          , i.GRUPO_ESTRUTURA REF
          , TRIM(
              LEADING '0' FROM (
                REGEXP_REPLACE(
                  REGEXP_REPLACE(
                    i.GRUPO_ESTRUTURA
                  , '^(.+[^a-zA-Z])[a-zA-Z]*$'
                  , '\\1'
                  )
                , '^[a-zA-Z]([^a-zA-Z].+)*$'
                , '\\1'
                )
              )
            ) MODELO
          , i.SUBGRU_ESTRUTURA TAM
          , i.ITEM_ESTRUTURA COR
          FROM BASI_010 i -- (ref+tam+cor)
          WHERE i.NIVEL_ESTRUTURA = 1
            AND i.GRUPO_ESTRUTURA < 'C' -- apenas PA, PG e PB
            {pre_filtra_modelo} -- pre_filtra_modelo
        )
        SELECT
          {select_get} -- select_get
        FROM refs e
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = e.TAM
        WHERE 1=1
          {filtra_modelo} -- filtra_modelo
        GROUP BY
          {group_get} -- group_get
        ORDER BY
          {order_get} -- order_get
    """
    cursor.execute(sql)
    return rows_to_dict_list(cursor)


def get_vendas(
        cursor, ref=None, periodo=None, colecao=None, cliente=None, por=None,
        modelo=None, order_qtd=True, ultimos_dias=None):

    # key_cache = make_key_cache()
    key_cache = my_make_key_cache(
        'get_vendas', ref, periodo, colecao, cliente, por, modelo, order_qtd,
        ultimos_dias)

    cached_result = cache.get(key_cache)
    if cached_result is not None:
        fo2logger.info('cached '+key_cache)
        return cached_result

    if order_qtd:
        order = '1 DESC'
    else:
        order = ''

    def add_order(new_order):
        nonlocal order
        sep = "\n, " if order else ''
        order += sep + new_order

    filtra_col = ''
    if colecao is not None:
        ref = None
        filtra_col = "AND v.COL = '{}'".format(colecao)

    filtra_cliente = ''
    if cliente is not None:
        filtra_cliente = "AND v.CNPJ9 = '{}'".format(cliente)

    filtra_modelo = ''
    filtra_modelo_select_item = ''
    pre_filtra_modelo = ''
    if modelo is not None:
        filtra_modelo = "AND v.MODELO = '{}'".format(modelo)
        pre_filtra_modelo = \
            "AND inf.GRUPO_ESTRUTURA LIKE '%{}%'".format(modelo)
        filtra_modelo_select_item = f""" --
          AND TRIM(
                LEADING '0' FROM (
                  REGEXP_REPLACE(
                    v.GRUPO_ESTRUTURA
                  , '^([^a-zA-Z]+)[a-zA-Z]*$'
                  , '\\1'
                  )
                )
              ) = '{modelo}'
        """
    filtra_ref = ''
    pre_filtra_ref = ''
    if ref is not None:
        filtra_ref = "AND v.REF = '{}'".format(ref)
        pre_filtra_ref = "AND inf.GRUPO_ESTRUTURA = '{}'".format(ref)

    hoje = date.today()
    ini_mes = hoje.replace(day=1)
    filtra_periodo = ''
    pre_filtra_periodo = ''
    if periodo is not None:
        periodo_list = periodo.split(':')
        ini_periodo = dec_months(ini_mes, int(periodo_list[0]))
        filtra_periodo = "  AND v.dt >= TO_DATE('{}', 'yyyy-mm-dd')".format(
            ini_periodo.strftime('%Y-%m-%d'))
        pre_filtra_periodo = \
            "  AND nf.DATA_EMISSAO >= TO_DATE('{}', 'yyyy-mm-dd')".format(
                ini_periodo.strftime('%Y-%m-%d'))
        if periodo_list[1] != '':
            fim_periodo = dec_months(ini_mes, int(periodo_list[1]))
            filtra_periodo += \
                "  AND v.dt < TO_DATE('{}', 'yyyy-mm-dd')".format(
                    fim_periodo.strftime('%Y-%m-%d'))
            pre_filtra_periodo += \
                "  AND nf.DATA_EMISSAO < TO_DATE('{}', 'yyyy-mm-dd')".format(
                    fim_periodo.strftime('%Y-%m-%d'))

    filtra_ultimos_dias = ''
    pre_filtra_ultimos_dias = ''
    if ultimos_dias is not None:
        filtra_ultimos_dias = \
            "  AND v.dt >= ""TO_DATE('{}', 'yyyy-mm-dd') - {} + 1"
        filtra_ultimos_dias = filtra_ultimos_dias.format(
            hoje.strftime('%Y-%m-%d'), ultimos_dias)
        pre_filtra_ultimos_dias = \
            "  AND nf.DATA_EMISSAO >= TO_DATE('{}', 'yyyy-mm-dd') - {} + 1"
        pre_filtra_ultimos_dias = pre_filtra_ultimos_dias.format(
            hoje.strftime('%Y-%m-%d'), ultimos_dias)

    select_por = ''
    group_por = ''
    if por == 'modelo':
        select_por = ", v.MODELO"
        # no filtro por modelo não busca modelos com qtd zerada, por EMISSAO
        # apenas repete o valor, para, ao agrupar, não fazer diferença
        select_item = ", '{}' MODELO".format(modelo)
        select_global = select_por
        group_por = ", v.MODELO"
        add_order('v.MODELO')
    elif por == 'ref':
        select_por = ", v.REF"
        select_item = ", v.GRUPO_ESTRUTURA REF"
        select_global = select_por
        group_por = ", v.REF"
        add_order('v.REF')
    elif por == 'cor':
        select_por = ", v.COR"
        select_item = ", v.ITEM_ESTRUTURA COR"
        select_global = select_por
        group_por = ", v.COR"
        add_order('v.COR')
    elif por == 'tam':
        select_por = ", t.ORDEM_TAMANHO\n, v.TAM"
        select_item = ", t.ORDEM_TAMANHO\n, v.SUBGRU_ESTRUTURA TAM"
        select_global = ", v.ORDEM_TAMANHO\n, v.TAM"
        group_por = ", v.ORDEM_TAMANHO\n, v.TAM"
        add_order("v.ORDEM_TAMANHO\n, v.TAM")

    sql = f"""
        SELECT
          sum(v.qtd) qtd
          {select_global} -- select_global
        FROM (
        WITH vendido AS
        (
        SELECT
          nf.NUM_NOTA_FISCAL NF
        , nf.DATA_EMISSAO DT
        , nf.NATOP_NF_NAT_OPER NATOP
        , nop.COD_NATUREZA COD_NAT
        , nop.DIVISAO_NATUR DIV_NAT
        , inf.NIVEL_ESTRUTURA NIVEL
        , inf.GRUPO_ESTRUTURA REF
        , TRIM(LEADING '0' FROM
               (REGEXP_REPLACE(inf.GRUPO_ESTRUTURA,
                               '^([^a-zA-Z]+)[a-zA-Z]*$', '\\1'
                               ))) MODELO
        , inf.SUBGRU_ESTRUTURA TAM
        , inf.ITEM_ESTRUTURA COR
        , inf.QTDE_ITEM_FATUR QTD
        , inf.VALOR_UNITARIO PRECO
        , r.COLECAO COL
        , col.DESCR_COLECAO COLECAO
        , r.CGC_CLIENTE_9 CNPJ9
        FROM FATU_050 nf -- nota fiscal da Tussor - capa
        LEFT JOIN OBRF_010 fe -- nota fiscal de entrada/devolução
          ON fe.NOTA_DEV = nf.NUM_NOTA_FISCAL
         AND fe.SITUACAO_ENTRADA = 1 -- ativa
        JOIN PEDI_080 nop -- natureza da operação
          ON nop.NATUR_OPERACAO = nf.NATOP_NF_NAT_OPER
         AND nop.ESTADO_NATOPER = nf.NATOP_NF_EST_OPER
        JOIN fatu_060 inf -- item de nf de saída
          ON inf.CH_IT_NF_NUM_NFIS = nf.NUM_NOTA_FISCAL
        LEFT JOIN BASI_030 r -- item (ref+tam+cor)
          on r.NIVEL_ESTRUTURA = inf.NIVEL_ESTRUTURA
         AND r.REFERENCIA = inf.GRUPO_ESTRUTURA
        LEFT JOIN BASI_140 col
          ON col.COLECAO = r.COLECAO
        --JOIN BASI_010 rtc -- item (ref+tam+cor)
        --  on rtc.NIVEL_ESTRUTURA = inf.NIVEL_ESTRUTURA
        -- AND rtc.GRUPO_ESTRUTURA = inf.GRUPO_ESTRUTURA
        -- AND rtc.SUBGRU_ESTRUTURA = inf.SUBGRU_ESTRUTURA
        -- AND rtc.ITEM_ESTRUTURA = inf.ITEM_ESTRUTURA
        WHERE 1=1
          AND (nf.NATOP_NF_NAT_OPER IN (1, 2)
               OR (nop.DIVISAO_NATUR = 8
                   AND nop.COD_NATUREZA in ('5.11', '6.11')
                  )
              )
          AND nf.SITUACAO_NFISC = 1
          AND fe.DOCUMENTO IS NULL
          {pre_filtra_modelo} -- pre_filtra_modelo
          {pre_filtra_ref} -- pre_filtra_ref
          {pre_filtra_periodo} -- pre_filtra_periodo
          {pre_filtra_ultimos_dias} -- pre_filtra_ultimos_dias
        )
        SELECT
          v.qtd
          {select_por} -- select_por
        FROM vendido v
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = v.TAM
        WHERE 1=1
          -- AND v.dt > TO_DATE('2019-01-01', 'yyyy-mm-dd')
          {filtra_col} -- filtra_col
          {filtra_cliente} -- filtra_cliente
          {filtra_modelo} -- filtra_modelo
          {filtra_ref} -- filtra_ref
          {filtra_ultimos_dias} -- filtra_ultimos_dias
        --
        UNION
        --
        SELECT
          0
          {select_item} -- select_item
        FROM BASI_010 v -- item (ref+tam+cor)
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = v.SUBGRU_ESTRUTURA
        WHERE v.NIVEL_ESTRUTURA = 1
          {filtra_modelo_select_item} -- filtra_modelo_select_item
        ) v
        GROUP BY
          1
          {group_por} -- group_por
        ORDER BY
          {order} -- order
    """
    cursor.execute(sql)

    cached_result = rows_to_dict_list_lower(cursor)
    cache.set(key_cache, cached_result)
    fo2logger.info('calculated '+key_cache)
    return cached_result


def faturamento_para_meta(cursor, ano, mes=None, tipo='total', empresa=1):
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

    sql = """
        SELECT
    """
    if tipo == 'total':
        sql += """
              to_char(f.DATA_EMISSAO, 'MM/YYYY') MES
            , sum(f.BASE_ICMS) VALOR
        """
    elif tipo == 'cliente':
        sql += """
              c.NOME_CLIENTE CLIENTE
            , sum(f.BASE_ICMS) VALOR
        """
    else:
        sql += """
              f.NUM_NOTA_FISCAL NF
            , f.DATA_EMISSAO DATA
            , f.BASE_ICMS VALOR
            , c.NOME_CLIENTE
              || ' (' || lpad(c.CGC_9, 8, '0')
              || '/' || lpad(c.CGC_4, 4, '0')
              || '-' || lpad(c.CGC_2, 2, '0')
              || ')' CLIENTE
            , n.COD_NATUREZA NAT
            , n.DIVISAO_NATUR DIV
        """
    sql += f"""
        FROM FATU_050 f
        JOIN PEDI_080 n
          ON n.NATUR_OPERACAO = f.NATOP_NF_NAT_OPER
         AND n.ESTADO_NATOPER = f.NATOP_NF_EST_OPER
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = f.CGC_9
         AND c.CGC_4 = f.CGC_4
        WHERE 1=1
          AND f.CODIGO_EMPRESA = {empresa}
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
    else:
        sql += """
            ORDER BY
              f.NUM_NOTA_FISCAL
        """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def devolucao_para_meta(cursor, ano, mes=None, tipo='total', empresa=1):
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

    sql = """
        SELECT
    """
    if tipo == 'total':
        sql += """
              to_char(fe.DATA_TRANSACAO, 'MM/YYYY') MES
            , sum(fe.VALOR_ITENS - fe.VALOR_DESCONTO) VALOR
        """
    elif tipo == 'cliente':
        sql += """
              c.NOME_CLIENTE CLIENTE
            , sum(fe.VALOR_ITENS - fe.VALOR_DESCONTO) VALOR
        """
    else:
        sql += """
              fe.DOCUMENTO NF
            , fe.DATA_TRANSACAO DATA
            , fe.VALOR_ITENS - fe.VALOR_DESCONTO VALOR
            , c.NOME_CLIENTE
              || ' (' || lpad(c.CGC_9, 8, '0')
              || '/' || lpad(c.CGC_4, 4, '0')
              || '-' || lpad(c.CGC_2, 2, '0')
              || ')' CLIENTE
            , n.COD_NATUREZA NAT
            , n.DIVISAO_NATUR DIV
        """
    sql += f"""
        FROM OBRF_010 fe -- capa de nota de entrada
        JOIN PEDI_080 n -- natureza de operação
          ON n.NATUR_OPERACAO = fe.NATOPER_NAT_OPER
         AND n.ESTADO_NATOPER = fe.NATOPER_EST_OPER
        LEFT JOIN PEDI_010 c -- cliente
          ON c.CGC_9 = fe.CGC_CLI_FOR_9
         AND c.CGC_4 = fe.CGC_CLI_FOR_4
        --WHERE fe.DOCUMENTO = 208240
        JOIN ESTQ_005 tre -- transações de estoque
          ON tre.CODIGO_TRANSACAO = fe.CODIGO_TRANSACAO
        WHERE 1=1
          AND fe.LOCAL_ENTREGA = {empresa}
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
    else:
        sql += """
            ORDER BY
              fe.DOCUMENTO
        """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def get_tabela_preco(cursor, col, mes, seq):
    sql = f"""
        SELECT
          t.*
        FROM pedi_090 t
        WHERE 1=1
          AND t.NIVEL_ESTRUTURA = 1
          AND t.COL_TABELA_PRECO = {col}
          AND t.MES_TABELA_PRECO = {mes}
          AND t.SEQ_TABELA_PRECO = {seq}
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def itens_tabela_preco(cursor, col, mes, seq):
    sql = f"""
        SELECT
          ti.*
        FROM pedi_095 ti
        WHERE ti.TAB_COL_TAB = {col}
          AND ti.TAB_MES_TAB = {mes}
          AND ti.TAB_SEQ_TAB = {seq}
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
