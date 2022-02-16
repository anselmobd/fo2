from pprint import pprint

from django.shortcuts import render

from fo2.connections import db_cursor_so

from systextil.queries.tabela import estagio


def view(request):
    cursor = db_cursor_so(request)
    data = estagio.query(cursor)
    context = {
        'titulo': 'Estágios',
        'headers': ('Estágio', 'Descrição', 'Lead time', 'Depósito'),
        'fields': ('est', 'descr', 'lt', 'dep'),
        'data': data,
    }
    return render(request, 'systextil/tabela.html', context)
