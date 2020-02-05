from django.views import View
from django.shortcuts import (
    redirect,
    render,
    )

import email_signature.models as models


def index(request):
    return render(request, 'email_signature/index.html')


def show_template(request):
    try:
        template = models.Layout.objects.filter(
            habilitado=True).first().template
    except Exception:
        return redirect('apoio_ao_erp')

    context = {
        'nome': 'Nome do funcionário',
        'setor': 'Setor',
        'email': 'funcionario@cuecasduomo.com.br',
        'num_1': '(21) 99999-1111',
        'num_2': '(21) 99999-2222',
    }
    return render(request, f'email_signature/{template}.html', context)
