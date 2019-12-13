import datetime
import time
import hashlib
from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.shortcuts import redirect
from django.core.exceptions import SuspiciousOperation

from utils.views import totalize_data, totalize_grouped_data, TableHfs
from fo2.template import group_rowspan
from geral.functions import request_user, has_permission

from . import forms
from . import models


def index(request):
    context = {}
    return render(request, 'estoque/index.html', context)


class PorDeposito(View):
    Form_class = forms.PorDepositoForm
    template_name = 'estoque/posicao_estoque.html'
    title_name = 'Posição de estoque'

    def mount_context(
            self, cursor, nivel, ref, tam, cor, deposito, agrupamento, tipo):
        context = {
            'nivel': nivel,
            'tam': tam,
            'cor': cor,
            'deposito': deposito,
            'agrupamento': agrupamento,
            'tipo': tipo,
            }
        modelo = None
        if len(ref) % 5 == 0:
            context.update({
                'ref': ref,
            })
        else:
            modelo = ref.lstrip("0")
            ref = ''
            context.update({
                'modelo': modelo,
            })
        if agrupamento == 'rct':
            group = ''
        else:
            group = agrupamento
        data = models.posicao_estoque(
            cursor, nivel, ref, tam, cor, deposito, zerados=False, group=group,
            tipo=tipo, modelo=modelo)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        if agrupamento == 'r':
            totalize_data(data, {
                'sum': ['qtd_positiva', 'qtd_negativa'],
                'count': [],
                'descr': {'dep_descr': 'Totais:'},
                'row_style': 'font-weight: bold;',
            })
            soma = data[-1]['qtd_positiva'] + data[-1]['qtd_negativa']
            context.update({
                'headers': ('Nível', 'Referência', 'Depósito',
                            'Quantidades Positivas', 'Quantidades Negativas'),
                'fields': ('cditem_nivel99', 'cditem_grupo', 'dep_descr',
                           'qtd_positiva', 'qtd_negativa'),
                'style': {4: 'text-align: right;',
                          5: 'text-align: right;'},
                'soma': soma,
            })
        elif agrupamento == 'tc':
            totalize_data(data, {
                'sum': ['qtd_positiva', 'qtd_negativa'],
                'count': [],
                'descr': {'cditem_item': 'Totais:'},
                'row_style': 'font-weight: bold;',
            })
            soma = data[-1]['qtd_positiva'] + data[-1]['qtd_negativa']
            context.update({
                'headers': ('Nível', 'Tamanho', 'Cor',
                            'Quantidades Positivas', 'Quantidades Negativas'),
                'fields': ('cditem_nivel99', 'cditem_subgrupo', 'cditem_item',
                           'qtd_positiva', 'qtd_negativa'),
                'style': {4: 'text-align: right;',
                          5: 'text-align: right;'},
                'soma': soma,
            })
        else:
            totalize_data(data, {
                'sum': ['qtd'],
                'count': [],
                'descr': {'dep_descr': 'Total:'},
                'row_style': 'font-weight: bold;',
            })
            context.update({
                'headers': ('Nível', 'Referência', 'Tamanho',
                            'Cor', 'Depósito', 'Quantidade'),
                'fields': ('cditem_nivel99', 'cditem_grupo', 'cditem_subgrupo',
                           'cditem_item', 'dep_descr', 'qtd'),
                'style': {6: 'text-align: right;'},
            })
        context.update({
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            nivel = form.cleaned_data['nivel']
            ref = form.cleaned_data['ref']
            tam = form.cleaned_data['tam']
            cor = form.cleaned_data['cor']
            deposito = form.cleaned_data['deposito']
            agrupamento = form.cleaned_data['agrupamento']
            tipo = form.cleaned_data['tipo']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, nivel, ref, tam, cor, deposito, agrupamento, tipo))
        context['form'] = form
        return render(request, self.template_name, context)


class ValorMp(View):
    Form_class = forms.ValorForm
    template_name = 'estoque/valor_mp.html'
    title_name = 'Valor de estoque'

    def mount_context(
            self, cursor, nivel, positivos, zerados, negativos, preco_zerado,
            deposito_compras):
        context = {
            'nivel': nivel,
            'positivos': positivos,
            'zerados': zerados,
            'negativos': negativos,
            'preco_zerado': preco_zerado,
            'deposito_compras': deposito_compras,
        }

        data = models.valor(
            cursor, nivel, positivos, zerados, negativos, preco_zerado,
            deposito_compras)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        totalize_grouped_data(data, {
            'group': ['nivel'],
            'sum': ['total'],
            'count': [],
            'descr': {'deposito': 'Total:'}
        })

        for row in data:
            row['qtd|DECIMALS'] = 2
            row['preco|DECIMALS'] = 2
            row['total|DECIMALS'] = 2

        context.update({
            'headers': ('Nível', 'Referência', 'Tamanho', 'Cor',
                        'Conta estoque', 'Depósito',
                        'Quantidade', 'Preço', 'Total'),
            'fields': ('nivel', 'ref', 'tam', 'cor',
                       'conta_estoque', 'deposito',
                       'qtd', 'preco', 'total'),
            'style': {
                7: 'text-align: right;',
                8: 'text-align: right;',
                9: 'text-align: right;',
            },
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            nivel = form.cleaned_data['nivel']
            positivos = form.cleaned_data['positivos']
            zerados = form.cleaned_data['zerados']
            negativos = form.cleaned_data['negativos']
            preco_zerado = form.cleaned_data['preco_zerado']
            deposito_compras = form.cleaned_data['deposito_compras']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, nivel, positivos, zerados, negativos, preco_zerado,
                deposito_compras))
        context['form'] = form
        return render(request, self.template_name, context)


class InventarioExpedicao(View):
    Form_class = forms.InventarioExpedicaoForm
    template_name = 'estoque/inventario_expedicao.html'
    title_name = 'Inventário p/ expedição'

    def mount_context(self, cursor, data_ini):
        context = {
            'data_ini': data_ini,
        }

        refs = models.refs_com_movimento(cursor, data_ini)
        if len(refs) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        deps = [231, 101, 102]
        for ref in refs:
            ref['deps'] = []
            for dep in deps:
                header, fields, data, style, total = \
                    models.grade_estoque(
                        cursor, ref['ref'], dep, data_ini=data_ini)
                grade = None
                if total != 0:
                    grade = {
                        'headers': header,
                        'fields': fields,
                        'data': data,
                        'style': style,
                    }
                    ref['deps'].append({
                        'dep': dep,
                        'grade': grade,
                    })

        context.update({
            'headers': ['Referência'],
            'fields': ['ref'],
            'refs': refs,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            data_ini = form.cleaned_data['data_ini']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, data_ini))
        context['form'] = form
        return render(request, self.template_name, context)


class ReferenciaDeposito(View):
    Form_class = forms.ReferenciasEstoqueForm
    template_name = 'estoque/referencia_deposito.html'
    title_name = 'Por referência em depósito'

    def mount_context(self, request, cursor, deposito, modelo):
        context = {
            'modelo': modelo,
            'permission': has_permission(
                request, 'base.can_adjust_stock'),
        }

        data = models.referencia_deposito(cursor, deposito, modelo)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        if has_permission(request, 'base.can_adjust_stock'):
            for row in data:
                row['ref|TARGET'] = '_blank'
                row['ref|LINK'] = reverse(
                    'estoque:mostra_estoque__get', args=[
                        row['dep'], row['ref']])

        group = ['dep']
        tot_conf = {
            'group': group,
            'sum': ['estoque', 'falta', 'soma'],
            'count': [],
            'descr': {'ref': 'Totais:'},
        }
        if deposito == '-':
            tot_conf.update({
                'global_sum': ['estoque', 'falta', 'soma'],
                'global_descr': {'ref': 'Totais gerais:'},
            })
        totalize_grouped_data(data, tot_conf)
        group_rowspan(data, group)

        context.update({
            'headers': ['Depósito', 'Referência', 'Estoque', 'Falta', 'Soma'],
            'fields': ['dep', 'ref', 'estoque', 'falta', 'soma'],
            'group': group,
            'data': data,
            'style': {
                3: 'text-align: right;',
                4: 'text-align: right;',
                5: 'text-align: right;',
            },
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            deposito = form.cleaned_data['deposito']
            modelo = form.cleaned_data['modelo']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                request, cursor, deposito, modelo))
        context['form'] = form
        return render(request, self.template_name, context)


class MostraEstoque(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'base.can_adjust_stock'
        self.Form_class = forms.MostraEstoqueForm
        self.template_name = 'estoque/mostra_estoque.html'
        self.title_name = 'Ajuste de estoque'
        self.table = TableHfs({
            'cor': {
                'header': 'Cor',
            },
            'tam': {
                'header': 'Tamanho',
            },
            'qtd': {
                'header': 'Estoque atual',
                'style': 'text-align: right;',
            },
            'qtd_inv': {
                'header': 'Estoque na data',
                'style': 'text-align: right;',
            },
            'movimento': {
                'header': 'Movimento',
                'style': 'text-align: right;',
            },
            'ajuste': {
                'header': 'Ajuste pelo inventário',
                'style': 'text-align: right;',
            },
            'executa': {
                'header': 'Executa',
            },
            'edita': {
                'header': 'Edita',
            },
        })

    def mount_context(self, request, cursor, deposito, ref, qtd, idata, hora):
        try:
            qtd = int(qtd)
        except Exception:
            qtd = None
        context = {
            'deposito': deposito,
            'ref': ref,
            'qtd': qtd,
            'idata': idata,
            'hora': hora,
        }

        data = models.estoque_deposito_ref(cursor, deposito, ref)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        for row in data:
            movimento = 0
            ajuste = 0
            if idata is not None:
                d_tot_movi = models.trans_fo2_deposito_ref(
                    cursor, deposito, ref, row['cor'], row['tam'],
                    tipo='s', data=idata, hora=hora)
                if len(d_tot_movi) != 0:
                    for d_row in d_tot_movi:
                        if d_row['es'] == 'E':
                            movimento += d_row['qtd']
                        elif d_row['es'] == 'S':
                            movimento -= d_row['qtd']
                if qtd is not None:
                    ajuste = qtd - row['qtd'] + movimento
            row['movimento'] = movimento
            row['qtd_inv'] = row['qtd'] - movimento
            row['ajuste'] = ajuste

        edita_pos = 999
        self.table.cols('cor', 'tam')
        if idata is None:
            self.table.add('qtd')
        else:
            self.table.add('qtd_inv', 'movimento', 'qtd')
            if qtd is not None:
                self.table.add('ajuste')
                edita_pos = -1

        if has_permission(request, 'base.can_adjust_stock'):
            self.table.add(edita_pos, 'edita')
            if idata is not None and qtd is not None:
                self.table.add('executa')
            for row in data:
                movimento = 0
                if idata is not None:
                    d_tot_movi = models.trans_fo2_deposito_ref(
                        cursor, deposito, ref, row['cor'], row['tam'],
                        tipo='s', data=idata, hora=hora)
                    if len(d_tot_movi) != 0:
                        for d_row in d_tot_movi:
                            if d_row['es'] == 'E':
                                movimento += d_row['qtd']
                            elif d_row['es'] == 'S':
                                movimento -= d_row['qtd']
                row['movimento'] = movimento
                row['qtd_inv'] = row['qtd'] - movimento
                row['edita'] = 'Edita'
                row['edita|LINK'] = reverse(
                    'estoque:edita_estoque__get', args=[
                        deposito, ref, row['cor'], row['tam']])
                if row['qtd'] == 0:
                    row['zera'] = '-'
                else:
                    row['zera'] = 'Zera'
                    row['zera|LINK'] = reverse(
                        'estoque:zera_estoque__get', args=[
                            deposito, ref, row['cor'], row['tam']])
                if idata is not None and qtd is not None:
                    if row['ajuste'] == 0:
                        row['executa'] = '-'
                    else:
                        trail = hash_trail(
                            request,
                            deposito,
                            ref,
                            row['cor'],
                            row['tam'],
                            row['ajuste'],
                        )
                        row['executa'] = '''
                            <a title="Executa ajuste indicado pelo inventário"
                             class="btn btn-primary"
                             style="padding: 0px 12px;"
                             href="javascript:void(0);"
                             onclick="exec_ajuste(this,
                                \'{dep}\', \'{ref}\', \'{cor}\', \'{tam}\',
                                \'{ajuste}\', \'{trail}\');"
                            >Ajusta</a>
                        '''.format(
                            dep=deposito,
                            ref=ref,
                            cor=row['cor'],
                            tam=row['tam'],
                            ajuste=row['ajuste'],
                            trail=trail)

        headers, fields, style = self.table.hfs()
        context.update({
            'safe': ['executa'],
            'headers': headers,
            'fields': fields,
            'data': data,
            'style': style,
        })

        data = models.trans_fo2_deposito_ref(cursor, deposito, ref)
        if len(data) != 0:
            context.update({
                't_headers': ['Data/hora', 'Documento', 'Cor', 'Tamanho',
                              'Transação', 'E/S', 'Quantidade'],
                't_fields': ['hora', 'numdoc', 'cor', 'tam',
                             'trans', 'es', 'qtd'],
                't_data': data,
                't_style': {7: 'text-align: right;', },
            })
        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}

        get_data_inv = None
        idata = None
        if 'ajuste_inv_data' in request.COOKIES:
            get_data_inv = request.COOKIES.get('ajuste_inv_data')
        if get_data_inv is None:
            self.form = self.Form_class()
        else:
            self.form = self.Form_class(initial={"data": get_data_inv})
            idata = datetime.datetime.strptime(get_data_inv, '%Y-%m-%d').date()

        deposito = kwargs['deposito']
        ref = kwargs['ref']
        cursor = connections['so'].cursor()
        context.update(self.mount_context(
            request, cursor, deposito, ref, None, idata, None))

        context['form'] = self.form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        self.form = self.Form_class(request.POST)

        deposito = kwargs['deposito']
        ref = kwargs['ref']

        set_data_inv = None
        if self.form.is_valid():
            qtd = self.form.cleaned_data['qtd']
            data = self.form.cleaned_data['data']
            hora = self.form.cleaned_data['hora']
            set_data_inv = data
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                request, cursor, deposito, ref, qtd, data, hora))

        context['form'] = self.form
        response = render(request, self.template_name, context)
        if set_data_inv is None:
            response.delete_cookie('ajuste_inv_data')
        else:
            response.set_cookie('ajuste_inv_data', set_data_inv)
        return response


class TransacoesDeAjuste():

    def __init__(self):
        self.transacoes = {
            1: {
                'codigo': 105,
                'es': 'E',
                'descr': 'Entrada por inventário',
            },
            -1: {
                'codigo': 3,
                'es': 'S',
                'descr': 'Saída por inventário',
            },
        }

    def get(self, sinal):
        trans = self.transacoes[sinal]['codigo']
        es = self.transacoes[sinal]['es']
        descr = self.transacoes[sinal]['descr']
        return trans, es, descr


class ZeraEstoque(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'base.can_adjust_stock'
        self.template_name = 'estoque/zera_estoque.html'
        self.title_name = 'Ajuste de estoque'

        self.transacoes = TransacoesDeAjuste()

    def mount_context(
            self, cursor, deposito, ref, cor, tam, qtd, conf_hash, trail):
        context = {
            'deposito': deposito,
            'ref': ref,
            'cor': cor,
            'tam': tam,
        }
        executa = conf_hash is not None

        produto = models.get_preco_medio_ref_cor_tam(cursor, ref, cor, tam)
        if len(produto) == 0:
            context.update({
                'mensagem': 'Referência/Cor/Tamanho não encontrada',
            })
            return context
        preco_medio = produto[0]['preco_medio']

        l_estoque = models.get_estoque_dep_ref_cor_tam(
            cursor, deposito, ref, cor, tam)
        if len(l_estoque) == 0:
            estoque = 0
        else:
            estoque = l_estoque[0]['estoque']
        ajuste = qtd - estoque
        if ajuste == 0:
            context.update({
                'mensagem': 'O depósito já está com a quantidade desejada',
            })
            return context
        sinal = 1 if ajuste > 0 else -1
        ajuste *= sinal

        context.update({
            'qtd': qtd,
            'estoque': estoque,
        })

        trans, es, descr = self.transacoes.get(sinal)

        if executa:
            num_doc = '702{}'.format(time.strftime('%y%m%d'))
            if models.insert_transacao_ajuste(
                    cursor, deposito, ref, tam, cor, num_doc, trans, es,
                    ajuste, preco_medio):
                context.update({
                    'estoque': qtd,
                })
                mensagem = \
                    "Foi executada a transação '{:03}' ({}) " \
                    "com a quantidade {}."
            else:
                mensagem = \
                    "Erro ao executar a transação '{:03}' ({}) " \
                    "com a quantidade {}."
        else:
            context.update({
                'trail': trail,
            })
            mensagem = \
                "Deve ser executada a transação '{:03}' ({}) " \
                "com a quantidade {}."
        mensagem = mensagem.format(trans, descr, ajuste)
        context.update({
            'mensagem': mensagem,
        })
        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        if 'qtd' in kwargs:
            qtd = int(kwargs['qtd'])
        else:
            qtd = 0

        deposito = kwargs['deposito']
        ref = kwargs['ref']
        cor = kwargs['cor']
        tam = kwargs['tam']

        hash_cache = ';'.join(map(format, (
            deposito,
            ref,
            cor,
            tam,
            qtd,
            time.strftime('%y%m%d'),
            request_user(request),
        )))
        hash_object = hashlib.md5(hash_cache.encode())
        trail = hash_object.hexdigest()

        if 'conf_hash' in kwargs:
            conf_hash = kwargs['conf_hash']
            if trail != conf_hash:
                return redirect('apoio_ao_erp')
        else:
            conf_hash = None
        cursor = connections['so'].cursor()
        context.update(self.mount_context(
            cursor, deposito, ref, cor, tam, qtd, conf_hash, trail))
        return render(request, self.template_name, context)


class EditaEstoque(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'base.can_adjust_stock'
        self.Form_class = forms.EditaEstoqueForm
        self.template_name = 'estoque/edita_estoque.html'
        self.title_name = 'Ajuste de estoque'

        self.transacoes = TransacoesDeAjuste()

    def start(self):
        self.context = {'titulo': self.title_name}
        self.cursor = connections['so'].cursor()

    def pre_mount_context(self, request, **kwargs):
        self.request = request

        self.deposito = kwargs['deposito']
        self.ref = kwargs['ref']
        self.cor = kwargs['cor']
        self.tam = kwargs['tam']
        self.qtd = kwargs['qtd']
        self.data = kwargs['data']
        self.hora = kwargs['hora']

        produto = models.get_preco_medio_ref_cor_tam(
            self.cursor, self.ref, self.cor, self.tam)
        if len(produto) == 0:
            raise SuspiciousOperation('produto')

        self.preco_medio = produto[0]['preco_medio']

        l_estoque = models.get_estoque_dep_ref_cor_tam(
            self.cursor, self.deposito, self.ref, self.cor, self.tam)
        if len(l_estoque) == 0:
            self.estoque = 0
        else:
            self.estoque = l_estoque[0]['estoque']

        self.movimento = 0
        if self.data is not None:
            d_tot_movi = models.trans_fo2_deposito_ref(
                self.cursor, self.deposito, self.ref, self.cor, self.tam,
                tipo='s', data=self.data, hora=self.hora)
            if len(d_tot_movi) != 0:
                for row in d_tot_movi:
                    if row['es'] == 'E':
                        self.movimento += row['qtd']
                    elif row['es'] == 'S':
                        self.movimento -= row['qtd']

        anterior = {}
        posterior = {}
        get_prox = False
        lista = models.estoque_deposito_ref(
            self.cursor, self.deposito, self.ref)
        for row in lista:
            item = '{}.{}'.format(
                row['tam'],
                row['cor'],
            )
            if get_prox:
                posterior['item'] = item
                posterior['cor'] = row['cor']
                posterior['tam'] = row['tam']
                break
            else:
                if self.cor == row['cor'] and self.tam == row['tam']:
                    get_prox = True
                else:
                    anterior['item'] = item
                    anterior['cor'] = row['cor']
                    anterior['tam'] = row['tam']

        self.context.update({
            'deposito': self.deposito,
            'ref': self.ref,
            'cor': self.cor,
            'tam': self.tam,
            'estoque': self.estoque,
            'movimento': self.movimento,
            'movimento_neg': -self.movimento,
            'qtd': self.qtd,
            'data': self.data,
            'hora': self.hora,
            'anterior': anterior,
            'posterior': posterior,
        })

        try:
            self.qtd = int(self.qtd)
        except Exception:
            self.qtd = None
        if self.qtd is not None:
            self.ajuste = self.qtd - self.estoque + self.movimento
            if self.ajuste == 0:
                raise SuspiciousOperation('estoque ok')

            self.sinal = 1 if self.ajuste > 0 else -1
            self.ajuste *= self.sinal

            self.trans, self.es, self.descr = self.transacoes.get(self.sinal)

            hash_cache = ';'.join(map(format, (
                self.deposito,
                self.ref,
                self.cor,
                self.tam,
                self.qtd,
                time.strftime('%y%m%d'),
                request_user(self.request),
                self.request.session.session_key,
            )))
            hash_object = hashlib.md5(hash_cache.encode())
            self.trail = hash_object.hexdigest()

            if 'conf_hash' in kwargs:
                self.conf_hash = kwargs['conf_hash']
                if self.trail != self.conf_hash:
                    raise SuspiciousOperation('conf_hash')
            else:
                self.conf_hash = None
            self.executa = self.conf_hash is not None

            if self.executa:
                num_doc = '702{}'.format(time.strftime('%y%m%d'))
                if models.insert_transacao_ajuste(
                        self.cursor,
                        self.deposito,
                        self.ref,
                        self.tam,
                        self.cor,
                        num_doc,
                        self.trans,
                        self.es,
                        self.ajuste,
                        self.preco_medio
                        ):
                    self.context.update({
                        'estoque': self.qtd + self.movimento,
                    })
                    mensagem = \
                        "Foi executada a transação '{:03}' ({}) " \
                        "com a quantidade {}."
                else:
                    mensagem = \
                        "Erro ao executar a transação '{:03}' ({}) " \
                        "com a quantidade {}."
            else:
                self.context.update({
                    'trail': self.trail,
                })
                mensagem = \
                    "Deve ser executada a transação '{:03}' ({}) " \
                    "com a quantidade {}."
            mensagem = mensagem.format(self.trans, self.descr, self.ajuste)
            self.context.update({
                'mensagem': mensagem,
            })

    def mount_context(self, request, **kwargs):
        try:
            self.pre_mount_context(request, **kwargs)
        except SuspiciousOperation as e:
            if e.args[0] == 'produto':
                self.context.update({
                    'mensagem': 'Referência/Cor/Tamanho não encontrada',
                })
            elif e.args[0] == 'estoque ok':
                self.context.update({
                    'mensagem':
                        'O depósito já está com a quantidade desejada',
                })
            else:
                return False
        return True

    def get(self, request, *args, **kwargs):
        self.start()

        get_data_inv = None
        if 'ajuste_inv_data' in request.COOKIES:
            get_data_inv = request.COOKIES.get('ajuste_inv_data')
        if get_data_inv is None:
            self.form = self.Form_class()
        else:
            self.form = self.Form_class(initial={"data": get_data_inv})

        if 'qtd' in kwargs:
            if get_data_inv is not None:
                kwargs['data'] = get_data_inv
            return self.post(request, *args, **kwargs)
        else:
            kwargs['qtd'] = None
            kwargs['data'] = None
            kwargs['hora'] = None

        if not self.mount_context(request, **kwargs):
            return redirect('apoio_ao_erp')

        self.context['form'] = self.form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.start()
        self.form = self.Form_class(request.POST)

        if 'qtd' in kwargs:
            self.form.data['qtd'] = kwargs['qtd']
        if 'data' in kwargs:
            self.form.data['data'] = kwargs['data']

        set_data_inv = None
        if self.form.is_valid():
            qtd = self.form.cleaned_data['qtd']
            data = self.form.cleaned_data['data']
            hora = self.form.cleaned_data['hora']
            kwargs['qtd'] = qtd
            kwargs['data'] = data
            kwargs['hora'] = hora
            set_data_inv = data
            if not self.mount_context(request, **kwargs):
                return redirect('apoio_ao_erp')

        self.context['form'] = self.form
        response = render(request, self.template_name, self.context)
        if set_data_inv is None:
            response.delete_cookie('ajuste_inv_data')
        else:
            response.set_cookie('ajuste_inv_data', set_data_inv)
        return response


def hash_trail(request, *fields):
    params = list(fields) + [
        time.strftime('%y%m%d'),
        request_user(request),
        request.session.session_key,
    ]
    hash_cache = ';'.join(map(format, params))
    hash_object = hashlib.md5(hash_cache.encode())
    return hash_object.hexdigest()


@permission_required('base.can_adjust_stock')
def executa_ajuste(request, **kwargs):
    data = {}

    dep = kwargs['dep']
    ref = kwargs['ref']
    cor = kwargs['cor']
    tam = kwargs['tam']
    ajuste = kwargs['ajuste']
    trail = kwargs['trail']

    if dep not in ['101', '102', '231']:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Depósito inválido',
        })
        return JsonResponse(data, safe=False)

    try:
        ajuste = int(ajuste)
        _ = 1 / ajuste  # erro, se zero
    except Exception:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Quantidade inválida para transação',
        })
        return JsonResponse(data, safe=False)

    cursor = connections['so'].cursor()

    produto = models.get_preco_medio_ref_cor_tam(
        cursor, ref, cor, tam)
    try:
        preco_medio = produto[0]['preco_medio']
    except Exception:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Referência/Cor/Tamanho não encontrada',
        })
        return JsonResponse(data, safe=False)

    sinal = 1 if ajuste > 0 else -1
    transacoes = TransacoesDeAjuste()
    trans, es, descr = transacoes.get(sinal)

    trail_check = hash_trail(
        request,
        dep,
        ref,
        cor,
        tam,
        ajuste,
    )
    if trail != trail_check:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Trail hash inválido',
            # 'trail_check': trail_check,
        })
        return JsonResponse(data, safe=False)

    num_doc = '702{}'.format(time.strftime('%y%m%d'))
    quant = ajuste * sinal
    if models.insert_transacao_ajuste(
            cursor,
            dep,
            ref,
            tam,
            cor,
            num_doc,
            trans,
            es,
            quant,
            preco_medio
            ):
        data.update({
            'result': 'OK',
            'descricao_erro': "Foi executada a transação '{:03}' ({}) "
                              "com a quantidade {}.".format(
                                trans,
                                es,
                                quant,
                              ),
        })
    else:
        data.update({
            'result': 'ERR',
            'descricao_erro': "Erro ao executar a transação '{:03}' ({}) "
                              "com a quantidade {}.".format(
                                trans,
                                es,
                                quant,
                              ),
        })

    return JsonResponse(data, safe=False)
