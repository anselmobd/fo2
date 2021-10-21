from pprint import pprint

from django.views import View
from django.shortcuts import (
    redirect,
    render,
    )

import email_signature.models as models


def index(request):
    return render(request, 'email_signature/index.html')


def get_template(tipo):
    try:
        return models.Layout.objects.filter(
            habilitado=True,
            tipo=tipo,
        ).first().template
    except Exception:
        return


def get_template_file(tipo):
    template = get_template(tipo)
    if template is not None:
        return f'email_signature/{template}.html'


def show_template(request, tipo=None):
    template_file = get_template_file(tipo)
    if template_file is None:
        return redirect('intranet')

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
