from pprint import pprint

from utils.functions.models import (
    dictlist,
    GradeQtd,
)
from utils.functions.queries import debug_cursor_execute


def sql_em_estoque(ref=None, get=None):

    if ref is None:
        filter_ref = ''
    elif isinstance(ref, str):
        filter_ref = f"and l.PROCONF_GRUPO = '{ref}'"
    else:
        refs = ', '.join(ref)
        filter_ref = f"and l.PROCONF_GRUPO in ({refs})"

    if get == 'ref':
        distinct = True
        fields = """--
              l.PROCONF_GRUPO ref
        """
    else:
        distinct = False
        fields = """--
              l.PERIODO_PRODUCAO per
            , l.ORDEM_CONFECCAO oc
            , l.PROCONF_GRUPO ref
            , l.PROCONF_SUBGRUPO tam
            , tam.ORDEM_TAMANHO ordem_tam
            , l.PROCONF_ITEM cor
            , l.ORDEM_PRODUCAO op
            , l.QTDE_PECAS_PROG qtd_prog
            , l.QTDE_DISPONIVEL_BAIXA qtd
        """

    sql = f"""
        SELECT {"DISTINCT" if distinct else ""}
        {fields} -- fields
        FROM ENDR_014 lp
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO 
         AND l.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000)
        LEFT JOIN BASI_220 tam -- cadastro de tamanhos
          ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE l.CODIGO_ESTAGIO = 63
          AND l.QTDE_DISPONIVEL_BAIXA > 0
          {filter_ref} -- filter_ref
    """
    return sql

def lotes_em_estoque(cursor, get='ref'):
    sql = sql_em_estoque(get=get)
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def grade_estoque(cursor, ref=None):

    # Grade de solicitação
    grade = GradeQtd(cursor, case='lower')

    sql_base = sql_em_estoque(ref=ref)

    sql = f"""
        WITH base as
        ({sql_base})    
        SELECT distinct
          b.tam tamanho
        , b.ordem_tam ordem_tamanho
        from base b
        order by
          b.ordem_tam
    """
    grade.col(
        id='tamanho',
        name='Tamanho',
        total='Total',
        sql=sql,
    )

    sql = f"""
        WITH base as
        ({sql_base})    
        SELECT distinct
          b.cor
        from base b
        order by
          b.cor
    """
    grade.row(
        id='cor',
        name='Cor',
        name_plural='Cores',
        total='Total',
        sql=sql,
    )

    sql = f"""
        WITH base as
        ({sql_base})    
        SELECT distinct
          b.tam tamanho
        , b.cor
        , sum(b.qtd) qtd
        from base b
        group by
          b.tam
        , b.cor
        order by
          b.tam
        , b.cor
    """
    grade.value(
        id='qtd',
        sql=sql,
    )

    fields = grade.table_data['fields']
    data = grade.table_data['data']
    style = grade.table_data['style']

    data_complementar = None
    total_complementar = 0

    context_ref = {
        'referencia': ref,
        'headers': grade.table_data['header'],
        'fields': fields,
        'data': data,
        'style': style,
        'total': grade.total,
        'data_complementar': data_complementar,
        'total_complementar': total_complementar,
    }

    return context_ref
