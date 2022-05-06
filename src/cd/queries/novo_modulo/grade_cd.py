from pprint import pprint

from utils.functions.models import GradeQtd

from cd.queries.novo_modulo.lotes import sql_em_estoque


def grade_estoque(cursor, tipo=None, ref=None):
    grade = GradeQtd(cursor, case='lower')

    if tipo in ['i', 's', 'p']:
        sql_base = sql_em_estoque(tipo=tipo, ref=ref, get='lote_qtd')
    if tipo == 'sp':
        sql_base_s = sql_em_estoque(tipo='s', ref=ref, get='lote_qtd')
        sql_base_p = sql_em_estoque(tipo='p', ref=ref, get='lote_qtd')
        sql_base = f"""--
            (
                {sql_base_s}
                UNION
                {sql_base_p}
            )
        """
    if tipo == 'i-sp':
        sql_base_i = sql_em_estoque(tipo='i', ref=ref, get='lote_qtd')
        sql_base_s = sql_em_estoque(tipo='s', ref=ref, sinal="-", get='lote_qtd')
        sql_base_p = sql_em_estoque(tipo='p', ref=ref, sinal="-", get='lote_qtd')
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
