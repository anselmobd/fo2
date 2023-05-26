import operator
import re
from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.sql import sql_test_in

from cd.classes.endereco import EnderecoCd
from cd.functions.endereco import calc_rota


def query_endereco(cursor, tipo='TO'):
    where_tipo = []
    if tipo == 'IE':
        where_tipo = [
            f"REGEXP_LIKE(e.COD_ENDERECO, '^1[ABCDEFGH][0123456789]{{4}}$')",
        ]
    elif tipo == 'IQ':
        where_tipo = [
            f"REGEXP_LIKE(e.COD_ENDERECO, '^1Q[0123456789]{{4}}$')",
        ]
    elif tipo == 'IL':
        where_tipo = [
            f"REGEXP_LIKE(e.COD_ENDERECO, '^1L[0123456789]{{4}}$')",
        ]
    elif tipo == 'LO':
        where_tipo = [
            "e.COD_ENDERECO LIKE '2%'",
             f"REGEXP_LIKE(e.COD_ENDERECO, '^2[XY][0123456789]{{4}}$')",
        ]
    elif tipo == 'IN':
        where_tipo = [
            "e.COD_ENDERECO LIKE '1%'",
            f"NOT REGEXP_LIKE(e.COD_ENDERECO, '^1[ABCDEFGHLQ][0123456789]{{4}}$')",
        ]
    elif tipo == 'IT':
        where_tipo = [
            "e.COD_ENDERECO LIKE '1%'",
        ]
    elif tipo == 'EL':
        where_tipo = [
            f"REGEXP_LIKE(e.COD_ENDERECO, '^2S[0123456789]{{4}}$')",
        ]
    elif tipo == 'EN':
        where_tipo = [
            "e.COD_ENDERECO LIKE '2%'",
            f"NOT REGEXP_LIKE(e.COD_ENDERECO, '^2S[0123456789]{{4}}$')",
        ]
    elif tipo == 'ET':
        where_tipo = [
            "e.COD_ENDERECO LIKE '2%'",
        ]
    elif tipo != 'TO':
        where_tipo = [
            f"REGEXP_LIKE(e.COD_ENDERECO, '^1{tipo}[0123456789]{{4}}$')",
        ]
    field_list=[
        "e.COD_ENDERECO end",
        "e.ROTA",
        "ec.COD_CONTAINER palete",
    ]
    order_list=[
        f"e.COD_ENDERECO",
    ]
    where = "\n  AND ".join(where_tipo) if where_tipo else ""
    qwhere = " ".join(["WHERE", where]) if where else "-- where"

    fields = "\n, ".join(field_list)
    order = "\n, ".join(order_list) if order_list else ""

    sql = f"""
        select
          {fields}
        from ENDR_013 e -- endereço
        left join ENDR_015 ec -- endereço/container
          on ec.COD_ENDERECO = e.COD_ENDERECO
        {qwhere}
        order by {order}
    """
   
    debug_cursor_execute(cursor, sql)
    data = dictlist_lower(cursor)
    
    data = data_details_from_end(data, 'end')

    return data


def data_details_from_end(data, end_field):
    ecd = EnderecoCd()
    for row in data:
        if not row['palete']:
            row['palete'] = '-'
        ecd.endereco = row[end_field]
        row.update(ecd.details_dict)

    data.sort(key=operator.itemgetter('prioridade', 'bloco', 'order_ap'))

    return data


def add_endereco(cursor, endereco):
    """Cria endereco no banco de dados
    Recebe: cursor e endereco a ser criado
    Retorna: Se sucesso, None, senão, mensagem de erro
    """
    rota = calc_rota(endereco)
    sql = f"""
        INSERT INTO SYSTEXTIL.ENDR_013
        (RUA, BOX, ALTURA, COD_ENDERECO, EMPRESA, PROCESSO, SITUACAO, TIPO_ENDERECO, ROTA)
        VALUES(NULL, NULL, NULL, '{endereco}', 1, 1, '1', '1', '{rota}')
    """
    try:
        debug_cursor_execute(cursor, sql)
    except Exception as e:
        return repr(e)


def conteudo_local(
    cursor,
    local=None,
    bloco=None,
    item=False,
    qtd63=False,
    item_qtd63=False,
):
    """Lista lotes paletizados
    Retorna
        endereco
        palete
        op
        lote
        data de inclusão
    Filtros
        local (opcional): pode ser tanto um endereço quando um palete
        blobo (opcional): início de endereço
    Parâmetros
        item (default False): Adiciona retorno de:
            referência
            tamanho
            cor
            ordem_tam
            item (calculado 'ref.tam.cor')
        qtd63 (default False): Adiciona retorno de:
            qtd (quantidade do lote no estágio 63)
        item_qtd63 (default False): item e qtd63
    """

    if item_qtd63:
        item = True
        qtd63 = True

    retorna_item = """--
        , l.PROCONF_GRUPO ref
        , l.PROCONF_SUBGRUPO tam
        , l.PROCONF_ITEM cor
        , t.ORDEM_TAMANHO ordem_tam
    """ if item else ''

    retorna_qtd = """--
        , coalesce(l63.QTDE_A_PRODUZIR_PACOTE, 0) qtd
    """ if qtd63 else ''

    join_dict = {
        'l' : """--
            LEFT JOIN PCPC_040 l
              ON l.PERIODO_PRODUCAO = TRUNC(lp.ORDEM_CONFECCAO / 100000)
             AND l.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000)
             AND l.SEQUENCIA_ESTAGIO = 1
            LEFT JOIN BASI_220 t -- tamanhos
              ON t.TAMANHO_REF = l.PROCONF_SUBGRUPO
        """,
        'l63' : """--
            LEFT JOIN PCPC_040 l63
              ON l63.PERIODO_PRODUCAO = TRUNC(lp.ORDEM_CONFECCAO / 100000)
             AND l63.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000)
             AND l63.CODIGO_ESTAGIO = 63
        """,
    }

    join_set = set()
    if item:
        join_set.add('l')
    if qtd63:
        join_set.add('l63')

    joins = "\n".join([
        join_stm
        for join_key, join_stm in join_dict.items()
        if join_key in join_set
    ])

    filtra_local = f"""--
        AND ( ec.COD_ENDERECO = '{local}'
            OR UPPER(lp.COD_CONTAINER)  = '{local}'
            )
    """ if local else ''

    filtra_bloco = ""
    if bloco:
        if bloco == '0-':
            filtra_bloco = f"""--
                AND ec.COD_ENDERECO IS NULL
            """
        else:
            filtra_bloco = f"""--
                AND ec.COD_ENDERECO LIKE '{bloco}%'
            """

    sql = f"""
        SELECT
          ec.COD_ENDERECO endereco
        , UPPER(lp.COD_CONTAINER) palete
        , lp.ORDEM_PRODUCAO op
        , lp.ORDEM_CONFECCAO lote
        , lp.DATA_INCLUSAO data
        {retorna_item} -- retorna_item
        {retorna_qtd} -- retorna_qtd
        FROM ENDR_014 lp -- lote/palete - oc/container
        LEFT JOIN ENDR_015 ec -- endereço/container
          ON UPPER(ec.COD_CONTAINER) = UPPER(lp.COD_CONTAINER)
        {joins} -- joins
        WHERE 1=1
          {filtra_local} -- filtra_local
          {filtra_bloco} -- filtra_bloco
        ORDER BY
          lp.DATA_INCLUSAO DESC
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    if item:
        for row in dados:
            row['item'] = (
                f"{row['ref']}.{row['tam']}.{row['cor']}"
                if row['ref'] else '-'
            )

    return dados


def lotes_em_versao_palete(cursor, palete, data_versao):
    sql = f"""
        SELECT
          lph.ORDEM_PRODUCAO op
        , lph.ORDEM_CONFECCAO lote
        , lph.DATA_INCLUSAO data
        FROM ENDR_014_HIST_DUOMO lph -- esvaziamento de palete - lote/palete - oc/container
        WHERE lph.COD_CONTAINER = '{palete}'
          AND lph.DATA_VERSAO = '{data_versao}'
        ORDER BY
          lph.DATA_INCLUSAO DESC
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)


def lotes_em_palete(cursor, palete):
    sql = f"""
        SELECT
          ec.COD_ENDERECO endereco
        , lp.COD_CONTAINER palete
        , lp.ORDEM_PRODUCAO op
        , lp.ORDEM_CONFECCAO lote
        FROM ENDR_014 lp -- lote/palete - oc/container
        LEFT JOIN ENDR_015 ec -- endereço/container
          ON ec.COD_CONTAINER = lp.COD_CONTAINER 
        WHERE 1=1
          AND lp.COD_CONTAINER = '{palete}'
        ORDER BY
          lp.ORDEM_PRODUCAO
        , lp.ORDEM_CONFECCAO
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)


def add_lote_in_endereco(cursor, endereco, op, lote):
    sql = f"""
        INSERT INTO SYSTEXTIL.ENDR_014
        (COD_CONTAINER, ORDEM_PRODUCAO, ORDEM_CONFECCAO, DATA_INCLUSAO, NIVEL, GRUPO, SUB, ITEM, QUANTIDADE)
        VALUES('{endereco}', {op}, '{lote}', CURRENT_TIMESTAMP, NULL, NULL, NULL, NULL, 0)
    """
    try:
        debug_cursor_execute(cursor, sql)
        return True
    except Exception as e:
        return False


def local_de_lote(cursor, lote):
    sql = f"""
        SELECT
          ec.COD_ENDERECO endereco 
        , lp.COD_CONTAINER palete
        FROM ENDR_014 lp -- lote/palete - oc/container
        LEFT JOIN ENDR_015 ec -- endereço/container
          ON ec.COD_CONTAINER = lp.COD_CONTAINER 
        WHERE lp.ORDEM_CONFECCAO = {lote}
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)


def esvazia_palete(cursor, palete):
    sql = f"""
        DELETE FROM ENDR_014 lp -- lote/palete - oc/container
        WHERE lp.COD_CONTAINER  = '{palete}'
    """
    try:
        debug_cursor_execute(cursor, sql)
        return True
    except Exception as e:
        return False

def palete_guarda_hist(cursor, palete, usuario):
    sql = f"""
        INSERT INTO ENDR_014_HIST_DUOMO (
          COD_CONTAINER
        , ORDEM_PRODUCAO
        , ORDEM_CONFECCAO
        , DATA_INCLUSAO
        , NIVEL
        , GRUPO
        , SUB
        , ITEM
        , QUANTIDADE
        , USUARIO_SYSTEXTIL
        )
        SELECT
          COD_CONTAINER
        , ORDEM_PRODUCAO
        , ORDEM_CONFECCAO
        , DATA_INCLUSAO
        , NIVEL
        , GRUPO
        , SUB
        , ITEM
        , QUANTIDADE
        , '{usuario}'
        FROM ENDR_014 -- lote/palete - oc/container
        WHERE COD_CONTAINER = '{palete}'
    """
    try:
        debug_cursor_execute(cursor, sql)
        return True
    except Exception as e:
        return False

def get_palete(cursor, palete):
    palete_filter = sql_test_in("p.COD_CONTAINER", palete, ligacao_condicional='WHERE')
    sql = f"""
        SELECT
          p.COD_CONTAINER
        , p.COD_TIPO
        , p.ENDERECO
        , p.TARA_CONTAINER
        , p.QUANTIDADE_MAXIMO
        , p.ULTIMA_ATUALIZACAO_TARA
        , p.SITUACAO
        , p.TUSSOR_IMPRESSA
        FROM ENDR_012 p -- container palete
        {palete_filter} -- palete_filter
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)


def get_endereco(cursor, endereco):
    sql = f"""
        SELECT
          e.RUA
        , e.BOX
        , e.ALTURA
        , e.COD_ENDERECO
        , e.EMPRESA
        , e.PROCESSO
        , e.SITUACAO
        , e.TIPO_ENDERECO
        , e.ROTA
        FROM ENDR_013 e
        WHERE e.COD_ENDERECO = '{endereco}'
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)


def get_esvaziamentos_de_palete(cursor, palete):
    sql = f"""
        SELECT DISTINCT
          h.DATA_VERSAO dh
        FROM ENDR_014_HIST_DUOMO h
        WHERE h.COD_CONTAINER = '{palete}'
        ORDER BY 
          h.DATA_VERSAO DESC
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
