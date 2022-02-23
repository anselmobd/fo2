import re
from pprint import pprint

from utils.functions.models import rows_to_dict_list_lower


def insumos_cor_tamanho(
        cursor, qtd_itens='0', nivel=None, insumo=None):
    filtra_qtd_itens = ''
    if qtd_itens != '0':
        filtra_qtd_itens = 'WHERE rownum <= {qtd_itens}'.format(
            qtd_itens=qtd_itens)

    filtra_nivel = ''
    if nivel in ['2', '9']:
        filtra_nivel = "AND r.NIVEL_ESTRUTURA = '{nivel}'".format(nivel=nivel)

    filtra_insumo = ''
    if insumo:
        sep = ' AND '
        ref = ''
        nivel = ''

        so_ref = re.compile(r"^[A-Z0-9]{5}$")
        nivelref = re.compile(r"^\d[A-Z0-9]{5}$")
        nivel_ref = re.compile(r"^\d[\. -][A-Z0-9]{5}$")
        if so_ref.match(insumo):
            ref = insumo
        elif nivelref.match(insumo) or nivel_ref.match(insumo):
            ref = insumo[-5:]
            nivel = insumo[0]
        else:
            for parte in insumo.split():
                if parte:
                    filtra_insumo += sep + """
                        ( r.REFERENCIA LIKE '%{parte}%'
                        OR r.DESCR_REFERENCIA LIKE '%{parte}%')
                    """.format(parte=parte)
        if nivel:
            filtra_insumo += sep + """
                r.NIVEL_ESTRUTURA = '{nivel}'
            """.format(nivel=nivel)
        if ref:
            filtra_insumo += sep + """
                r.REFERENCIA = '{ref}'
            """.format(ref=ref)

    sql = """
        WITH insumos AS
        (
            SELECT DISTINCT
              r.NIVEL_ESTRUTURA NIVEL
            , r.REFERENCIA REF
            , r.DESCR_REFERENCIA DESCR
            , t.TAMANHO_REF TAM
            , t.DESCR_TAM_REFER DESCR_TAM
            , tam.ORDEM_TAMANHO ORDEM_TAM
            , c.ITEM_ESTRUTURA COR
            , c.DESCRICAO_15 DESCR_COR
            FROM BASI_030 r -- referencia
            JOIN BASI_020 t -- tamanho
              ON t.BASI030_NIVEL030 = r.NIVEL_ESTRUTURA
             AND t.BASI030_REFERENC = r.REFERENCIA
            LEFT JOIN BASI_220 tam -- cadastro de tamanhos
              ON tam.TAMANHO_REF = t.TAMANHO_REF
            JOIN BASI_010 c -- cor
              ON c.NIVEL_ESTRUTURA = r.NIVEL_ESTRUTURA
             AND c.GRUPO_ESTRUTURA = r.REFERENCIA
             AND c.SUBGRU_ESTRUTURA = t.TAMANHO_REF
            WHERE r.NIVEL_ESTRUTURA IN (2, 9)
              AND r.DESCR_REFERENCIA NOT LIKE '-%'
              AND t.DESCR_TAM_REFER  NOT LIKE '-%'
              AND c.DESCRICAO_15  NOT LIKE '-%'
              AND c.ITEM_ATIVO = 0 -- ativo
              {filtra_nivel} -- filtra_nivel
              {filtra_insumo} -- filtra_insumo
            ORDER BY
              r.NIVEL_ESTRUTURA
            , r.REFERENCIA
            , c.ITEM_ESTRUTURA
            , tam.ORDEM_TAMANHO
            , t.TAMANHO_REF
        )
        SELECT
          i.*
        FROM insumos i
        {filtra_qtd_itens} -- filtra_qtd_itens
    """.format(
        filtra_qtd_itens=filtra_qtd_itens,
        filtra_nivel=filtra_nivel,
        filtra_insumo=filtra_insumo)
    cursor.execute(sql)
    return rows_to_dict_list_lower(cursor)
