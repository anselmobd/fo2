from pprint import pprint

import django.forms
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse

import geral.forms as forms
from geral.functions import (
    get_empresa,
)
from geral.models import (
    Pop,
    PopAssunto,
    UsuarioPopAssunto,
)
from utils.views import group_rowspan


def pop(request, pop_assunto=None, id=None):
    assunto = PopAssunto.objects.get(slug=pop_assunto)
    prefixo = (
        assunto.grupo_assunto.nome
        if assunto.grupo_assunto.nome
        else 'POPs'
    )    
    context = {'titulo': f"{prefixo}: {assunto.nome}"}

    can_edit = False
    user = None
    if request.user.is_authenticated:
        user = request.user
    if user:
        can_edit = user.has_perm('geral.can_manage_pop')
        if can_edit:
            verificacao = UsuarioPopAssunto.objects.filter(
                usuario=request.user, assunto=assunto)
            can_edit = len(verificacao) != 0

    if can_edit:
        if id:
            instance = get_object_or_404(Pop, id=id)
            context.update({'edit': True})
        else:
            instance = None
            context.update({'insert': True})
        if request.method == 'POST':
            form = forms.PopForm(
                request.POST, request.FILES, instance=instance)
            if form.is_valid():
                form.save()
                return redirect('geral:pop', pop_assunto)
        else:
            if instance is None:
                form = forms.PopForm()
                form.fields['assunto'].initial = assunto.id
            else:
                form = forms.PopForm(instance=instance)
        form.fields['assunto'].widget = django.forms.HiddenInput()
        context.update({'form': form})

    if can_edit:
        select = Pop.objects.filter(assunto__slug=pop_assunto)
        select = select.order_by('-uploaded_at')
    else:
        select = Pop.objects.filter(assunto__slug=pop_assunto, habilitado=True)
        select = select.order_by('topico', 'descricao')
    select = select.values()
    data = list(select)
    for row in data:
        row['descricao|LINK'] = '/media/{}'.format(row['pop'])
        row['descricao|TARGET'] = '_blank'
        row['habilitado'] = 'sim' if row['habilitado'] else 'não'
        row['edit'] = ''
        row['edit|LINK'] = reverse('geral:pop', args=[pop_assunto, row['id']])
    context.update({
        'data': data,
    })
    if can_edit:
        context.update({
            'headers': ('Adicionado em', 'Tópico', 'Título', 'Arquivo POP',
                        'Habilitado', 'Editar'),
            'fields': ('uploaded_at', 'topico', 'descricao', 'pop',
                       'habilitado', 'edit'),
        })
    else:
        group = ['topico']
        group_rowspan(data, group)
        context.update({
            'headers': ['Tópico', 'Título'],
            'fields': ['topico', 'descricao'],
            'group': group,
        })
    if get_empresa(request) == 'agator':
        context.update({
            'extends_html': 'geral/index_agator.html',
        })
    else:
        context.update({
            'extends_html': 'geral/index.html'
        })
    return render(request, 'geral/pop.html', context)
