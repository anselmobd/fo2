from pprint import pprint

from django.shortcuts import render

from fo2.connections import db_cursor_so

from utils.views import totalize_data

from systextil.queries.tabela.colecao import query_colecao


def view(request):
    cursor = db_cursor_so(request)
    data = query_colecao(cursor)

    totalize_data(
        data,
        {
            'sum': [
                'produto',
                'pa',
                'pg',
                'pb',
                'mp',
                'md',
                'desmonte',
                'insumo',
                'total',
            ],
            'descr': {'descr_colecao': 'Totais:'},
            'row_style': 'font-weight: bold;',
        }
    )

    context = {
        'titulo': 'Coleções',
        'headers': (
            'Código',
            'Descrição',
            'Produto',
            'PA',
            'PG',
            'PB',
            'MP',
            'MD',
            'Desmonte',
            'Insumo',
            'Total',
        ),
        'fields': (
            'colecao',
            'descr_colecao',
            'produto',
            'pa',
            'pg',
            'pb',
            'mp',
            'md',
            'desmonte',
            'insumo',
            'total',
        ),
        'style': {
            3: 'text-align: right;',
            4: 'text-align: right;',
            5: 'text-align: right;',
            6: 'text-align: right;',
            7: 'text-align: right;',
            8: 'text-align: right;',
            9: 'text-align: right;',
            10: 'text-align: right;',
            11: 'text-align: right;',
        },
        'data': data,
    }
    return render(request, 'systextil/tabela.html', context)

