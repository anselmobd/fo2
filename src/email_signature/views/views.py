from pprint import pprint

from django.shortcuts import render

import email_signature.functions as functions


def index(request):
    return render(request, 'email_signature/index.html')


def show_template(request, tipo):
    template_file = functions.gets.get_template_file(tipo)

    context = {
        'nome': 'Nome do funcionário',
        'setor': 'Setor',
        'email': 'funcionario@cuecasduomo.com.br',
        'ddd_1': 21,
        'num_1': '99999-1111',
        'ddd_2': 21,
        'num_2': '99999-2222',
    }
    return render(request, template_file, context)
