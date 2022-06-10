from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute

from lotes.functions.varias import modelo_de_ref


def query(
    cursor,
    fields='ref',
    ref=None,
    colecao=None,
    modelo=None,
    com_qtd_63=True,
):
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
        filter_colecao = f"""
            AND r.COLECAO = '{colecao}'
        """
        joins.add('r')

    filtra_lote = """--
        AND l.CODIGO_ESTAGIO = 63
        AND l.QTDE_DISPONIVEL_BAIXA > 0
    """ if com_qtd_63 else """--
        AND l.SEQUENCIA_ESTAGIO = 1
    """

    fields_tuple = {
        'ref': ('ref', ),
        'inv': (
            'ref',
            'ordem_tam',
            'tam',
            'op',
            'qtd_prog',
            'qtd_dbaixa',
            'oc',
            'per',
            'cor',
            'qtd',
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
        'cor': "l.PROCONF_ITEM",
        'qtd': "l.QTDE_DISPONIVEL_BAIXA",
    }

    fields_statements = "\n".join(
        [
            f"{field_statement[field]} {field}"
            for field in fields_tuple
        ]
    )

    field_join = {
        'ordem_tam': "tam",
    }

    for field in fields_tuple:
        if field in field_join:
            joins.add(field_join[field])

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
        {joins_statements} -- joins_statements
        WHERE 1=1
          {filtra_ref} -- filtra_ref
          {filtra_colecao} -- filtra_colecao
          {filtra_lote} -- filtra_lote
    """
    debug_cursor_execute(cursor, sql)
    dados = dictlist(cursor)

    for row in dados:
        row['modelo'] = modelo_de_ref(row['ref'])

    if modelo:
        return [
            row
            for row in dados        
            if row['modelo'] == modelo
        ]
    else:
        return dados
