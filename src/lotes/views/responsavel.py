import re
from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.views import View
from django.http import JsonResponse

from fo2.models import rows_to_dict_list

from geral.functions import has_permission

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

    pode_editar = False
    editar = False
    if has_permission(request, 'lotes.can_edit_estagio_direito'):
        pode_editar = True

    if todos == 'e':
        if pode_editar:
            editar = True
            pode_editar = False
        else:
            todos = 'a'

    context = {
        'titulo': title_name,
        'pode_editar': pode_editar,
        'editar': editar,
    }

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
                        'headers': ('Usuário Systêxtil ( matrícula )',
                                    'Estágio',
                                    'Baixa Lote', 'Estorna Lote',
                                    'Cria OS', 'Cancela OS'),
                        'fields': ('USUARIO', 'ESTAGIO',
                                   'BL', 'EL', 'CO', 'AO'),
                        'data': data,
                    })
    else:
        form = ResponsPorEstagioForm()
    context['form'] = form
    return render(request, 'lotes/respons.html', context)


def altera_direito_estagio(request, id):
    cursor = connections['so'].cursor()
    data = {
        'id': id,
    }
    erro = False
    ids = id.split('_')
    pprint(ids)

    data_r = models.responsavel(
        cursor, 't', 'e', ids[0], '', ids[1])
    pprint(data_r)
    if len(data_r) == 0:
        erro = True

    if not erro:
        row = data_r[0]
        state = row[ids[2]]

    if erro:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Erro ao alterar direito',
        })
        return JsonResponse(data, safe=False)

    data.update({
        'result': 'OK',
        'state': state,
    })
    return JsonResponse(data, safe=False)
