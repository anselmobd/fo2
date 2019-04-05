from pprint import pprint, pformat
import yaml

from django import forms
from django.db import connections
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View

from base.views import O2BaseGetPostView

from fo2.models import rows_to_dict_list
# from utils.classes import LoggedInUser

import produto.queries

from .models import Painel, PainelModulo, InformacaoModulo, \
                    UsuarioPainelModulo, Pop, PopAssunto, UsuarioPopAssunto
import geral.forms as forms
import geral.queries as queries


def index(request):
    context = {}
    return render(request, 'geral/index.html', context)


def deposito(request):
    data = queries.deposito()
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
            form = forms.PopForm(request.POST, request.FILES, instance=instance)
            if form.is_valid():
                form.save()
                return redirect('geral:pop', pop_assunto)
        else:
            if instance is None:
                form = forms.PopForm()
                form.fields['assunto'].initial = assunto.id
            else:
                form = forms.PopForm(instance=instance)
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


def dict_alternativas():
    return {
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
        23: 'PG Unidade Com Corte',
        4: 'Sem Costura',
        14: 'PB Sem Costura',
        24: 'PG Sem Costura',
        34: 'PA de PG Sem Costura',
        5: 'Sunga',
        15: 'PB Sunga',
        25: 'PG Sunga',
        35: 'PA de PG Sunga',
        6: 'Camisa',
        7: 'Pijama',
        27: 'PG Pijama',
        8: 'Forro Interno',
        9: 'Meia',
        29: 'PG Meia',
        51: 'Interno',
        61: 'PB Interno',
        71: 'PG Interno',
        81: 'PA de PG Interno',
        52: 'Sobra de Multimarca',
    }


def dict_roteiros():
    return {
        'mp': {
            8: 'Forro Interno',
        },
        'md': {
            1: 'MD Interno',
            2: 'MD Unidade Sem Corte',
            3: 'MD Unidade Com Corte',
            4: 'MD Sem Costura',
            5: 'MD Sunga',
            6: 'MD Camisa',
            9: 'MD Meia',
            51: 'MD Interno',
            52: 'Sobra de Multimarca',
        },
        'pb': {
            11: 'PB Interno',
            12: 'PB Unidade Sem Corte',
            13: 'PB Unidade Com Corte',
            14: 'PB Sem Costura',
            15: 'PB Sunga',
            61: 'PB Interno',
        },
        'pg': {
            21: 'PG Interno',
            22: 'PG Unidade Sem Corte',
            23: 'PG Unidade Com Corte',
            24: 'PG Sem Costura',
            25: 'PG Sunga',
            27: 'PG Pijama',
            29: 'PG Meia',
            71: 'PG Interno',
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
            5: 'PA Sunga',
            15: 'PA de PB Sunga',
            25: 'PA de PG Sunga',
            35: 'PA de PG Sunga',
            7: 'PA Pijama',
            27: 'PA de PG Pijama',
            9: 'PA Meia',
            29: 'PA de PG Meia',
            51: 'PA Interno',
            61: 'PA de PB Interno',
            71: 'PA de PG Interno',
            81: 'PA de PG Interno',
            52: 'Sobra de Multimarca',
        }
    }


def dict_estagios():
    return {
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
            'deposito': '-',
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
        28: {
            'descr': 'Passadoria',
            'deposito': '-',
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


def dict_fluxo(id):
    try:
        id = int(id)
        fluxo_num = int(id)
    except Exception:
        fluxo_num = int(id[:-1])

    alternativas = dict_alternativas()
    roteiros = dict_roteiros()
    estagios = dict_estagios()

    fluxo_base = {
        # gerais
        'alternativas': alternativas,
        'roteiros': roteiros,
        'estagios': estagios,
        # templates
        'template_bloco': 'geral/fluxo_bloco.html',
        # específicos
        # 'rascunho': '#Rascunho#',
        'rascunho': '',
        'versao_num': '19.01',
        'versao_data': '05/04/2019',
        'versao_sufixo': '20190405',
        'id': id,
        'fluxo_num': fluxo_num,
    }

    fluxo_padrao = {}

    fluxo_padrao['cueca'] = fluxo_base.copy()
    fluxo_padrao['cueca'].update({
        # templates
        'template_base': 'geral/fluxo.html',
        # específicos
        'tem_mp': False,
        'seta_md_label': 'MD',
        'seta_pg_label': 'PG / PB',
        'seta_pa_label': 'PA',
        'md_cabecalho': 'MD\nDepósito da OP: 231',
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
            'cabecalho': 'MD p/ PG - <b><u>M</u></b>999<b><u>A</u></b><br />'
                         'Sem acessórios (TAG)<br />para encabidar',
        },
        'mdext1': False,
        'mdext2': False,
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
        'pa_cabecalho': 'PA - 9999*\nDepósito da OP: 101/102',
        'pa_de_md': {
            'nivel': 'pa',
            'alt_incr': 0,
            'nome': 'pa0x',
            'cabecalho': 'Kit ou<br />Individual Encabidado ou<br />'
                         'Individual Embalado<br />'
                         '(a desativar)',
        },
        'pa_enc_de_pb': {
            'nivel': 'pa',
            'alt_incr': 10,
            'nome': 'pa1x',
            'cabecalho': 'Individual Encabidado',
        },
        'pa_emb_de_pg': {
            'nivel': 'pa',
            'alt_incr': 20,
            'nome': 'pa2x',
            'cabecalho': 'Kit ou<br />Individual Embalado',
        },
        'pa_enc_de_pg': {
            'nivel': 'pa',
            'alt_incr': 30,
            'nome': 'pa3x',
            'cabecalho': 'Individual Emcabidado',
        },
    })

    fluxo_padrao['1_bloco'] = fluxo_base.copy()
    fluxo_padrao['1_bloco'].update({
        # templates
        'template_base': 'geral/fluxo_com_1_bloco.html',
        # específicos
        'bloco': {
            'alt_incr': 0,
            'nome': 'bloco',
        },
    })

    fluxo_config = {}

    fluxo_config[1] = {
        'base': 'cueca',
        'fluxo_nome': 'Interno',
        'produto': 'CUECA COM costura',
        'caracteristicas': [
            'Corte: Interno',
            'Costura: Interna',
        ],
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
            'ests': [3, 6, 12, 15, 18, 21, 33, 45, 48, 51],
            'gargalo': 33,
            'insumos': {
                15: ['Malha', ],
                18: ['Etiquetas',
                     'Elástico',
                     'Transfer', ],
            },
        },
        'pb': {
            'ests': [3, 18, 60, 57, 63],
            'gargalo': 60,
            'insumos': {
                18: ['Cabide', ],
                60: ['MD p/ PB<br /><b><u>M</u></b>999*', ],
            },
        },
        'pg': {
            'ests': [3, 18, 60, 57, 63],
            'gargalo': 60,
            'insumos': {
                60: ['MD p/ PG<br /><b><u>M</u></b>999<b><u>A</u></b>', ],
            },
        },
        'pa_de_md': {
            'ests': [3, 18, 60, 57, 63, 66],
            'gargalo': 60,
            'insumos': {
                18: [
                    'Cabide',
                    'Embalagem',
                    'Cartela',
                    'Etiquetas',
                    'Caixa',
                ],
                60: ['MD<br /><b><u>M</u></b>999*'],
            }
        },
        'pa_enc_de_pb': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PB<br /><b><u>B</u></b>999*'],
            }
        },
        'pa_emb_de_pg': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Embalagem',
                    'Cartela',
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PG<br /><b><u>A</u></b>999*'],
            }
        },
        'pa_enc_de_pg': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'TAG',
                    'Cabide',
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PG<br /><b><u>A</u></b>999*'],
            }
        },
    }

    # 1p
    fluxo_aux = {
        'produto': 'SHORT',
        'caracteristicas': [
            'Corte: Interno',
            'Estamparia: Interna ou Sem',
            'Costura: Interna',
        ],
        'seta_pg_label': 'PG',
        'tem_mp': False,
        'md_p_pb': False,
        'md_p_pg': {
            'cabecalho': 'MD - <b><u>M</u></b>999*',
            'insumos': {
                15: ['Forro',
                     'Malha', ],
                18: ['Etiquetas',
                     'Elástico',
                     'Cadarço', ],
            },
        },
        'pb': False,
        'pg': {
            'cabecalho': 'PG - <b><u>A</u></b>999*<br />'
                         'Depósito da OP: 231',
            'insumos': {
                18: ['TAG', ],
                60: ['MD<br /><b><u>M</u></b>999*', ],
            },
        },
        'pa_de_md': {
            'cabecalho': 'Individual Encabidado ou<br />'
                         'Individual Embalado<br />'
                         '(a desativar)',
            'insumos': {
                18: [
                    'TAG',
                    'Cabide',
                    'Embalagem',
                    'Etiquetas',
                    'Caixa',
                ],
            }
        },
        'pa_enc_de_pb': False,
        'pa_emb_de_pg': {
            'cabecalho': 'Individual Embalado',
            'insumos': {
                18: [
                    'Embalagem',
                    'Etiquetas',
                    'Caixa',
                ],
            }
        },
        'pa_enc_de_pg': {
            'insumos': {
                18: [
                    'Cabide',
                    'Etiquetas',
                    'Caixa',
                ],
            }
        },
    }
    fluxo_config['1p'] = update_dict(fluxo_config[1], fluxo_aux)

    fluxo_config[2] = {
        'base': 'cueca',
        'fluxo_nome': 'Costura externa',
        'produto': 'CUECA COM costura',
        'caracteristicas': [
            'Corte: Interno',
            'Costura: Externa',
        ],
        'md_p_pb': {
            'cabecalho': 'MD p/ PB - <b><u>C</u></b>999*<br />'
                         'Com acessórios (TAG)<br />para encabidar',
            'ests': [3, 6, 15, 18, 12],
            'gargalo': 12,
            'insumos': {
                15: ['Malha', ],
            },
        },
        'md_p_pg': {
            'cabecalho': 'MD p/ PG - <b><u>C</u></b>999<b><u>A</u></b><br />'
                         'Sem acessórios (TAG)<br />para encabidar',
            'ests': [3, 6, 15, 18, 12],
            'gargalo': 12,
            'insumos': {
                15: ['Malha', ],
            },
        },
        'pb': {
            'ests': [3, 18, 21, 'os', 24, 55, 57, 63],
            'gargalo': 24,
            'insumos': {
                'os': ['MD p/ PB<br /><b><u>C</u></b>999*'],
                55: [
                    'Etiquetas',
                    'Elástico',
                    'TAG',
                    'Cabide',
                ],
            }
        },
        'pg': {
            'ests': [3, 18, 21, 'os', 24, 55, 57, 63],
            'gargalo': 24,
            'insumos': {
                'os': ['MD p/ PG<br /><b><u>C</u></b>999<b><u>A</u></b>'],
                55: [
                    'Etiquetas',
                    'Elástico',
                ],
            }
        },
        'pa_de_md': {
            'ests': [3, 18, 21, 'os', 24, 55, 57, 63, 66],
            'gargalo': 24,
            'insumos': {
                18: [
                    'Etiquetas',
                    'Caixa',
                ],
                'os': ['MD<br /><b><u>C</u></b>999*'],
                55: [
                    'Etiquetas',
                    'Elástico',
                    'TAG',
                    'Transfer',
                    'Cabide',
                    'Embalagem',
                    'Cartela',
                ],
            }
        },
        'pa_enc_de_pb': {
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
        'pa_emb_de_pg': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Transfer',
                    'Embalagem',
                    'Cartela',
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PG<br /><b><u>A</u></b>999*'],
            }
        },
        'pa_enc_de_pg': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Transfer',
                    'TAG',
                    'Cabide',
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PG<br /><b><u>A</u></b>999*'],
            }
        },
    }

    # 2p <- 2
    fluxo_aux = {
        'produto': 'SHORT',
        'md_p_pb': {
            'cabecalho': 'MD - <b><u>C</u></b>999*',
            'insumos': {
                15: ['Forro',
                     'Malha', ],
            },
        },
        'md_p_pg': False,
        'pb': False,
        'pg': False,
        'pa_de_md': {
            'ests': [3, 18, 21, 'os', 24, 54, 57, 63, 66],
            'insumos': {
                54: [
                    'Etiquetas',
                    'Elástico',
                    'Ilhós',
                    'Transfer',
                    'Cabide',
                    'Embalagem',
                ],
                55: [],
            }
        },
        'pa_enc_de_pb': False,
        'pa_emb_de_pg': False,
        'pa_enc_de_pg': False,
    }
    fluxo_config['2p'] = update_dict(fluxo_config[2], fluxo_aux)

    fluxo_config[3] = {
        'base': 'cueca',
        'fluxo_nome': 'Corte e costura externos',
        'produto': 'CUECA COM costura',
        'caracteristicas': [
            'Corte: Externo',
            'Costura: Externa',
        ],
        'md_p_pb': {
            'cabecalho': 'MD - <b><u>R</u></b>999*',
            'ests': [3, 6, 12],
            'gargalo': 12,
        },
        'md_p_pg': False,
        'pb': {
            'ests': [3, 18, 21, 'os', 24, 54, 57, 63],
            'gargalo': 24,
            'insumos': {
                'os': ['MD<br /><b><u>R</u></b>999*', ],
                57: [
                    'Malha',
                    'Etiquetas',
                    'Elástico',
                    'Transfer',
                    'TAG',
                    'Cabide',
                ],
            },
        },
        'pg': {
            'ests': [3, 18, 21, 'os', 24, 54, 57, 63],
            'gargalo': 24,
            'insumos': {
                'os': ['MD<br /><b><u>R</u></b>999*', ],
                57: [
                    'Malha',
                    'Etiquetas',
                    'Elástico',
                    'Transfer',
                ],
            },
        },
        'pa_de_md': {
            'ests': [3, 18, 21, 'os', 24, 54, 57, 63, 66],
            'gargalo': 24,
            'insumos': {
                18: [
                    'Etiquetas',
                    'Caixa',
                ],
                'os': ['MD<br /><b><u>R</u></b>999*'],
                54: [
                    'Etiquetas',
                    'Elástico',
                    'TAG',
                    'Cabide',
                    'Embalagem',
                    'Cartela',
                ],
            }
        },
        'pa_enc_de_pb': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PB<br /><b><u>B</u></b>999*'],
            }
        },
        'pa_emb_de_pg': {
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Embalagem',
                    'Cartela',
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PG<br /><b><u>A</u></b>999*'],
            }
        },
        'pa_enc_de_pg': False,
    }

    fluxo_config[4] = fluxo_config[1].copy()
    fluxo_config[4].update({
        'fluxo_nome': 'Tecelagem de cueca',
        'produto': 'CUECA SEM costura',
        'caracteristicas': [
            'Tecelagem: Interna',
            'Costura: Interna',
            'Tingimento: Externo',
        ],
        'tem_mp': False,
        'md_p_pb': {
            'ests': [3, 22, 9, 27, 30, 36, 21, 'os', 24, 39, 18, 45, 48, 51],
            'gargalo': 27,
            'insumos': {
                27: ['Fio', ],
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
                27: ['Fio', ],
                15: ['Malha', ],
                18: ['Etiquetas',
                     'Transfer', ],
            },
        },
    })

    # 5 <- 1
    fluxo_aux = {
        'fluxo_nome': 'Costura externa de sunga',
        'produto': 'SUNGA',
        'caracteristicas': [
            'Corte: Interno',
            'Estamparia: Interna ou Sem',
            'Costura: Externa',
        ],
        'seta_pg_label': 'PG',
        'tem_mp': True,
        'md_p_pb': False,
        'md_p_pg': {
            'cabecalho': 'MD - <b><u>C</u></b>999*',
            'ests': [3, 6, 12, 15, 18, 21, 'os', 24, 55, 45, 51],
            'gargalo': 24,
            'insumos': {
                15: ['Malha', ],
                18: ['Transfer', ],
                55: ['Etiquetas',
                     'Forro - <b><u>F</u></b>999*',
                     'Eslástico',
                     'Cadarço', ],
            },
        },
        'pb': False,
        'pg': {
            'cabecalho': 'PG - <b><u>A</u></b>999*<br />'
                         'Depósito da OP: 231',
            'insumos': {
                18: ['TAG', ],
                60: ['MD<br /><b><u>C</u></b>999*', ],
            },
        },
        'pa_cabecalho': 'PA\nDepósito da OP: 101/102',
        'pa_de_md': {
            'cabecalho': 'PA - 9999*<br /><br />'
                         'Individual Encabidado ou<br />'
                         'Individual Embalado<br />'
                         '(a desativar)',
            'insumos': {
                18: [
                    'TAG',
                    'Cabide',
                    'Embalagem',
                    'Etiquetas',
                    'Caixa',
                ],
                60: ['MD<br /><b><u>C</u></b>999*'],
            }
        },
        'pa_enc_de_pb': False,
        'pa_emb_de_pg': {
            'cabecalho': 'PA - 9999<b><u>A</u></b><br /><br />'
                         'Individual Embalado',
            'insumos': {
                18: [
                    'Embalagem',
                    'Etiquetas',
                    'Caixa',
                ],
            }
        },
        'pa_enc_de_pg': {
            'cabecalho': 'PA - 9999<b><u>A</u></b><br /><br />'
                         'Individual Encabidado',
            'insumos': {
                18: [
                    'Cabide',
                    'Etiquetas',
                    'Caixa',
                ],
            }
        },
    }
    fluxo_config[5] = update_dict(fluxo_config[1], fluxo_aux)

    fluxo_config[6] = {
        'base': '1_bloco',
        'fluxo_nome': 'Costura externa de camisa',
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
                18: ['Transfer', ],
                55: ['Etiquetas', ],
            },
        },
    }

    fluxo_config[7] = {
        'base': 'cueca',
        'fluxo_nome': 'Pijama',
        'produto': 'PIJAMA',
        'caracteristicas': [],
        'seta_pg_label': 'PG',
        'md_p_pb': False,
        'md_p_pg': False,
        'mdext1':  {
            'cabecalho': 'MD SAMBA - <b><u>M</u></b>999*<br />Fluxo 1',
        },
        'mdext2':  {
            'cabecalho': 'MD CAMISA - <b><u>M</u></b>999*<br />Fluxo 6',
        },
        'pb': False,
        'pg': {
            'cabecalho': 'PG - <b><u>A</u></b>999*<br />'
                         'Depósito da OP: 231<br /><br />'
                         'Kit',
            'ests': [3, 18, 60, 57, 63],
            'gargalo': 60,
            'insumos': {
                18: [
                    'Embalagem',
                    'Cartela',
                ],
                60: [
                    'MD SAMBA<br /><b><u>M</u></b>999*',
                    'MD CAMISA<br /><b><u>M</u></b>999*',
                ],
            },
        },
        'pa_de_md': {
            'cabecalho': 'Kit',
            'ests': [3, 18, 60, 57, 63, 66],
            'gargalo': 60,
            'insumos': {
                18: [
                    'Embalagem',
                    'Cartela',
                    'Etiquetas',
                    'Caixa',
                ],
                60: [
                    'MD SAMBA<br /><b><u>M</u></b>999*',
                    'MD CAMISA<br /><b><u>M</u></b>999*',
                ],
            }
        },
        'pa_enc_de_pb': False,
        'pa_emb_de_pg': {
            'cabecalho': 'Kit',
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                18: [
                    'Etiquetas',
                    'Caixa',
                ],
                66: ['PG<br /><b><u>A</u></b>999*'],
            }
        },
        'pa_enc_de_pg': False,
    }

    fluxo_config[8] = {
        'base': '1_bloco',
        'fluxo_nome': 'Parte',
        'produto': 'SUNGA (Forro)',
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

    fluxo_config[9] = {
        'base': 'cueca',
        'produto': 'MEIA',
        'fluxo_nome': 'Tecelagem de meia',
        'caracteristicas': [
            'Tecelagem: Interna',
        ],
        'seta_pg_label': 'PG',
        'md_p_pb': {
            'cabecalho': 'MD - <b><u>M</u></b>999*<br />'
                         'Depósito da OP: 231',
            'ests': [3, 22, 9, 27, 28, 51],
            'gargalo': 27,
            'insumos': {
                27: ['Fio', ],
            },
        },
        'md_p_pg': False,
        'pb': False,
        'pg': {
            'cabecalho': 'PG - <b><u>A</u></b>999*<br />'
                         'Depósito da OP: 231<br /><br />'
                         'Kit',
            'ests': [3, 18, 60, 48, 57, 63],
            'gargalo': 60,
            'insumos': {
                18: ['Etiquetas',
                     'TAG', ],
                60: ['MD<br /><b><u>M</u></b>999*', ],
            },
        },
        'pa_de_md': {
            'cabecalho': 'Kit',
            'ests': [3, 18, 60, 48, 57, 63, 66],
            'gargalo': 60,
            'insumos': {
                18: ['Etiquetas',
                     'TAG', ],
                60: ['MD<br /><b><u>M</u></b>999*'],
            }
        },
        'pa_enc_de_pb': False,
        'pa_emb_de_pg': {
            'cabecalho': 'Kit',
            'ests': [3, 18, 66],
            'gargalo': 66,
            'insumos': {
                66: ['PG<br /><b><u>A</u></b>999*'],
            }
        },
        'pa_enc_de_pg': False,
    }

    # 51
    fluxo_aux = {
        'produto': 'Não Tecelagem',
    }
    aux_blocos = [
        'md_p_pb', 'md_p_pg', 'pb', 'pg', 'pa_de_md', 'pa_enc_de_pb',
        'pa_emb_de_pg', 'pa_enc_de_pg',
    ]
    for aux_bloco in aux_blocos:
        fluxo_aux[aux_bloco] = {
            'ests': [e if e != 18 else 19
                     for e in fluxo_config[1][aux_bloco]['ests']],
            'insumos': {
                18: [],
                19: (fluxo_config[1][aux_bloco]['insumos'][18]
                     if 18 in fluxo_config[1][aux_bloco]['insumos'] else [])
            },
        }
    fluxo_config[51] = update_dict(fluxo_config[1], fluxo_aux)

    # 51p
    fluxo_aux = {
        'produto': 'SUNGA - SHORT',
        'tem_mp': True,
        'pg': False,
        'pa_emb_de_pg': False,
        'pa_enc_de_pg': False,
    }
    aux_blocos = [
        'md_p_pb', 'md_p_pg', 'pb', 'pa_de_md', 'pa_enc_de_pb',
    ]
    for aux_bloco in aux_blocos:
        if fluxo_config['1p'][aux_bloco]:
            fluxo_aux[aux_bloco] = {
                'ests': [e if e != 18 else 19
                         for e in fluxo_config['1p'][aux_bloco]['ests']],
                'insumos': {
                    18: [],
                    19: (fluxo_config['1p'][aux_bloco]['insumos'][18]
                         if 18 in fluxo_config['1p'][aux_bloco]['insumos']
                         else [])
                },
            }
    fluxo_config['51p'] = update_dict(fluxo_config['1p'], fluxo_aux)

    fluxo_config[52] = {
        'base': 'cueca',
        'produto': 'MULTIMARCA',
        'fluxo_nome': 'Sobra de multimarca',
        'caracteristicas': [],
        'seta_md_label': 'PPG',
        'seta_pa_label': 'PG',
        'md_cabecalho': 'PPG\nDepósito da OP: 231',
        'md_p_pb': {
            'cabecalho': '<b><u>D</u></b>999* - para Desmontar',
            'ests': [3, 57, 63],
            'gargalo': 57,
            'insumos': {
                57: ['MD<br /><b><u>M</u></b>999*', ],
            },
        },
        'md_p_pg': False,
        'pb': False,
        'pg': False,
        'pa_cabecalho': 'PG\nDepósito da OP: 231',
        'pa_de_md': {
            'cabecalho': '<b><u>A</u></b>999* - Remontado',
            'ests': [3, 18, 45, 48, 51, 60, 57, 63],
            'gargalo': 60,
            'insumos': {
                18: ['Cartela',
                     'Transfer',
                     'Etiquetas',
                     'TAG', ],
                60: ['PPG<br /><b><u>D</u></b>999*'],
            }
        },
        'pa_enc_de_pb': False,
        'pa_emb_de_pg': False,
        'pa_enc_de_pg': False,
    }

    if id not in fluxo_config:
        return None

    return update_dict(
        fluxo_padrao[fluxo_config[id]['base']], fluxo_config[id])


def dict_colecao_fluxos(colecao, tipo, ref):
    cf = {
        (1, 2, 3, 4, 13, 15, ): {
            ('pa', 'pg', 'pb', ): {'': [1, 2, 3, 51]},
            ('md', ): {'M': [1, 51],
                       'C': [2],
                       'R': [3],
                       },
        },
        (5, ): {
            ('md', ): {'M': [51],
                       'C': [6],
                       },
        },
        (6, ): {
            ('md', ): {'M': [51]}
        },
        (7, ): {
            ('pa', 'pg'): {'': [7, 51]},
        },
        (8, ): {
            ('pa', ): {'': [5, '51p']},
            ('pg', ): {'': [5]},
            ('md', ): {'M': ['51p'],
                       'C': [5],
                       'F': [8],
                       },
        },
        (9, 10, 11, 12, 16, 17, ): {
            ('pa', 'pg', 'pb', 'md', ): {'': [4]},
        },
        (18, ): {
            ('pa', ): {'': ['1p', '2p', 5, '51p']},
            ('pg', ): {'': ['1p', 5]},
            ('md', ): {'M': ['1p', '51p'],
                       'C': ['2p', 5],
                       },
        },
        (50, ): {
            ('md', ): {'V': [8]}
        },
    }

    col_id = None
    for col_tuple in cf:
        if colecao in col_tuple:
            col_id = col_tuple
            break
    if col_id is None:
        return []
    col_dict = cf[col_id]

    tipo_id = None
    for tipo_tuple in col_dict:
        if tipo in tipo_tuple:
            tipo_id = tipo_tuple
            break
    if tipo_id is None:
        return []
    tipo_dict = col_dict[tipo_id]

    inicio = ['']
    if tipo == 'md':
        inicio.insert(0, ref[0])

    for ini in inicio:
        if ini in tipo_dict:
            return tipo_dict[ini]

    return []


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


def get_roteiros_de_fluxo(id):
    fluxo = dict_fluxo(id)

    roteiros = {}
    fluxo_num = fluxo['fluxo_num']
    for k in fluxo:
        if isinstance(fluxo[k], dict):
            if 'ests' in fluxo[k]:
                if k == 'bloco':
                    tipo = fluxo[k]['nivel']
                else:
                    tipo = k[:2]
                if tipo == 'mp':
                    tipo = 'md'
                if tipo not in roteiros:
                    roteiros[tipo] = {}
                roteiros[tipo][fluxo_num+fluxo[k]['alt_incr']] = [
                    fluxo[k]['ests'],
                    fluxo[k]['gargalo'],
                ]
    return roteiros


def roteiros_de_fluxo(request, id):
    roteiros = get_roteiros_de_fluxo(id)
    return HttpResponse(
        pformat(roteiros, indent=4),
        content_type='text/plain')


def unidade(request):
    cursor = connections['so'].cursor()
    sql = '''
        SELECT
          di.DIVISAO_PRODUCAO DIV
        , di.DESCRICAO DESCR
        , ci.ESTADO UF
        , ci.CIDADE
        , ' (' || lpad(fo.FORNECEDOR9, 8, '0')
          || '/' || lpad(fo.FORNECEDOR4, 4, '0')
          || '-' || lpad(fo.FORNECEDOR2, 2, '0')
          || ') '
          || fo.NOME_FORNECEDOR NOME
        FROM BASI_180 di -- divisão / unidade
        JOIN SUPR_010 fo -- fornacedor
          ON fo.FORNECEDOR9 = di.FACCIONISTA9
         AND fo.FORNECEDOR4 = di.FACCIONISTA4
         AND fo.FORNECEDOR2 = di.FACCIONISTA2
        JOIN BASI_160 ci -- cidade
          ON ci.COD_CIDADE = fo.COD_CIDADE
        WHERE di.DIVISAO_PRODUCAO > 1
          AND di.DIVISAO_PRODUCAO < 1000
        ORDER BY
          di.DIVISAO_PRODUCAO
    '''
    cursor.execute(sql)
    data = rows_to_dict_list(cursor)
    context = {
        'titulo': 'Unidades / Divisões',
        'headers': ('Código ', 'Descrição', 'UF', 'Cidade',
                    '(CNPJ) Razão social'),
        'fields': ('DIV', 'DESCR', 'UF', 'CIDADE',
                   'NOME'),
        'data': data,
    }
    return render(request, 'geral/unidade.html', context)
