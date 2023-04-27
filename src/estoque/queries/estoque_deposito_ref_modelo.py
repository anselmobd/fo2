from pprint import pprint

from systextil.queries.produto.modelo import (
    sql_modeloint_ref,
    sql_modelostr_ref,
    sql_sele_modeloint_ref,
)
from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute


__all__ = ['estoque_deposito_ref_modelo']


def estoque_deposito_ref_modelo(cursor, deposito, ref=None, modelo=None):
    if ref == '-':
        ref = None

    filtro_ref = f"AND rtc.GRUPO_ESTRUTURA = '{ref}'" if ref else ''

    filtro_prod = "AND rtc.GRUPO_ESTRUTURA < 'C0000'" if not ref else ''

    pprint(modelo)
    if modelo and modelo != "-":
        if '-' in modelo:
            modelos = modelo.split('-')
            filtro_modelo = f"""--
                AND {sql_modeloint_ref('rtc.GRUPO_ESTRUTURA')} >= TO_NUMBER('{modelos[0]}')
                AND {sql_modeloint_ref('rtc.GRUPO_ESTRUTURA')} <= TO_NUMBER('{modelos[1]}')
            """
        else:
            filtro_modelo = f"""--
                AND {sql_modelostr_ref('rtc.GRUPO_ESTRUTURA')} = '{modelo}'
            """
    else:
        filtro_modelo = ''

    sql = f'''
        SELECT
          i.MODELO
        , i.REF
        , i.COR
        , ta.ORDEM_TAMANHO
        , i.TAM
        , i.DEP
        , COALESCE(e.QTDE_ESTOQUE_ATU, 0) QTD
        FROM (
          SELECT
            {sql_sele_modeloint_ref('rtc.GRUPO_ESTRUTURA')}
          , rtc.GRUPO_ESTRUTURA REF
          , rtc.SUBGRU_ESTRUTURA TAM
          , rtc.ITEM_ESTRUTURA COR
          , d.CODIGO_DEPOSITO DEP
          FROM BASI_010 rtc
          JOIN BASI_205 d
            ON 1=1
          JOIN BASI_020 rt
            ON rt.BASI030_NIVEL030 = rtc.NIVEL_ESTRUTURA
           AND rt.BASI030_REFERENC = rtc.GRUPO_ESTRUTURA 
           AND rt.TAMANHO_REF = rtc.SUBGRU_ESTRUTURA 
           AND rt.DESCR_TAM_REFER NOT LIKE '-%'
          JOIN BASI_030 r
            ON r.NIVEL_ESTRUTURA = rtc.NIVEL_ESTRUTURA
           AND r.REFERENCIA = rtc.GRUPO_ESTRUTURA 
           AND r.DESCR_REFERENCIA NOT LIKE '-%'
          WHERE 1=1
            AND rtc.NIVEL_ESTRUTURA = 1
            AND rtc.ITEM_ATIVO = 0
            AND rtc.DATA_DESATIVACAO IS NULL
            AND rtc.DESCRICAO_15 NOT LIKE '-%'
            AND d.CODIGO_DEPOSITO = '{deposito}'
            -- AND rtc.GRUPO_ESTRUTURA < 'C0000'
            {filtro_prod} -- filtro_prod
            -- filtra códigos mal construídos
            -- AND REGEXP_LIKE (
            --       rtc.GRUPO_ESTRUTURA
            --     , '^0?[abAB]?([0-9]+)[a-zA-Z]*$'
            --     )
            {filtro_ref} -- filtro_ref
            {filtro_modelo} -- filtro_modelo
        ) i
        LEFT JOIN BASI_220 ta
          ON ta.TAMANHO_REF = i.TAM
        LEFT JOIN ESTQ_040 e
          ON e.LOTE_ACOMP = 0
         AND e.CDITEM_NIVEL99 = 1
         AND e.CDITEM_GRUPO = i.REF
         AND e.CDITEM_SUBGRUPO = i.TAM
         AND e.CDITEM_ITEM = i.COR
         AND e.DEPOSITO = i.DEP
        ORDER BY
          i.MODELO
        , NLSSORT(i.REF,'NLS_SORT=BINARY_AI')
        , i.COR
        , ta.ORDEM_TAMANHO
    '''

    debug_cursor_execute(cursor, sql)
    return dictlist_lower(cursor)
