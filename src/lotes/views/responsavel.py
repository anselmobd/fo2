import re
from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.views import View
from django.http import JsonResponse

from utils.functions.models import rows_to_dict_list

from geral.functions import has_permission

from lotes.forms import ResponsPorEstagioForm
import lotes.models as models


def respons_edit(request):
    return respons_custom(request, 'e')


def respons_todos(request):
    return respons_custom(request, 't')


def respons(request):
    return respons_custom(request, 'a')


def respons_custom(request, todos):
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
    estagio = ids[0]
    usuario = ids[1]
    coluna = ids[2]

    data_r = models.responsavel(
        cursor, 't', 'e', estagio, '', usuario)
    if len(data_r) == 0:
        row = {
            'CO': ' ',
            'AO': ' ',
            'BL': ' ',
            'EL': ' ',
        }
    else:
        row = data_r[0]

    state = row[coluna]
    acao = []

    if coluna == 'CO':
        if state == 'X':
            acao.append(['exclui', 3])
        else:
            acao.append(['inclui', 3])

    elif coluna == 'AO':
        if state == 'X':
            acao.append(['exclui', 4])
        else:
            acao.append(['inclui', 4])

    elif coluna == 'BL':
        if state == 'X':
            acao.append(['exclui', 1])
            acao.append(['exclui', 2])
            acao.append(['altera', 0, 2])
        else:
            if row['EL'] == 'X':
                acao.append(['altera', 2, 0])
            else:
                acao.append(['inclui', 1])

    elif coluna == 'EL':
        if state == 'X':
            acao.append(['exclui', 2])
            acao.append(['exclui', 1])
            acao.append(['altera', 0, 1])
        else:
            if row['BL'] == 'X':
                acao.append(['altera', 1, 0])
            else:
                acao.append(['inclui', 2])

    result = True
    for passo in acao:
        if result:
            tipo_acao = passo[0]
            if tipo_acao == 'inclui':
                tipo_movimento = passo[1]
                result = result and models.responsavel_inclui_direitos(
                    cursor, estagio, usuario, tipo_movimento)

            elif tipo_acao == 'exclui':
                tipo_movimento = passo[1]
                result = result and models.responsavel_exclui_direitos(
                    cursor, estagio, usuario, tipo_movimento)

            elif tipo_acao == 'altera':
                tipo_movimento_de = passo[1]
                tipo_movimento_para = passo[2]
                result = result and models.responsavel_altera_direitos(
                    cursor, estagio, usuario,
                    tipo_movimento_de, tipo_movimento_para)
    erro = not result

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
