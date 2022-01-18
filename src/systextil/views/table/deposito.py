from pprint import pprint

from django.shortcuts import render

from fo2.connections import db_cursor_so

from utils.functions.format import format_cnpj

from systextil.queries.tabela.deposito import query_deposito


def deposito(request):
    cursor = db_cursor_so(request)
    data = query_deposito(cursor)
    propriedades = {
        1: 'Próprio',
        2: 'Em terceiros',
        3: 'De terceiros',
    }
    for row in data:
        if row['FORN'] == ' ':
            row['CNPJ'] = ''
        else:
            row['CNPJ'] = \
                f"{format_cnpj(row)} - {row['FORN']}"
        if row['PROP'] in propriedades:
            row['PROP'] = '{} - {}'.format(
                row['PROP'], propriedades[row['PROP']])
    context = {
        'titulo': 'Depósitos',
        'headers': ('Depósito', 'Descrição', 'Propriedade', 'Terceiro'),
        'fields': ('COD', 'DESCR', 'PROP', 'CNPJ'),
        'data': data,
    }
    return render(request, 'systextil/tabela.html', context)

