from pprint import pprint

from django.shortcuts import render

from fo2.connections import db_cursor_so

from systextil.queries.tabela import unidade


def view(request):
    cursor = db_cursor_so(request)
    data = unidade. query(cursor)
    context = {
        'titulo': 'Unidades / Divisões',
        'headers': ('Código ', 'Descrição', 'UF', 'Cidade',
                    '(CNPJ) Razão social'),
        'fields': ('div', 'descr', 'uf', 'cidade',
                   'nome'),
        'data': data,
    }
    return render(request, 'systextil/tabela.html', context)
