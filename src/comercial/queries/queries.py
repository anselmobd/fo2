from datetime import datetime, date, timedelta
# from firebird.base import DatabaseWrapper
from pprint import pprint

from django.db import connections
from django.core.cache import cache

from utils.functions.models import rows_to_dict_list, rows_to_dict_list_lower
from utils.functions import dec_months, my_make_key_cache, fo2logger


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
        modelo=None, order_qtd=True, ultimos_dias=None, zerados=True):

    # key_cache = make_key_cache()
    key_cache = my_make_key_cache(
        'get_vendas', ref, periodo, colecao, cliente, por, modelo, order_qtd,
        ultimos_dias, zerados)

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
    """
    if zerados:
        sql += f"""
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
        """
    sql += f"""
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


def get_vendas_new(
        cursor, ref=None, periodo=None, colecao=None, cliente=None, por=None,
        modelo=None, order_qtd=True, ultimos_dias=None, refs_incl=None, mult_incl=None):
    """
    ref e modelo e refs_incl são tratados em conjunto com OR
    """
    # key_cache = make_key_cache()
    key_cache = my_make_key_cache(
        'get_vendas', ref, periodo, colecao, cliente, por, modelo, order_qtd,
        ultimos_dias, refs_incl)

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
    filtra_col_select_item = '1=2'
    if colecao is not None:
        ref = None
        filtra_col = f"AND v.COL = '{colecao}'"
        filtra_col_select_item = f"r.COLECAO = '{colecao}'"

    filtra_cliente = ''
    filtra_cliente_select_item = '1=2'
    if cliente is not None:
        filtra_cliente = f"AND v.CNPJ9 = '{cliente}'"
        filtra_cliente_select_item = f"r.CGC_CLIENTE_9 = '{cliente}'"

    if (
        modelo is None and
        refs_incl is None and
        ref is None
    ):
        or_filtro = '1=1'
    else:
        or_filtro = '1=2'

    if (
        modelo is None and
        refs_incl is None and
        ref is None and
        colecao is None and
        cliente is None
    ):
        or_filtro_select_item = '1=1'
    else:
        or_filtro_select_item = '1=2'

    filtra_modelo = '1=2'
    pre_filtra_modelo = '1=2'
    filtra_modelo_select_item = '1=2'
    if modelo is not None:
        filtra_modelo = "v.MODELO = '{}'".format(modelo)
        pre_filtra_modelo = \
            "inf.GRUPO_ESTRUTURA LIKE '%{}%'".format(modelo)
        filtra_modelo_select_item = f""" --
            TRIM(
              LEADING '0' FROM (
                REGEXP_REPLACE(
                  v.GRUPO_ESTRUTURA
                , '^([^a-zA-Z]+)[a-zA-Z]*$'
                , '\\1'
                )
              )
            ) = '{modelo}'
        """

    filtra_refs_incl = '1=2'
    pre_filtra_refs_incl = '1=2'
    filtra_refs_incl_select_item = '1=2'
    multiplicador = ''
    if refs_incl is not None:
        if isinstance(refs_incl, tuple):
            filtra_refs_incl = ""
            pre_filtra_refs_incl = ""
            filtra_refs_incl_select_item = ""
            refs_incl_sep = ""
            for idx, ref_incl in enumerate(refs_incl):
                if mult_incl is not None:
                    multiplicador += (
                        f" WHEN inf.GRUPO_ESTRUTURA = '{ref_incl}' THEN {mult_incl[idx]} ")
                filtra_refs_incl += (
                    refs_incl_sep + f"v.REF = '{ref_incl}'")
                pre_filtra_refs_incl += (
                    refs_incl_sep + f"inf.GRUPO_ESTRUTURA = '{ref_incl}'")
                filtra_refs_incl_select_item += (
                    refs_incl_sep + f"v.GRUPO_ESTRUTURA = '{ref_incl}'")
                refs_incl_sep = " OR "
        else:
            filtra_refs_incl = f"v.REF = '{refs_incl}'"
            pre_filtra_refs_incl = \
                f"inf.GRUPO_ESTRUTURA = '{refs_incl}'"
            filtra_refs_incl_select_item = f"v.GRUPO_ESTRUTURA = '{refs_incl}'"

    filtra_ref = '1=2'
    pre_filtra_ref = '1=2'
    filtra_ref_select_item = '1=2'
    if ref is not None:
        filtra_ref = f"v.REF = '{ref}'"
        pre_filtra_ref = f"inf.GRUPO_ESTRUTURA = '{ref}'"
        filtra_ref_select_item = f"v.GRUPO_ESTRUTURA = '{ref}'"

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
        select_item = (
        """--
            , TRIM(LEADING '0' FROM
               (REGEXP_REPLACE(v.GRUPO_ESTRUTURA,
                               '^([^a-zA-Z]+)[a-zA-Z]*$', '\\1'
                               ))) MODELO
        """)
        select_global = select_por
        join_on = "ON pr.MODELO = v.MODELO"
        group_por = ", v.MODELO"
        add_order('v.MODELO')
    elif por == 'modelo+incl':
        select_por = f", '{modelo}' MODELO"
        select_item = (
        """--
            , TRIM(LEADING '0' FROM
               (REGEXP_REPLACE(v.GRUPO_ESTRUTURA,
                               '^([^a-zA-Z]+)[a-zA-Z]*$', '\\1'
                               ))) MODELO
        """)
        select_global = select_por
        join_on = "ON pr.MODELO = v.MODELO"
    elif por == 'ref':
        select_por = ", v.REF"
        select_item = ", v.GRUPO_ESTRUTURA REF"
        select_global = select_por
        join_on = "ON pr.REF = v.REF"
        group_por = ", v.REF"
        add_order('v.REF')
    elif por == 'cor':
        select_por = ", v.COR"
        select_item = ", v.ITEM_ESTRUTURA COR"
        select_global = select_por
        join_on = "ON pr.COR = v.COR"
        group_por = ", v.COR"
        add_order('v.COR')
    elif por == 'tam':
        select_por = ", t.ORDEM_TAMANHO\n, v.TAM"
        select_item = ", t.ORDEM_TAMANHO\n, v.SUBGRU_ESTRUTURA TAM"
        select_global = ", v.ORDEM_TAMANHO\n, v.TAM"
        join_on = "ON pr.TAM = v.TAM"
        group_por = ", v.ORDEM_TAMANHO\n, v.TAM"
        add_order("v.ORDEM_TAMANHO\n, v.TAM")

    sql = f"""
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
        , CASE
            WHEN 1=2 THEN 0
            {multiplicador} -- multiplicador
            ELSE 1
          END * inf.QTDE_ITEM_FATUR QTD
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
        LEFT JOIN BASI_030 r -- ref
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
          AND (
            {or_filtro} -- or_filtro
            OR
            {pre_filtra_modelo} -- pre_filtra_modelo
            OR
            {pre_filtra_refs_incl} -- pre_filtra_refs_incl
            OR
            {pre_filtra_ref} -- pre_filtra_ref
          )
          {pre_filtra_periodo} -- pre_filtra_periodo
          {pre_filtra_ultimos_dias} -- pre_filtra_ultimos_dias
        ),
        por_ref AS
        (
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
          AND (
            {or_filtro} -- or_filtro
            OR
            {filtra_modelo} -- filtra_modelo
            OR
            {filtra_refs_incl} -- filtra_refs_incl
            OR
            {filtra_ref} -- filtra_ref
          )
          {filtra_ultimos_dias} -- filtra_ultimos_dias
        ),
        all_ref AS 
        (
        SELECT DISTINCT
          0 qtd
          {select_item} -- select_item
        FROM BASI_010 v -- item (ref+tam+cor)
        JOIN BASI_030 r -- ref
          on r.NIVEL_ESTRUTURA = v.NIVEL_ESTRUTURA
         AND r.REFERENCIA = v.GRUPO_ESTRUTURA
        LEFT JOIN BASI_220 t
          ON t.TAMANHO_REF = v.SUBGRU_ESTRUTURA
        WHERE v.NIVEL_ESTRUTURA = 1
          AND v.GRUPO_ESTRUTURA < 'A0000'
          AND (
            NOT ( v.GRUPO_ESTRUTURA >= '0A000'
                AND v.GRUPO_ESTRUTURA <= '0Z999'
                )
              )  
          AND (
            {or_filtro_select_item} -- or_filtro_select_item
            OR
            {filtra_modelo_select_item} -- filtra_modelo_select_item
            OR
            {filtra_refs_incl_select_item} -- filtra_refs_incl_select_item
            OR
            {filtra_ref_select_item} -- filtra_ref_select_item
            OR
            {filtra_col_select_item} -- filtra_col_select_item
            OR
            {filtra_cliente_select_item} -- filtra_cliente_select_item
          )
        )
        SELECT
          coalesce(sum(pr.qtd), 0) qtd
          {select_global} -- select_global
        FROM all_ref v
        LEFT JOIN por_ref pr
          -- ON pr.REF = v.ref
          {join_on} -- join_on
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


def devolucao_para_meta(cursor, ano, mes=None, tipo='total', empresa=1, ref=None):
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
        --WHERE fe.DOCUMENTO = 208240
        JOIN ESTQ_005 tre -- transações de estoque
          ON tre.CODIGO_TRANSACAO = fe.CODIGO_TRANSACAO
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
    return rows_to_dict_list_lower(cursor)


def get_tabela_preco(cursor, col=None, mes=None, seq=None):
    filtra_col = ''
    if col is not None:
        filtra_col = f"AND t.COL_TABELA_PRECO = '{col}'"
    filtra_mes = ''
    if mes is not None:
        filtra_mes = f"AND t.MES_TABELA_PRECO = '{mes}'"
    filtra_seq = ''
    if seq is not None:
        filtra_seq = f"AND t.SEQ_TABELA_PRECO = '{seq}'"
    sql = f"""
        SELECT
          t.*
        FROM pedi_090 t
        WHERE 1=1
          AND t.NIVEL_ESTRUTURA = 1
          {filtra_col} -- filtra_col
          {filtra_mes} -- filtra_mes
          {filtra_seq} -- filtra_seq
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)


def itens_tabela_preco(cursor, col, mes, seq):
    sql = f"""
        SELECT
          r.DESCR_REFERENCIA
        , ti.*
        FROM pedi_095 ti
        JOIN basi_030 r
          ON r.NIVEL_ESTRUTURA = ti.NIVEL_ESTRUTURA
         AND r.REFERENCIA = ti.GRUPO_ESTRUTURA
        WHERE ti.TAB_COL_TAB = {col}
          AND ti.TAB_MES_TAB = {mes}
          AND ti.TAB_SEQ_TAB = {seq}
    """
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
