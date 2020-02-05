from django.views import View
from django.shortcuts import (
    redirect,
    render,
    )

import email_signature.models as models


def index(request):
    return render(request, 'email_signature/index.html')


def get_template():
    try:
        return models.Layout.objects.filter(
            habilitado=True).first().template
    except Exception:
        pass


def get_template_file():
    template = get_template()
    if template is not None:
        return f'email_signature/{template}.html'


def show_template(request):
    template_file = get_template_file()
    if template_file is None:
        return redirect('apoio_ao_erp')

    context = {
        'nome': 'Nome do funcionário',
        'setor': 'Setor',
        'email': 'funcionario@cuecasduomo.com.br',
        'num_1': '(21) 99999-1111',
        'num_2': '(21) 99999-2222',
    }
    return render(request, template_file, context)
