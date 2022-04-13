from curses.ascii import isdigit
from pprint import pprint

from systextil.queries.base import SMountQuery

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute

from cd.classes.palete import Plt


def query_palete(impressa_SNA='A', order='D'):
    where_impressa = []
    if impressa_SNA != 'A':
        where_impressa = [
            f"COALESCE(co.TUSSOR_IMPRESSA, 'N') = '{impressa_SNA}'"
        ]

    if order[0].upper() == 'D':
        order = "DESC"
    else:
        order = "ASC"

    return SMountQuery(
        fields=[
          "co.COD_CONTAINER palete",
          "COALESCE(co.TUSSOR_IMPRESSA, 'N') impressa",
        ],
        table="ENDR_012 co",
        where=[
            "co.COD_CONTAINER LIKE 'P%'",
        ]+
        where_impressa,
        order=[
          f"co.COD_CONTAINER {order}",
        ],
    ).oquery.debug_execute()


def add_palete(cursor, quant=1):
    """Cria palete no banco de dados
    Recebe: cursor e quant de paletes a ser criados
    Retorna: Se sucesso, None, senão, mensagem de erro
    """
    paletes = query_palete()
    if len(paletes) == 0:
        palete = Plt().mount(1)
    else:
        palete = Plt(paletes[0]['palete']).next()

    if isinstance(quant, str):
        quant = int(quant)

    for _ in range(quant):
        sql = f"""
            INSERT INTO SYSTEXTIL.ENDR_012
            (COD_CONTAINER, COD_TIPO, ENDERECO, TARA_CONTAINER, QUANTIDADE_MAXIMO, ULTIMA_ATUALIZACAO_TARA, SITUACAO)
            VALUES('{palete}', 1, NULL, 1, 1, CURRENT_TIMESTAMP, '1')
        """
        try:
            debug_cursor_execute(cursor, sql)
        except Exception as e:
            return repr(e)
        palete = Plt(palete).next()


def mark_palete_printed(cursor, palete):
    """Marca palete como impresso no banco de dados
    Recebe: cursor e código do palete a ser marcado
    Retorna: Se sucesso, None, senão, mensagem de erro
    """
    sql = f"""
        UPDATE SYSTEXTIL.ENDR_012
        SET 
            TUSSOR_IMPRESSA = 'S'
        WHERE COD_CONTAINER = '{palete}'
    """
    try:
        debug_cursor_execute(cursor, sql)
    except Exception as e:
        return repr(e)


def get_paletes(cursor):
    sql = f"""
        SELECT
          p.COD_CONTAINER
        , p.COD_TIPO
        , p.ENDERECO
        , MIN(ec.COD_ENDERECO) ENDERECO_CONTAINER
        , COUNT(DISTINCT ec.COD_ENDERECO) enderecos
        , p.TARA_CONTAINER
        , p.QUANTIDADE_MAXIMO
        , p.ULTIMA_ATUALIZACAO_TARA
        , p.SITUACAO
        , p.TUSSOR_IMPRESSA
        , COUNT(lp.COD_CONTAINER) lotes
        FROM ENDR_012 p -- container palete
        LEFT JOIN ENDR_014 lp -- lote/palete - oc/container
          ON lp.COD_CONTAINER = p.COD_CONTAINER
        LEFT JOIN ENDR_015 ec -- endereço/container 
          ON ec.COD_CONTAINER = p.COD_CONTAINER
        --WHERE 1=1
        --  AND p.COD_CONTAINER = 'PLT0999I'
        GROUP BY 
          p.COD_CONTAINER
        , p.COD_TIPO
        , p.ENDERECO
        , p.TARA_CONTAINER
        , p.QUANTIDADE_MAXIMO
        , p.ULTIMA_ATUALIZACAO_TARA
        , p.SITUACAO
        , p.TUSSOR_IMPRESSA
        ORDER BY 
          p.COD_CONTAINER
    """
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)
