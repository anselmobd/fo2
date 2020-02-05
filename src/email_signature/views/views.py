from django.views import View
from django.shortcuts import render


def index(request):
    return render(request, 'email_signature/index.html')


def show_template(request):
    context = {
        'nome': 'Nome do funcionário',
        'setor': 'Setor',
        'email': 'funcionario@cuecasduomo.com.br',
        'num_1': '(21) 99999-1111',
        'num_2': '(21) 99999-2222',
    }
    return render(request, 'email_signature/assin-abvtex.html', context)
