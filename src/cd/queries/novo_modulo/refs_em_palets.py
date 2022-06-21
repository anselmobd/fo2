from pprint import pprint

from utils.functions.models.dictlist import dictlist_lower
from utils.functions.queries import debug_cursor_execute

from lotes.functions.varias import (
    lote_de_periodo_oc,
    modelo_de_ref,
)


def query(
    cursor,
    fields='ref',
    ref=None,
    colecao=None,
    modelo=None,
    sele_lotes='63',
):
    """
    sele_lotes
        63 = todos os lotes endereçados e com quantidade no estágio 63
        n63 = todos os lotes endereçados e com quantidade não no estágio 63
        qq = todos os lotes endereçados e com quantidade em qq estágio
    """
    joins = set()

    if ref:
        if not isinstance(ref, (tuple, list)):
            ref = (ref, )
        ref_virgulas = ', '.join([f"'{r}'" for r in ref])
        filtra_ref = f"""--
            AND l.PROCONF_GRUPO in ({ref_virgulas})
        """
    else:
        filtra_ref = ''

    filtra_colecao = ''
    if colecao:
        filtra_colecao = f"""
            AND r.COLECAO = '{colecao}'
        """
        joins.add('r')

    if sele_lotes == '63':
        filtra_lote = """--
            AND l.CODIGO_ESTAGIO = 63
            AND l.QTDE_DISPONIVEL_BAIXA > 0
        """
    elif sele_lotes == 'n63':
        filtra_lote = """--
            AND l.CODIGO_ESTAGIO <> 63
            AND l.QTDE_DISPONIVEL_BAIXA > 0
        """
    elif sele_lotes == 'qq':
        filtra_lote = """--
            AND l.QTDE_DISPONIVEL_BAIXA > 0
        """
    else:
        filtra_lote = """--
            AND l.SEQUENCIA_ESTAGIO = 1
        """

    fields_tuple = {
        'ref': ('ref', ),
        'inv': (
            'ref',
            'ordem_tam',
            'tam',
            'op',
            'oc',
            'per',
            'cor',
            'qtd',
        ),
        'emp': (
            'ref',
            'ordem_tam',
            'tam',
            'op',
            'qtd_emp qtd',
            'oc',
            'per',
            'cor',
        ),
        'sol': (
            'ref',
            'ordem_tam',
            'tam',
            'op',
            'qtd_sol qtd',
            'oc',
            'per',
            'cor',
        ),
        'all': (
            'ref',
            'ordem_tam',
            'tam',
            'op',
            'oc',
            'per',
            'cor',
            'qtd',
            'qtd_emp',
            'qtd_sol',
        ),
        'detalhe': (
            'ref',
            'ordem_tam',
            'tam',
            'op',
            'oc',
            'per',
            'estagio',
            'cor',
            'qtd_prog',
            'qtd',
            'est_sol',
            'solicitacoes',
            'qtd_emp',
            'qtd_sol',
            'palete',
            'endereco',
            'rota',
        ),
    }
    if not isinstance(fields, (tuple, list)):
        fields = fields_tuple[fields]

    field_statement = {
        'ref': "l.PROCONF_GRUPO",
        'ordem_tam': "COALESCE(tam.ORDEM_TAMANHO, 0)",
        'tam': "l.PROCONF_SUBGRUPO",
        'op': "l.ORDEM_PRODUCAO",
        'qtd_prog': "l.QTDE_PECAS_PROG",
        'qtd_dbaixa': "l.QTDE_DISPONIVEL_BAIXA",
        'oc': "l.ORDEM_CONFECCAO",
        'per': "l.PERIODO_PRODUCAO",
        'estagio': "COALESCE(l.CODIGO_ESTAGIO, 999)",
        'cor': "l.PROCONF_ITEM",
        'qtd': "l.QTDE_DISPONIVEL_BAIXA",
        'palete': """--
            CASE
              WHEN lp.COD_CONTAINER IS NOT NULL
               AND lp.COD_CONTAINER <> '0'
              THEN lp.COD_CONTAINER
              ELSE '-'
            END
        """,
        'rota': "COALESCE(e.ROTA, '-')",
        'endereco': "COALESCE(ec.COD_ENDERECO, '-')",
        'qtd_prog': "l.QTDE_PECAS_PROG",
        'est_sol': """
            ( SELECT
                MOD(
                  ( SELECT 
                      MAX(
                        CASE WHEN l2.CODIGO_ESTAGIO = 63 THEN 163
                        ELSE l2.CODIGO_ESTAGIO
                        END
                      )
                    FROM pcpc_040 l2
                    WHERE 1=1
                      AND l2.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                      AND l2.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO
                      AND l2.QTDE_DISPONIVEL_BAIXA > 0
                  )
                , 100
                )
              FROM dual
            )
        """,
        'solicitacoes': """--
            COALESCE(
                ( SELECT
                    LISTAGG(DISTINCT COALESCE(TO_CHAR(sl.SOLICITACAO), '#'), ', ')
                    WITHIN GROUP (ORDER BY sl.SOLICITACAO) colicitacoes
                FROM pcpc_044 sl -- solicitação / lote 
                WHERE 1=1
                    AND sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                    AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO 
                    AND sl.ORDEM_CONFECCAO <> 0 
                    AND sl.GRUPO_DESTINO <> '0'
                    AND sl.SITUACAO IN (1, 2, 3, 4)
                ),
            '-'
            )
        """,
        'qtd_emp': """--
            COALESCE(
                ( SELECT
                    SUM(sl.QTDE) qtd_emp
                  FROM pcpc_044 sl -- solicitação / lote 
                  WHERE 1=1
                    AND sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                    AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO 
                    AND sl.ORDEM_CONFECCAO <> 0 
                    AND sl.GRUPO_DESTINO <> '0'
                    AND sl.SITUACAO IN (1, 2, 3, 4)
                    AND sl.SOLICITACAO IS NULL
                ),
                0
            )
        """,
        'qtd_sol': """--
            COALESCE(
                ( SELECT
                    SUM(sl.QTDE) qtd_sol
                  FROM pcpc_044 sl -- solicitação / lote 
                  WHERE 1=1
                    AND sl.ORDEM_PRODUCAO = l.ORDEM_PRODUCAO
                    AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO 
                    AND sl.ORDEM_CONFECCAO <> 0 
                    AND sl.GRUPO_DESTINO <> '0'
                    AND sl.SITUACAO IN (1, 2, 3, 4)
                    AND sl.SOLICITACAO IS NOT NULL
                ),
                0
            )
        """,
    }

    field_join = {
        'ordem_tam': "tam",
    }

    fields_statements_list = []
    for field in fields:
        if ' ' in field:
            fields_cod, field_alias = field.split()
        else:
            fields_cod = field_alias = field

        fields_statements_list.append(
            f"{field_statement[fields_cod]} {field_alias}"
        )

        if fields_cod in field_join:
            joins.add(field_join[fields_cod])

    fields_statements = "\n, ".join(fields_statements_list)

    join_statement = {
        'r': """--
            JOIN BASI_030 r -- referencia
              ON r.NIVEL_ESTRUTURA = 1
             AND r.REFERENCIA = l.PROCONF_GRUPO 
        """,
        'tam': """--
            LEFT JOIN BASI_220 tam -- cadastro de tamanhos
              ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO 
        """,
    }

    joins_statements = "\n".join(
        [
            join_statement[join]
            for join in joins
        ]
    )

    sql = f"""
        SELECT DISTINCT
          {fields_statements} -- fields_statements
        FROM ENDR_014 lp
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO 
         AND l.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000)
        LEFT JOIN ENDR_015 ec -- endereço/container 
          ON ec.COD_CONTAINER = lp.COD_CONTAINER
        LEFT JOIN ENDR_013 e -- endereço
          ON e.COD_ENDERECO = ec.COD_ENDERECO
        {joins_statements} -- joins_statements
        WHERE 1=1
          {filtra_lote} -- filtra_lote
          {filtra_colecao} -- filtra_colecao
          {filtra_ref} -- filtra_ref
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist_lower(cursor)

    for row in dados:
        row['modelo'] = modelo_de_ref(row['ref'])
        if {'per', 'oc'}.issubset(fields):
            row['lote'] = lote_de_periodo_oc(row['per'], row['oc'])

    if modelo:
        return [
            row
            for row in dados        
            if row['modelo'] == modelo
        ]
    else:
        return dados
