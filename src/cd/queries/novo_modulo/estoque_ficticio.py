from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute
from utils.functions.strings import only_digits


def condicao_valor(ref):
    if len(ref.split()) == 2:
        condicao = ref.split()[0]
        ref = str(ref.split()[1])
    else:
        condicao = '='
    return condicao, ref


def query(
    cursor,
    ref=None,
    tam=None,
    cor=None,
    com_ordem_tam = False,
):

    filter_ref = ''
    ref_conds = []
    ref_in = []
    if isinstance(ref, str):
        ref = map(
            str.strip,
            ref.split(','),
        )
    if ref is not None:  # iterable
        for r in ref:
            condicao, valor = condicao_valor(r)
            if condicao == '=':
                ref_in.append(valor)
            else:
                ref_conds.append(f"l.PROCONF_GRUPO {condicao} '{valor}'")
    if ref_in:
        refs = ', '.join([f"'{r}'" for r in ref_in])
        ref_conds.append(f"l.PROCONF_GRUPO in ({refs})")
    if ref_conds:
        filters_ref = " AND ".join(ref_conds)
        filter_ref = f"AND {filters_ref}"

    filter_tam = f"AND l.PROCONF_SUBGRUPO = '{tam}'" if tam else ''

    filter_cor = f"AND l.PROCONF_ITEM = '{cor}'" if cor else ''

    join_ordem_tam = ''
    field_ordem_tam = ''
    if com_ordem_tam:
        field_ordem_tam = ", COALESCE(tam.ORDEM_TAMANHO, 0) ordem_tam"
        join_ordem_tam = """--
            LEFT JOIN BASI_220 tam -- cadastro de tamanhos
              ON tam.TAMANHO_REF = l.TAM 
        """

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
          JOIN PCPC_020 op
            ON op.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
          WHERE 1=1
            AND op.COD_CANCELAMENTO = 0
            AND (
              l.CODIGO_ESTAGIO = 60
              OR l.CODIGO_ESTAGIO = 57
              OR l.CODIGO_ESTAGIO = 63
            )
            AND NOT ( l.QTDE_DISPONIVEL_BAIXA = 0 )
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
        {field_ordem_tam} -- field_ordem_tam
        FROM lotes_605763end l
        {join_ordem_tam} -- join_ordem_tam
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

    return dados
