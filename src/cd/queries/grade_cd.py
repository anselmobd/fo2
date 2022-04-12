from pprint import pprint

from utils.functions.models import (
    dictlist,
    GradeQtd,
)
from utils.functions.queries import debug_cursor_execute


def sql_em_estoque(tipo=None, ref=None, get=None, sinal='+'):
    """Monta SQL base de lotes em produção final
    (por ora, apenas endereçados)
    Recebe:
      tipo
        i = inventário; todos os lotes
        p = lotes de OPs de Pedidos
      ref
        None = grade total (da solicitação)
        string = filtra uma referência
        list = lista de referências
    """

    if ref is None:
        filter_ref = ''
    elif isinstance(ref, str):
        filter_ref = f"and l.PROCONF_GRUPO = '{ref}'"
    else:
        refs = ', '.join([f"'{r}'" for r in ref])
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
            , l.QTDE_DISPONIVEL_BAIXA qtd_dbaixa
        """

    if tipo == 'p':
        field_qtd = f"""--
            , {sinal}l.QTDE_DISPONIVEL_BAIXA qtd
        """
        tipo_join = """--
            JOIN PCPC_020 op
              ON op.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO
        """
        tipo_filter = """--
              AND op.PEDIDO_VENDA <> 0
              AND l.QTDE_DISPONIVEL_BAIXA > 0
        """
    elif tipo == 's':
        field_qtd = f"""--
            , {sinal}sl.QTDE qtd
        """
        tipo_join = """--
            JOIN PCPC_044 sl
              ON sl.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO
             AND sl.ORDEM_CONFECCAO = l.ORDEM_CONFECCAO 
        """
        tipo_filter = """--
              AND sl.SITUACAO IN (2, 3, 4)
        """
    elif tipo == 'i':
        field_qtd = f"""--
            , {sinal}l.QTDE_DISPONIVEL_BAIXA qtd
        """
        tipo_join = ""
        tipo_filter = """--
              AND l.QTDE_DISPONIVEL_BAIXA > 0
        """
    else:
        field_qtd = ""
        tipo_join = ""
        tipo_filter = ""

    sql = f"""
        SELECT {"DISTINCT" if distinct else ""}
        {fields} -- fields
        {field_qtd} -- field_qtd
        FROM ENDR_014 lp
        JOIN PCPC_040 l
          ON l.ORDEM_PRODUCAO = lp.ORDEM_PRODUCAO 
         AND l.ORDEM_CONFECCAO = MOD(lp.ORDEM_CONFECCAO, 100000)
        {tipo_join} -- tipo_join
        LEFT JOIN BASI_220 tam -- cadastro de tamanhos
          ON tam.TAMANHO_REF = l.PROCONF_SUBGRUPO
        WHERE l.CODIGO_ESTAGIO = 63
          {tipo_filter} -- tipo_filter
          {filter_ref} -- filter_ref
    """
    return sql

def lotes_em_estoque(cursor, get='ref'):
    sql = sql_em_estoque(get=get)
    debug_cursor_execute(cursor, sql)
    return dictlist(cursor)


def grade_estoque(cursor, tipo=None, ref=None):
    grade = GradeQtd(cursor, case='lower')

    if tipo in 'isp':
        sql_base = sql_em_estoque(tipo=tipo, ref=ref)
    if tipo == 'sp':
        sql_base_s = sql_em_estoque(tipo='s', ref=ref)
        sql_base_p = sql_em_estoque(tipo='p', ref=ref)
        sql_base = f"""--
            (
                {sql_base_s}
                UNION
                {sql_base_p}
            )
        """
    if tipo == 'i-sp':
        sql_base_i = sql_em_estoque(tipo='i', ref=ref)
        sql_base_s = sql_em_estoque(tipo='s', ref=ref, sinal="-")
        sql_base_p = sql_em_estoque(tipo='p', ref=ref, sinal="-")
        sql_base = f"""--
            (
                {sql_base_i}
                UNION
                {sql_base_s}
                UNION
                {sql_base_p}
            )
        """

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
        SELECT
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
