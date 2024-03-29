import datetime
from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


def receita_inform(cursor, receita):
    sql = f"""
        WITH referencias AS
        ( SELECT
            sr.*
          FROM basi_030 sr
          WHERE sr.NIVEL_ESTRUTURA = 5
            AND sr.REFERENCIA = '{receita}'
        )
        SELECT
          r.REFERENCIA REF
        , r.DESCR_REFERENCIA DESCR
        FROM referencias r
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)


def receita_subgrupo(cursor, receita):
    sql = f"""
        SELECT DISTINCT
          t.TAMANHO_REF SUBGRUPO
        , t.DESCR_TAM_REFER DESCR
        FROM basi_020 t
        WHERE t.BASI030_NIVEL030 = 5
          AND t.BASI030_REFERENC = '{receita}'
        ORDER BY
          t.TAMANHO_REF
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)


def receita_cores(cursor, receita):
    sql = f"""
        SELECT 
          c.SUBGRU_ESTRUTURA SUBGRUPO
        , c.ITEM_ESTRUTURA COR
        , c.DESCRICAO_15 DESCR
        FROM basi_010 c
        WHERE c.NIVEL_ESTRUTURA = 5
          AND c.GRUPO_ESTRUTURA = '{receita}'
        ORDER BY
          c.SUBGRU_ESTRUTURA
        , c.ITEM_ESTRUTURA
    """
    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)


def receita_estrutura(cursor, niv, grup, sub, item):
    sql = f"""
        SELECT
          re.SEQUENCIA seq
        , re.NIVEL_COMP niv
        , re.GRUPO_COMP grup
        , re.SUB_COMP sub
        , re.ITEM_COMP item
        , item.NARRATIVA descr
        , re.ALTERNATIVA_COMP alt
        , re.CONS_UN_REC consumo_unidade
        , re.TIPO_CALCULO tipo_calc
        , calc.DESCRICAO calc_descr
        , re.CONSUMO consumo
        , COALESCE(re.LETRA_GRAFICO, '.') letra
        FROM BASI_050 re
        JOIN BASI_420 calc
          ON calc.CODIGO = re.TIPO_CALCULO
        JOIN BASI_010 item
          ON item.NIVEL_ESTRUTURA = re.NIVEL_COMP
         AND item.GRUPO_ESTRUTURA = re.GRUPO_COMP
         AND item.SUBGRU_ESTRUTURA = re.SUB_COMP
         AND item.ITEM_ESTRUTURA = re.ITEM_COMP
        WHERE re.NIVEL_ITEM = {niv}
          AND re.GRUPO_ITEM = '{grup}'
          AND re.SUB_ITEM = '{sub}'
          AND re.ITEM_ITEM = '{item}'
        ORDER BY 
          re.SEQUENCIA
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)
    for row in dados:
        row['comp'] = '.'.join([
            row['niv'],
            row['grup'],
            row['sub'],
            row['item'],
        ])
        row['calculo'] = ':'.join([
            str(row['tipo_calc']),
            row['calc_descr'],
        ])
    return dados
