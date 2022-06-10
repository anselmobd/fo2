from pprint import pprint

from utils.functions.models import dictlist
from utils.functions.queries import debug_cursor_execute

from lotes.functions.varias import modelo_de_ref


def query(
    cursor,
    ref=None,
    colecao=None,
    modelo=None,
    com_qtd_63=True,
):
    joins = set()

    filtra_ref = f"""--
        AND l.PROCONF_GRUPO = '{ref}'
    """ if ref else ''

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

    join_statement = {
        'r': """--
            JOIN BASI_030 r
              ON r.NIVEL_ESTRUTURA = 1
             AND r.REFERENCIA = l.PROCONF_GRUPO 
        """
    }

    joins_statements = "\n".join(
        [
            join_statement[join]
            for join in joins
        ]
    )

    sql = f"""
        SELECT DISTINCT
          l.PROCONF_GRUPO ref
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
