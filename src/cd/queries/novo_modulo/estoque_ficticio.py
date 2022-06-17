from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import only_digits


def query(
    cursor,
    modelo=None,
    ref=None,
    tam=None,
    cor=None,
):
    filter_modelo = f"AND l.REF LIKE '%{modelo}%'" if modelo else ''

    filter_ref = f"AND l.PROCONF_GRUPO = '{ref}'" if ref else ''

    filter_tam = f"AND l.PROCONF_SUBGRUPO = '{tam}'" if tam else ''

    filter_cor = f"AND l.PROCONF_ITEM = '{cor}'" if cor else ''

    sql = f"""
        WITH lotes_605763 AS
        ( SELECT DISTINCT
            l.ORDEM_PRODUCAO OP
          , l.PERIODO_PRODUCAO PER
          , l.ORDEM_CONFECCAO OC
          , l.CODIGO_ESTAGIO EST
          , l.QTDE_PROGRAMADA QTD_LOTE
          , l.PROCONF_GRUPO REF
          , l.PROCONF_SUBGRUPO TAM
          , l.PROCONF_ITEM COR
          FROM PCPC_040 l 
          WHERE 1=1
            AND l.QTDE_DISPONIVEL_BAIXA > 0
            AND (
              l.CODIGO_ESTAGIO = 60
              OR l.CODIGO_ESTAGIO = 57
              OR l.CODIGO_ESTAGIO = 63
            )
            {filter_ref} -- filter_ref
            {filter_tam} -- filter_tam
            {filter_cor} -- filter_cor
        )
        , lotes_605763end AS 
        ( SELECT DISTINCT 
            l.OP
          , l.PER
          , l.OC
          , l.QTD_LOTE
          , COALESCE(lp.COD_CONTAINER, '-') PALETE
          , l.REF
          , l.TAM
          , l.COR
          FROM lotes_605763 l
          LEFT JOIN ENDR_014 lp
            ON lp.ORDEM_PRODUCAO = l.OP
          AND lp.ORDEM_CONFECCAO = l.PER * 100000 + l.OC
          WHERE 1=1
            {filter_modelo} -- filter_modelo
            AND (
              l.EST <> 63
              OR lp.ORDEM_PRODUCAO IS NOT NULL
            )
        )
        SELECT 
          l.OP
        , l.PER
        , l.OC
        , l.PER * 100000 + l.OC LOTE
        , l.QTD_LOTE
        , l.PALETE
        , l.REF
        , l.TAM
        , l.COR
        , COALESCE(ec.COD_ENDERECO, '-') ENDERECO
        , COALESCE(
            ( SELECT
                LISTAGG(DISTINCT COALESCE(TO_CHAR(sl.SOLICITACAO), '#'), ', ')
                WITHIN GROUP (ORDER BY sl.SOLICITACAO) colicitacoes
              FROM pcpc_044 sl -- solicitação / lote 
              WHERE 1=1
                AND sl.ORDEM_PRODUCAO = l.OP
                AND sl.ORDEM_CONFECCAO = l.OC
            ),
          '-'
          ) SOLICITACOES
        , COALESCE(
            ( SELECT
                SUM(sl.QTDE) qtd_sol
              FROM pcpc_044 sl -- solicitação / lote 
              WHERE 1=1
                AND sl.ORDEM_PRODUCAO = l.OP
                AND sl.ORDEM_CONFECCAO = l.OC
            ),
          0
          ) QTD_EMP
        FROM lotes_605763end l
        LEFT JOIN ENDR_015 ec -- endereço/container 
          ON ec.COD_CONTAINER = l.PALETE
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    for row in dados:
        try:
            ref_modelo = int(only_digits(row['ref']))
        except ValueError:
            ref_modelo = 0
        row['modelo'] = ref_modelo

    if modelo:
        dados = [
            row
            for row in dados
            if row['modelo'] == modelo
        ]

    return dados
