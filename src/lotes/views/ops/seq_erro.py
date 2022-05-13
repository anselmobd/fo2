from pprint import pprint

from django.shortcuts import render

from fo2.connections import db_cursor_so

from lotes.queries.op import seq_erro


def view(request):
    cursor = db_cursor_so(request)
    data = seq_erro.lista_op(cursor)

    context = {
        'titulo': 'OP com erro de sequência',
        'headers': ['OP', 'Referência', 'Alternativa', 'Roteiro'],
        'fields': ['op', 'ref', 'alt', 'rot'],
        'data': data,
    }
    return render(request, 'lotes/op_seq_erro.html', context)
