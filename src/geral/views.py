import yaml
from pprint import pprint

from django.shortcuts import render, redirect, get_object_or_404
from django.db import connections
from django.views import View
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from fo2.models import rows_to_dict_list
# from utils.classes import LoggedInUser

from .models import Painel, PainelModulo, InformacaoModulo, \
                    UsuarioPainelModulo, Pop, PopAssunto
from .forms import InformacaoModuloForm, PopForm


def index(request):
    context = {}
    return render(request, 'geral/index.html', context)


def deposito(request):
    cursor = connections['so'].cursor()
    sql = '''
        SELECT
          d.CODIGO_DEPOSITO COD
        , d.DESCRICAO DESCR
        , d.TIP_PROPRIEDADE_DEPOSITO PROP
        , d.CNPJ9
        , d.CNPJ4
        , d.CNPJ2
        , CASE WHEN d.CNPJ9 = 0 THEN ' '
          ELSE coalesce(coalesce(f.NOME_FANTASIA, f.NOME_FORNECEDOR), '#')
          END FORN
        FROM BASI_205 d
        LEFT JOIN SUPR_010 f
          ON f.FORNECEDOR9 = d.CNPJ9
         AND f.FORNECEDOR4 = d.CNPJ4
         AND f.FORNECEDOR2 = d.CNPJ2
        ORDER BY
          d.CODIGO_DEPOSITO
    '''
    cursor.execute(sql)
    data = rows_to_dict_list(cursor)
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
    cursor = connections['so'].cursor()
    sql = '''
        SELECT
          e.CODIGO_ESTAGIO EST
        , e.DESCRICAO DESCR
        , CASE WHEN e.CODIGO_DEPOSITO = 0 THEN ' '
          ELSE e.CODIGO_DEPOSITO || '-' || d.DESCRICAO
          END DEP
        , e.LEED_TIME LT
        FROM MQOP_005 e
        LEFT JOIN BASI_205 d
          ON d.CODIGO_DEPOSITO = e.CODIGO_DEPOSITO
        ORDER BY
          e.CODIGO_ESTAGIO
    '''
    cursor.execute(sql)
    data = rows_to_dict_list(cursor)
    context = {
        'titulo': 'Estágios',
        'headers': ('Estágio', 'Descrição', 'Lead time', 'Depósito'),
        'fields': ('EST', 'DESCR', 'LT', 'DEP'),
        'data': data,
    }
    return render(request, 'geral/tabela_geral.html', context)


class PainelView(View):

    def get(self, request, *args, **kwargs):
        if 'painel' in kwargs:
            if len(kwargs['painel']) == 0:
                return redirect('apoio_ao_erp')

        cursor = connections['so'].cursor()
        painel = Painel.objects.filter(slug=kwargs['painel'])
        if len(painel) == 0:
            return redirect('apoio_ao_erp')

        layout = painel[0].layout
        config = yaml.load(layout)
        for modulo in config['dados']:
            modulo['dados'] = InformacaoModulo.objects.filter(
                painel_modulo__nome=modulo['modulo'],
                habilitado=True
            ).order_by('-data')

        context = {
            'titulo': painel[0].nome,
            'config': config,
            }
        return render(
            request, 'geral/{}.html'.format(config['template']), context)


class InformativoView(LoginRequiredMixin, View):
    Form_class = InformacaoModuloForm
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
    select = PopAssunto.objects.get(slug=pop_assunto)

    context = {'titulo': 'POPs de {}'.format(select.nome)}

    can_edit = False
    user = None
    if request.user.is_authenticated():
        user = request.user
    if user:
        can_edit = user.has_perm('geral.can_manage_pop')

    if can_edit:
        if id:
            instance = get_object_or_404(Pop, id=id)
            context.update({'edit': True})
        else:
            instance = None
            context.update({'insert': True})
        if request.method == 'POST':
            form = PopForm(request.POST, request.FILES, instance=instance)
            if form.is_valid():
                form.save()
                return redirect('geral:pop', pop_assunto)
        else:
            form = PopForm(instance=instance)
        context.update({'form': form})

    if can_edit:
        select = Pop.objects.filter(assunto__slug=pop_assunto)
        select = select.order_by('-uploaded_at')
    else:
        select = Pop.objects.filter(assunto__slug=pop_assunto, habilitado=True)
        select = select.order_by('descricao')
    select = select.values(
        'id', 'uploaded_at', 'assunto__nome', 'descricao', 'pop', 'habilitado')
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
            'headers': ('Adicionado em', 'Assunto', 'Título', 'Arquivo POP',
                        'Habilitado', 'Editar'),
            'fields': ('uploaded_at', 'assunto__nome', 'descricao', 'pop',
                       'habilitado', 'edit'),
        })
    else:
        context.update({
            'headers': ['Título'],
            'fields': ['descricao'],
        })
    return render(request, 'geral/pop.html', context)
