import yaml
from pprint import pprint

from django.shortcuts import render, redirect, get_object_or_404
from django.db import connections
from django.views import View
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.http import HttpResponse
from django.template import loader

from fo2.models import rows_to_dict_list
# from utils.classes import LoggedInUser

from .models import Painel, PainelModulo, InformacaoModulo, \
                    UsuarioPainelModulo, Pop, PopAssunto, UsuarioPopAssunto
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
    assunto = PopAssunto.objects.get(slug=pop_assunto)

    context = {'titulo': 'POPs de {}'.format(assunto.nome)}

    can_edit = False
    user = None
    if request.user.is_authenticated():
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
            form = PopForm(request.POST, request.FILES, instance=instance)
            if form.is_valid():
                form.save()
                return redirect('geral:pop', pop_assunto)
        else:
            if instance is None:
                form = PopForm()
                form.fields['assunto'].initial = assunto.id
            else:
                form = PopForm(instance=instance)
        form.fields['assunto'].widget = forms.HiddenInput()
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
    return render(request, 'geral/pop.html', context)


def update_dict(original, adding):
    result = original.copy()
    for key in adding.keys():
        if adding[key] is None:
            continue
        if isinstance(adding[key], dict):
            if key not in result or not isinstance(result[key], dict):
                result[key] = adding[key].copy()
            else:
                result[key] = update_dict(result[key], adding[key])
        else:
            result[key] = adding[key]
    return result


def gera_fluxo_dot(request, destino, id):
    id = int(id)

    alternativas = {
        1: 'Interno',
        11: 'PB Interno',
        21: 'PG Interno',
        31: 'PA de PG Interno',
        2: 'Unidade Sem Corte',
        12: 'PB Unidade Sem Corte',
        22: 'PG Unidade Sem Corte',
        32: 'PA de PG Unidade Sem Corte',
        3: 'Unidade Com Corte',
        13: 'PB Unidade Com Corte',
        24: 'PG Unidade Com Corte',
        4: 'Sem Costura',
        14: 'PB Sem Costura',
        24: 'PG Sem Costura',
        34: 'PA de PG Sem Costura',
        5: 'Praia',
        15: 'PB Praia',
        25: 'PG Praia',
        35: 'PA de PG Praia',
        6: 'Camisa',
        8: 'Forro Interno',
    }

    roteiros = {
        'mp': {
            8: 'Forro Interno',
        },
        'md': {
            1: 'MD Interno',
            2: 'MD Unidade Sem Corte',
            3: 'MD Unidade Com Corte',
            4: 'MD Sem Costura',
            5: 'MD Praia',
            6: 'MD Camisa',
        },
        'pb': {
            11: 'PB Interno',
            12: 'PB Unidade Sem Corte',
            13: 'PB Unidade Com Corte',
            14: 'PB Sem Costura',
            15: 'PB Praia',
        },
        'pg': {
            21: 'PG Interno',
            22: 'PG Unidade Sem Corte',
            23: 'PG Unidade Com Corte',
            24: 'PG Sem Costura',
            25: 'PG Praia',
        },
        'pa': {
            1: 'PA Interno',
            11: 'PA de PB Interno',
            21: 'PA de PG Interno',
            31: 'PA de PG Interno',
            2: 'PA Unidade Sem Corte',
            12: 'PA de PB Unidade Sem Corte',
            22: 'PA de PG Unidade Sem Corte',
            32: 'PA de PG Unidade Sem Corte',
            3: 'PA Unidade Com Corte',
            13: 'PA de PB Unidade Com Corte',
            23: 'PA de PG Unidade Com Corte',
            4: 'PA Sem Costura',
            14: 'PA de PB Sem Costura',
            24: 'PA de PG Sem Costura',
            34: 'PA de PG Sem Costura',
            5: 'PA Praia',
            15: 'PA de PB Praia',
            25: 'PA de PG Praia',
            35: 'PA de PG Praia',
        }
    }

    estagios = {
        3: {
            'descr': 'PCP (Liberação)',
            'deposito': '-',
        },
        6: {
            'descr': 'Risco',
            'deposito': '-',
        },
        9: {
            'descr': 'Abastece Fio',
            'deposito': '212',
        },
        12: {
            'descr': 'Etiquetas',
            'deposito': '231',
        },
        15: {
            'descr': 'Corte',
            'deposito': '-',
        },
        18: {
            'descr': 'Separação insumo',
            'deposito': '231',
        },
        19: {
            'descr': 'Separação insumo',
            'deposito': '231',
        },
        21: {
            'descr': 'Distribuição',
            'deposito': '-',
        },
        22: {
            'descr': 'Distribuição Tecelagem',
            'deposito': '-',
        },
        'os': {
            'codigo': 'OS',
            'descr': 'OS/NF',
            'deposito': '',
        },
        24: {
            'descr': 'Recepção',
            'deposito': '-',
        },
        27: {
            'descr': 'Tecelagem saia / meia',
            'deposito': '212',
        },
        30: {
            'descr': 'Tecelagem fundo',
            'deposito': '212',
        },
        33: {
            'descr': 'Costura Costurado',
            'deposito': '231',
        },
        36: {
            'descr': 'Costura Tecelagem',
            'deposito': '231',
        },
        39: {
            'descr': 'Tinturaria',
            'deposito': '-',
        },
        45: {
            'descr': 'Transfer / TAG',
            'deposito': '231',
        },
        48: {
            'descr': 'Revisão',
            'deposito': '-',
        },
        51: {
            'descr': 'CD MD',
            'deposito': '-',
        },
        54: {
            'descr': 'Terceiro MG',
            'deposito': '231',
        },
        55: {
            'descr': 'Terceiro RJ',
            'deposito': '231',
        },
        57: {
            'descr': 'Armazena',
            'deposito': '-',
        },
        60: {
            'descr': 'Embalagem',
            'deposito': '231',
        },
        63: {
            'descr': 'CD',
            'deposito': '-',
        },
        66: {
            'descr': 'Expedição',
            'deposito': '231',
        },
    }

    fluxo_padrao = {}
    fluxo_padrao['cueca'] = {
        # gerais
        'estagios': estagios,
        'alternativas': alternativas,
        'roteiros': roteiros,
        # templates
        'template_base': 'geral/fluxo.html',
        'template_bloco': 'geral/fluxo_bloco.html',
        # específicos
        'versao_num': '19.01',
        'versao_data': '11/02/2019',
        'tem_mp': False,
        'md_p_pb': {
            'nivel': 'md',
            'alt_incr': 0,
            'nome': 'mdpb',
            'cabecalho': 'MD p/ PB - <b><u>M</u></b>999*<br />'
                         'Com acessórios (TAG)<br />para encabidar',
        },
        'md_p_pg': {
            'nivel': 'md',
            'alt_incr': 0,
            'nome': 'mdpg',
            'cabecalho': 'MD p/ PB - <b><u>M</u></b>999<b><u>A</u></b><br />'
                         'Sem acessórios (TAG)<br />para encabidar',
        },
        'pb': {
            'nivel': 'pb',
            'alt_incr': 10,
            'nome': 'pb1x',
            'cabecalho': 'PB - <b><u>B</u></b>999*<br />'
                         'Depósito da OP: 231<br /><br />'
                         'Individual Encabidado',
        },
        'pg': {
            'nivel': 'pg',
            'alt_incr': 20,
            'nome': 'pg2x',
            'cabecalho': 'PG - <b><u>A</u></b>999*<br />'
                         'Depósito da OP: 231<br /><br />'
                         'Kit ou<br />Individual Encabidado ou<br />'
                         'Individual Embalado',
        },
        'pa_de_md': {
            'nivel': 'pa',
            'alt_incr': 0,
            'nome': 'pa0x',
            'cabecalho': 'Kit ou<br />Individual Encabidado ou<br />'
                         'Individual Embalado<br />'
                         '(a desativar)',
        },
        'pa_a_de_pb': {
            'nivel': 'pa',
            'alt_incr': 10,
            'nome': 'pa1x',
            'cabecalho': 'Individual Encabidado',
        },
        'pa_e_de_pg': {
            'nivel': 'pa',
            'alt_incr': 20,
            'nome': 'pa2x',
            'cabecalho': 'Kit ou<br />Individual Embalado',
        },
        'pa_a_de_pg': {
            'nivel': 'pa',
            'alt_incr': 30,
            'nome': 'pa3x',
            'cabecalho': 'Individual Emcabidado',
        },
    }

    fluxo_padrao['1_bloco'] = {
        # gerais
        'estagios': estagios,
        'alternativas': alternativas,
        'roteiros': roteiros,
        # templates
        'template_base': 'geral/fluxo_com_1_bloco.html',
        'template_bloco': 'geral/fluxo_bloco.html',
        # específicos
        'versao_num': '19.01',
        'versao_data': '11/02/2019',
        'bloco': {
            'alt_incr': 0,
            'nome': 'bloco',
        },
    }

    fluxo_config = {}

    fluxo_config[1] = {
        'base': 'cueca',
        'fluxo_num': 1,
        'fluxo_nome': 'Interno',
        'produto': 'CUECA COM costura - PRAIA - SHORT',
        'caracteristicas': [
            'Corte: Interno',
            'Estamparia: Interna ou Sem',
            'Costura: Interna',
        ],
        'tem_mp': True,
        'md_p_pb': {
            'ests': [3, 6, 12, 15, 18, 21, 33, 45, 48, 51],
            'gargalo': 33,
            'insumos': {
                15: ['Malha', ],
                18: ['Etiquetas',
                     'Elástico',
                     'TAG',
                     'Transfer', ],
            },
        },
        'md_p_pg': {
            'estagios': {
                3: ['', ],
                6: ['', ],
                12: ['', ],
                15: ['', [
                    'Malha',
                ]],
                18: ['', [
                    'Etiquetas',
                    'Elástico',
                    'Transfer',
                ]],
                21: ['', ],
                33: ['#', ],
                45: ['', ],
                48: ['', ],
                51: ['', ],
            }
        },
        'pb': {
            'estagios': {
                3: ['', ],
                18: ['', [
                    'Cabide',
                ]],
                60: ['#', ['MD p/ PB<br /><b><u>M</u></b>999*']],
                57: ['', []],
                63: ['', []],
            }
        },
        'pg': {
            'estagios': {
                3: ['', ],
                18: ['', ],
                60: ['#', [
                    'MD p/ PG<br /><b><u>M</u></b>999<b><u>A</u></b>']],
                57: ['', []],
                63: ['', []],
            }
        },
        'pa_de_md': {
            'estagios': {
                3: ['', ],
                18: ['', [
                    'TAG',
                    'Cabide',
                    'Embalagem',
                    'Cartela',
                ]],
                60: ['#', ['MD<br /><b><u>M</u></b>999*']],
                57: ['', []],
                63: ['', []],
                66: ['', [
                    'Etiquetas',
                    'Caixa',
                ]],
            }
        },
        'pa_a_de_pb': {
            'estagios': {
                3: ['', ],
                18: ['', [
                    'Etiquetas',
                    'Caixa',
                ]],
                66: ['#', ['PB<br /><b><u>B</u></b>999*']],
            }
        },
        'pa_e_de_pg': {
            'estagios': {
                3: ['', ],
                18: ['', [
                    'Embalagem',
                    'Cartela',
                    'Etiquetas',
                    'Caixa',
                ]],
                66: ['#', ['PG<br /><b><u>A</u></b>999*']],
            }
        },
        'pa_a_de_pg': {
            'estagios': {
                3: ['', ],
                18: ['', [
                    'TAG',
                    'Cabide',
                    'Etiquetas',
                    'Caixa',
                ]],
                66: ['#', ['PG<br /><b><u>A</u></b>999*']],
            }
        },
    }

    fluxo_config[2] = {
        'base': 'cueca',
        'fluxo_num': 2,
        'fluxo_nome': 'Externo',
        'produto': 'CUECA COM costura',
        'caracteristicas': [
            'Corte: Interno',
            'Costura: Externa',
        ],
        'md_p_pb': {
            'estagios': {
                3: ['', ],
                6: ['', ],
                15: ['', [
                    'Malha',
                ]],
                18: ['', ],
                12: ['#', ],
            }
        },
        'md_p_pg': {
            'estagios': {
                3: ['', ],
                6: ['', ],
                15: ['', [
                    'Malha',
                ]],
                18: ['', ],
                12: ['#', ],
            }
        },
        'pb': {
            'estagios': {
                3: ['', ],
                18: ['', [
                    'Etiquetas',
                    'Elástico',
                    'TAG',
                    'Cabide',
                ]],
                21: ['', []],
                'os': ['', ['MD p/ PB<br /><b><u>M</u></b>999*']],
                24: ['#', []],
                55: ['', []],
                57: ['', []],
                63: ['', []],
            }
        },
        'pg': {
            'estagios': {
                3: ['', ],
                18: ['', [
                    'Etiquetas',
                    'Elástico',
                ]],
                21: ['', []],
                'os': ['', [
                    'MD p/ PG<br /><b><u>M</u></b>999<b><u>A</u></b>']],
                24: ['#', []],
                55: ['', []],
                57: ['', []],
                63: ['', []],
            }
        },
        'pa_de_md': {
            'estagios': {
                3: ['', ],
                18: ['', [
                    'Etiquetas',
                    'Elástico',
                    'TAG',
                    'Transfer',
                    'Cabide',
                    'Embalagem',
                    'Cartela',
                    'Etiquetas',
                    'Caixa',
                ]],
                21: ['', []],
                'os': ['', ['MD<br /><b><u>M</u></b>999*']],
                24: ['#', []],
                55: ['', []],
                57: ['', []],
                63: ['', []],
                66: ['', []],
            }
        },
        'pa_a_de_pb': {
            'estagios': {
                3: ['', ],
                18: ['', [
                    'Transfer',
                    'Etiquetas',
                    'Caixa',
                ]],
                66: ['#', ['PB<br /><b><u>B</u></b>999*']],
            }
        },
        'pa_e_de_pg': {
            'estagios': {
                3: ['', ],
                18: ['', [
                    'Transfer',
                    'Embalagem',
                    'Cartela',
                    'Etiquetas',
                    'Caixa',
                ]],
                66: ['#', ['PG<br /><b><u>A</u></b>999*']],
            }
        },
        'pa_a_de_pg': {
            'estagios': {
                3: ['', ],
                18: ['', [
                    'Transfer',
                    'TAG',
                    'Cabide',
                    'Etiquetas',
                    'Caixa',
                ]],
                66: ['#', ['PG<br /><b><u>A</u></b>999*']],
            }
        },
    }

    fluxo_config[3] = {
        'base': 'cueca',
        'fluxo_num': 3,
        'fluxo_nome': 'Externo',
        'produto': 'CUECA COM costura',
        'caracteristicas': [
            'Corte: Externo',
            'Costura: Externa',
        ],
        'md_p_pb': {
            'cabecalho': 'MD - <b><u>M</u></b>999*',
            'ests': [3, 6, 12],
            'gargalo': 12,
        },
        'md_p_pg': False,
        'pb': {
            'ests': [3, 18, 21, 'os', 24, 54, 57, 63],
            'gargalo': 24,
            'insumos': {
                18: [
                    'Malha',
                    'Etiquetas',
                    'Elástico',
                    'TAG',
                    'Cabide',
                ],
                'os': ['MD<br /><b><u>M</u></b>999*', ],
            },
        },
        'pg': {
            'ests': [3, 18, 21, 'os', 24, 54, 57, 63],
            'gargalo': 24,
            'insumos': {
                18: [
                    'Malha',
                    'Etiquetas',
                    'Elástico',
                ],
                'os': ['MD<br /><b><u>M</u></b>999*', ],
            },
        },
        'pa_de_md': {
            'ests': [3, 18, 21, 'os', 24, 54, 57, 63, 66],
            'gargalo': 24,
            'insumos': {
                18: [
                    'Etiquetas',
                    'Elástico',
                    'TAG',
                    'Transfer',
                    'Cabide',
                    'Embalagem',
                    'Cartela',
                ],
                'os': ['MD<br /><b><u>M</u></b>999*'],
                66: [
                    'Etiquetas',
                    'Caixa',
                ],
            }
        },
        'pa_a_de_pb': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Transfer',
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PB<br /><b><u>B</u></b>999*'],
            }
        },
        'pa_e_de_pg': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Transfer',
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PB<br /><b><u>B</u></b>999*'],
            }
        },
        'pa_a_de_pg': False,
    }

    fluxo_config[4] = fluxo_config[1].copy()
    fluxo_config[4].update({
        'base': 'cueca',
        'fluxo_num': 4,
        'fluxo_nome': 'Sem costura',
        'produto': 'CUECA SEM costura',
        'caracteristicas': [
            'Tecelagem: Interna',
            'Costura: Internaa',
            'Tingimento: Externo',
        ],
        'tem_mp': False,
        'md_p_pb': {
            'ests': [3, 22, 9, 27, 30, 36, 21, 'os', 24, 39, 18, 45, 48, 51],
            'gargalo': 27,
            'insumos': {
                15: ['Malha', ],
                18: ['Etiquetas',
                     'TAG',
                     'Transfer', ],
            },
        },
        'md_p_pg': {
            'ests': [3, 22, 9, 27, 30, 36, 21, 'os', 24, 39, 18, 45, 48, 51],
            'gargalo': 27,
            'insumos': {
                15: ['Malha', ],
                18: ['Etiquetas',
                     'Transfer', ],
            },
        },
    })

    fluxo_config[5] = fluxo_config[1].copy()
    fluxo_config[5].update({
        'base': 'cueca',
        'fluxo_num': 5,
        'fluxo_nome': 'Externo',
        'produto': 'PRAIA',
        'caracteristicas': [
            'Corte: Interno',
            'Estamparia: Interna ou Sem',
            'Costura: Externa',
        ],
        'md_p_pb': {
            'ests': [3, 6, 12, 15, 18, 21, 'os', 24, 55, 45, 51],
            'gargalo': 24,
            'insumos': {
                15: ['Malha', ],
                18: ['Etiquetas',
                     'Eslástico',
                     'TAG',
                     'Transfer', ],
            },
        },
        'md_p_pg': {
            'ests': [3, 6, 12, 15, 18, 21, 'os', 24, 55, 45, 51],
            'gargalo': 24,
            'insumos': {
                15: ['Malha', ],
                18: ['Etiquetas',
                     'Eslástico',
                     'Transfer', ],
            },
        },
    })

    fluxo_config[6] = {
        'base': '1_bloco',
        'fluxo_num': 6,
        'fluxo_nome': 'Externo',
        'produto': 'CAMISA',
        'caracteristicas': [
            'Corte: Interno',
            'Costura: Externa',
        ],
        'seta_label': 'MD',
        'bloco': {
            'nivel': 'md',
            'cabecalho': 'MD - x9999<br />'
                         'Depósito da OP: 231',
            'ests': [3, 6, 12, 15, 18, 21, 'os', 24, 55, 45, 51],
            'gargalo': 24,
            'insumos': {
                15: ['Malha', ],
                18: ['Etiquetas',
                     'Eslástico',
                     'TAG',
                     'Transfer', ],
            },
        },
    }

    fluxo_config[8] = {
        'base': '1_bloco',
        'fluxo_num': 8,
        'fluxo_nome': 'Parte',
        'produto': 'PRAIA (Forro)',
        'caracteristicas': [
            'Corte: Interno',
        ],
        'seta_label': 'MP',
        'bloco': {
            'nivel': 'mp',
            'cabecalho': 'MP - <b><u>F</u></b>9999<br />'
                         'Depósito da OP: 231',
            'ests': [3, 6, 15],
            'gargalo': 6,
            'insumos': {
                15: ['Malha', ],
            },
        },
    }

    fluxo = update_dict(
        fluxo_padrao[fluxo_config[id]['base']], fluxo_config[id])

    if destino in ['a', 'f']:
        filename = \
            'roteiros_alt{fluxo_num}_{versao_num}_{versao_data}.dot'.format(
                **fluxo)
        templ = loader.get_template(fluxo['template_base'])
        http_resp = HttpResponse(
            templ.render(fluxo, request), content_type='text/plain')
        http_resp['Content-Disposition'] = \
            'attachment; filename="{filename}"'.format(filename=filename)
        return http_resp

    else:
        return render(
            request, fluxo['template_base'], fluxo, content_type='text/plain')
