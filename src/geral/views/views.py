import datetime
import pytz
import yaml
from pprint import pformat, pprint

import django.forms
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template import loader
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.views import View

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.functions.models import rows_to_dict_list

import produto.queries

import geral.forms as forms
import geral.models as models
import geral.queries as queries
from geral.functions import config_get_value, config_set_value, get_empresa
from geral.models import (InformacaoModulo, Painel, PainelModulo, Pop, PopAssunto,
                     UsuarioPainelModulo, UsuarioPopAssunto)

from geral.dados.fluxo_roteiros import get_roteiros_de_fluxo
from geral.dados.fluxos import dict_fluxo


def index(request):
    if get_empresa(request) == 'agator':
        return render(request, 'geral/index_agator.html')
    else:
        return render(request, 'geral/index.html')


def deposito(request):
    cursor = db_cursor_so(request)
    data = queries.deposito(cursor)
    propriedades = {
        1: 'Próprio',
        2: 'Em terceiros',
        3: 'De terceiros',
    }
    for row in data:
        if row['FORN'] == ' ':
            row['CNPJ'] = ''
        else:
            row['CNPJ'] = \
                '{CNPJ9:09}/{CNPJ4:04}-{CNPJ2:02} - {FORN}'.format(**row)
        if row['PROP'] in propriedades:
            row['PROP'] = '{} - {}'.format(
                row['PROP'], propriedades[row['PROP']])
    context = {
        'titulo': 'Depósitos',
        'headers': ('Depósito', 'Descrição', 'Propriedade', 'Terceiro'),
        'fields': ('COD', 'DESCR', 'PROP', 'CNPJ'),
        'data': data,
    }
    return render(request, 'geral/tabela_geral.html', context)


def estagio(request):
    cursor = db_cursor_so(request)
    data = queries.estagios(cursor)
    context = {
        'titulo': 'Estágios',
        'headers': ('Estágio', 'Descrição', 'Lead time', 'Depósito'),
        'fields': ('EST', 'DESCR', 'LT', 'DEP'),
        'data': data,
    }
    return render(request, 'geral/tabela_geral.html', context)


def periodo_confeccao(request):
    cursor = db_cursor_so(request)
    sql = '''
        SELECT
          p.PERIODO_PRODUCAO PERIODO
        , p.DATA_INI_PERIODO INI
        , p.DATA_FIM_PERIODO FIM
        FROM PCPC_010 p
        WHERE p.AREA_PERIODO = 1 -- confecção
        ORDER BY
          p.PERIODO_PRODUCAO
    '''
    cursor.execute(sql)
    data = rows_to_dict_list(cursor)

    for row in data:
        row['INI'] = row['INI'].date()
        row['FIM'] = row['FIM'].date()

    context = {
        'titulo': 'Períodos de confecção',
        'headers': ('Período', 'Data de início', 'Data de fim'),
        'fields': ('PERIODO', 'INI', 'FIM'),
        'data': data,
    }
    return render(request, 'geral/tabela_geral.html', context)


class PainelView(View):

    def get(self, request, *args, **kwargs):
        cursor = db_cursor_so(request)
        painel = Painel.objects.filter(slug=kwargs['painel'], habilitado=True)
        if len(painel) == 0:
            return redirect('apoio_ao_erp')

        ultimo_mes = timezone.now() - datetime.timedelta(days=61)

        layout = painel[0].layout
        config = yaml.load(layout)
        for dado in config['dados']:
            try:
                modulo = PainelModulo.objects.get(slug=dado['modulo'])
            except Exception:
                return redirect('apoio_ao_erp')

            if modulo.tipo == 'I':
                dado['modulo_nome'] = modulo.nome
                dado['dados'] = InformacaoModulo.objects.filter(
                    painel_modulo__slug=dado['modulo'],
                    habilitado=True,
                    data__gt=ultimo_mes,
                ).order_by('-data')

        context = {
            'titulo': painel[0].nome,
            'config': config,
            }
        return render(
            request, 'geral/{}.html'.format(config['template']), context)


class InformativoView(LoginRequiredMixin, View):
    Form_class = forms.InformacaoModuloForm
    template_name = 'geral/informativo.html'
    title_name = 'Informativos'
    context = {}
    informativo_id = None

    def list_informativo(self):
        self.context['informativos'] = InformacaoModulo.objects.filter(
            painel_modulo=self.modulo).order_by('-data')

    def tem_permissao(self, request, **kwargs):
        modulo_slug = kwargs['modulo']
        self.modulo = PainelModulo.objects.get(slug=modulo_slug)
        self.context = {
            'titulo': '{} - {}'.format(self.modulo.nome, self.title_name),
            'modulo_slug': modulo_slug,
            }

        verificacao = UsuarioPainelModulo.objects.filter(
            usuario=request.user, painel_modulo=self.modulo)
        if len(verificacao) == 0:
            self.context['msg_erro'] =\
                'Usuário não tem direito de manter o informativo "{}"'.format(
                    self.modulo.nome
                )
            return False
        return True

    def get_informativo_id(self, **kwargs):
        if 'id' in kwargs:
            self.informativo_id = kwargs['id']

    def get(self, request, *args, **kwargs):
        if not self.tem_permissao(request, **kwargs):
            return render(request, self.template_name, self.context)

        self.get_informativo_id(**kwargs)
        if self.informativo_id == 'add':
            form = self.Form_class()
            self.context['form'] = form
        else:
            informativo_por_id = InformacaoModulo.objects.filter(
                id=self.informativo_id)
            if len(informativo_por_id) == 0:
                self.list_informativo()
            else:
                self.context['informativo_id'] = self.informativo_id
                form = self.Form_class(
                    initial={'chamada': informativo_por_id[0].chamada,
                             'habilitado': informativo_por_id[0].habilitado})
                self.context['form'] = form

        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        if not self.tem_permissao(request, **kwargs):
            return render(request, self.template_name, self.context)

        form = None
        self.get_informativo_id(**kwargs)
        if self.informativo_id == 'add':
            form = self.Form_class(request.POST)
        else:
            informativo_por_id = InformacaoModulo.objects.filter(
                id=self.informativo_id)
            if len(informativo_por_id) == 0:
                self.list_informativo()
            else:
                self.context['informativo_id'] = self.informativo_id
                form = self.Form_class(
                    request.POST,
                    initial={'chamada': informativo_por_id[0].chamada,
                             'habilitado': informativo_por_id[0].habilitado})

        if form is not None:
            if form.is_valid():
                chamada = form.cleaned_data['chamada']
                habilitado = form.cleaned_data['habilitado']
                if self.informativo_id == 'add':
                    informativo = InformacaoModulo(
                        usuario=request.user)
                else:
                    informativo = InformacaoModulo.objects.get(
                        id=self.informativo_id)
                informativo.chamada = chamada
                informativo.habilitado = habilitado
                informativo.painel_modulo = self.modulo
                informativo.save()
                self.list_informativo()
            else:
                self.context['form'] = form
        return render(request, self.template_name, self.context)


def pop(request, pop_assunto=None, id=None):
    assunto = PopAssunto.objects.get(slug=pop_assunto)
    if assunto.grupo_slug == '':
        titulo = 'POPs de {}'.format(assunto.nome)
    else:
        titulo = assunto.nome
    context = {'titulo': titulo}

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
        select = select.order_by('descricao')
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
            'headers': ('Adicionado em', 'Título', 'Arquivo POP',
                        'Habilitado', 'Editar'),
            'fields': ('uploaded_at', 'descricao', 'pop',
                       'habilitado', 'edit'),
        })
    else:
        context.update({
            'headers': ['Título'],
            'fields': ['descricao'],
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


def gera_fluxo_dot(request, destino, id):
    fluxo = dict_fluxo(id)
    if fluxo is None:
        return HttpResponse("Fluxo {} não encontrado".format(id))

    if destino in ['a', 'f']:
        filename = \
            'roteiros_alt{id}_{versao_num}_{versao_sufixo}' \
            '.dot'.format(**fluxo)
        templ = loader.get_template(fluxo['template_base'])
        http_resp = HttpResponse(
            templ.render(fluxo, request), content_type='text/plain')
        http_resp['Content-Disposition'] = \
            'attachment; filename="{filename}"'.format(filename=filename)
        return http_resp

    else:
        return render(
            request, fluxo['template_base'], fluxo,
            content_type='text/plain')


class GeraFluxoDot(O2BaseGetPostView):
    def __init__(self, *args, **kwargs):
        super(GeraFluxoDot, self).__init__(*args, **kwargs)
        self.Form_class = forms.GeraFluxoDotForm
        self.template_name = 'geral/gera_fluxo_dot.html'
        self.title_name = 'Gera fluxo ".dot"'
        self.get_args = ['destino', 'id']

    def mount_context(self):
        destino = self.form.cleaned_data['destino']
        id = self.form.cleaned_data['id']
        self.context.update({
            'destino': destino,
            'id': id,
        })
        fluxo = dict_fluxo(id)
        if fluxo is None:
            self.context.update({
                'erro': "Fluxo {} não encontrado".format(id),
            })


def roteiros_de_fluxo(request, id):
    roteiros = get_roteiros_de_fluxo(id)
    return HttpResponse(
        pformat(roteiros, indent=4),
        content_type='text/plain')


def unidade(request):
    cursor = db_cursor_so(request)
    data = queries.unidades(cursor)
    context = {
        'titulo': 'Unidades / Divisões',
        'headers': ('Código ', 'Descrição', 'UF', 'Cidade',
                    '(CNPJ) Razão social'),
        'fields': ('DIV', 'DESCR', 'UF', 'CIDADE',
                   'NOME'),
        'data': data,
    }
    return render(request, 'geral/unidade.html', context)


class Configuracao(PermissionRequiredMixin, View):
    def __init__(self, *args, **kwargs):
        self.permission_required = 'geral.change_config'
        self.Form_class = forms.ConfigForm
        self.template_name = 'geral/config.html'
        self.title_name = 'Configuração'

    def get_values(self, request):
        values = {}
        for field in self.Form_class.field_param:
            param = self.Form_class.field_param[field]
            if request.user.is_superuser:
                values[field] = config_get_value(param)
            else:
                values[field] = config_get_value(param, request.user)
        return values

    def set_values(self, request, values):
        if request.user.is_superuser:
            usuario = None
        else:
            usuario = request.user
        ok = True
        for field in self.Form_class.field_param:
            param = self.Form_class.field_param[field]
            ok = ok and config_set_value(param, values[field], usuario=usuario)
        return ok

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        values = self.get_values(request)
        form.fields["op_unidade"].initial = values['op_unidade']
        form.fields["dias_alem_lead"].initial = values['dias_alem_lead']
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            values = {}
            values['op_unidade'] = form.cleaned_data['op_unidade']
            values['dias_alem_lead'] = form.cleaned_data['dias_alem_lead']
            if self.set_values(request, values):
                context['msg'] = 'Valores salvos!'
            else:
                context['msg'] = 'Houve algum erro ao salvar os valores!'
        context['form'] = form
        return render(request, self.template_name, context)
