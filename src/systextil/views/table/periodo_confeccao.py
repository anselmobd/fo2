from pprint import pprint

from django.shortcuts import render

from fo2.connections import db_cursor_so

from systextil.queries.tabela import periodo_confeccao


def view(request):
    cursor = db_cursor_so(request)
    data = periodo_confeccao.query(cursor)

    context = {
        'titulo': 'Períodos de confecção',
        'headers': ['Período', 'Data de início', 'Data de fim'],
        'fields': ['periodo', 'ini', 'fim'],
        'data': data,
    }
    return render(request, 'systextil/tabela.html', context)
