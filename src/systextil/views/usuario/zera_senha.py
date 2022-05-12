from pprint import pprint

from django.shortcuts import render

from fo2.connections import db_cursor_so



def view(request):
    cursor = db_cursor_so(request)
    context = {
        'titulo': 'Zera senha',
    }
    return render(request, 'systextil/usuario/zera_senha.html', context)
