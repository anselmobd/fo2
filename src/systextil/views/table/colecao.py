from pprint import pprint

from django.shortcuts import render

from fo2.connections import db_cursor_so

from utils.functions.format import format_cnpj

from systextil.queries.tabela.colecao import query_colecao


def view(request):
    cursor = db_cursor_so(request)
    data = query_colecao(cursor)
    context = {
        'titulo': 'Coleções',
        'headers': ('Código', 'Descrição'),
        'fields': ('colecao', 'descr_colecao'),
        'data': data,
    }
    return render(request, 'systextil/tabela.html', context)

