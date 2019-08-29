import re

from django.shortcuts import render
from django.db import connections
from django.views import View

from fo2.models import rows_to_dict_list

from lotes.forms import ResponsPorEstagioForm
import lotes.models as models


def responsEdit(request):
    return responsCustom(request, 'e')


def responsTodos(request):
    return responsCustom(request, 't')


def respons(request):
    return responsCustom(request, 'a')


def responsCustom(request, todos):
    title_name = 'Responsável por estágio'
    context = {'titulo': title_name}
    if todos in ['t', 'e']:
        context.update({'todos': True})
    if request.method == 'POST':
        form = ResponsPorEstagioForm(request.POST)
        if form.is_valid():
            estagio = form.cleaned_data['estagio']
            usuario = '%'+form.cleaned_data['usuario']+'%'
            usuario_num = re.sub("\D", "", form.cleaned_data['usuario'])
            ordem = form.cleaned_data['ordem']
            cursor = connections['so'].cursor()
            data = models.responsavel(
                cursor, todos, ordem, estagio, usuario, usuario_num)
            if len(data) != 0:
                if ordem == 'e':
                    context.update({
                        'headers': ('Estágio',
                                    'Usuário Systêxtil ( matrícula )',
                                    'Baixa Lote', 'Estorna Lote',
                                    'Cria OS', 'Cancela OS'),
                        'fields': ('ESTAGIO', 'USUARIO',
                                   'BL', 'EL', 'CO', 'AO'),
                        'data': data,
                    })
                else:
                    context.update({
                        'headers': ('Usuário', 'Estágio'),
                        'fields': ('USUARIO', 'ESTAGIO'),
                        'data': data,
                    })
    else:
        form = ResponsPorEstagioForm()
    context['form'] = form
    return render(request, 'lotes/respons.html', context)
