import re
from pprint import pprint

from django.shortcuts import render

from fo2.connections import db_cursor_so

from geral.functions import has_permission

from lotes.forms import ResponsPorEstagioForm
import lotes.queries as queries


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
            cursor = db_cursor_so(request)
            data = queries.responsavel(
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
