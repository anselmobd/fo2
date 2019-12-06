import time
import hashlib
from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.views import View
from django.urls import reverse
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.core.exceptions import SuspiciousOperation

from utils.views import totalize_data, totalize_grouped_data
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
    title_name = 'Ajuste de estoque'

    def mount_context(self, cursor, modelo):
        context = {
            'modelo': modelo,
        }

        data = models.referencia_deposito(cursor, modelo)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        for row in data:
            row['dep|TARGET'] = '_blank'
            row['dep|LINK'] = reverse(
                'estoque:edita_estoque__get', args=[
                    row['dep'], row['ref']])
        context.update({
            'headers': ['Referência', 'Depósito'],
            'fields': ['ref', 'dep'],
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
            modelo = form.cleaned_data['modelo']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, modelo))
        context['form'] = form
        return render(request, self.template_name, context)


class EditaEstoque(View):
    template_name = 'estoque/edita_estoque.html'
    title_name = 'Ajuste de estoque'

    def mount_context(self, request, cursor, deposito, ref):
        context = {
            'deposito': deposito,
            'ref': ref,
        }

        data = models.estoque_deposito_ref(cursor, deposito, ref)
        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        headers = ['Cor', 'Tamanho', 'Quant. total']
        fields = ['cor', 'tam', 'qtd']
        style = {
            3: 'text-align: right;',
        }

        if has_permission(request, 'base.can_adjust_stock'):
            headers = ['Cor', 'Tamanho', 'Zera', 'Quant. total', 'Edita']
            fields = ['cor', 'tam', 'zera', 'qtd', 'edita']
            style = {
                4: 'text-align: right;',
            }
            for row in data:
                row['edita'] = 'Edita'
                row['edita|LINK'] = reverse(
                    'estoque:ajusta_estoque__get', args=[
                        deposito, ref, row['cor'], row['tam']])
                if row['qtd'] == 0:
                    row['zera'] = '-'
                else:
                    row['zera'] = 'Zera'
                    row['zera|LINK'] = reverse(
                        'estoque:zera_estoque__get', args=[
                            deposito, ref, row['cor'], row['tam']])
        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'style': style,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        if 'deposito' in kwargs and 'ref' in kwargs:
            deposito = kwargs['deposito']
            ref = kwargs['ref']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(request, cursor, deposito, ref))
        return render(request, self.template_name, context)


class ZeraEstoque(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'base.can_adjust_stock'
        self.template_name = 'estoque/zera_estoque.html'
        self.title_name = 'Ajuste de estoque'

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

    def mount_context(
            self, cursor, deposito, ref, cor, tam, qtd, conf_hash, trail):
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

        context = {
            'deposito': deposito,
            'ref': ref,
            'cor': cor,
            'tam': tam,
            'qtd': qtd,
            'estoque': estoque,
        }

        trans = self.transacoes[sinal]['codigo']
        es = self.transacoes[sinal]['es']
        descr = self.transacoes[sinal]['descr']

        num_doc = '702{}'.format(time.strftime('%y%m%d'))

        if executa:
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
        self.Form_class = forms.AjustaEstoqueForm
        self.template_name = 'estoque/ajusta_estoque.html'
        self.title_name = 'Ajuste de estoque'

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

    def pre_mount_context(self, request, **kwargs):
        self.context = {'titulo': self.title_name}
        self.form = self.Form_class()
        self.cursor = connections['so'].cursor()

        self.request = request

        self.deposito = kwargs['deposito']
        self.ref = kwargs['ref']
        self.cor = kwargs['cor']
        self.tam = kwargs['tam']
        # self.qtd = kwargs['qtd']
        #
        # # a possibilidade de ValueError Exception
        # # é tratada por quem chama este método
        # self.qtd = int(self.qtd)

        produto = models.get_preco_medio_ref_cor_tam(
            self.cursor, self.ref, self.cor, self.tam)
        if len(produto) == 0:
            raise SuspiciousOperation('produto')

        self.preco_medio = produto[0]['preco_medio']

        # l_estoque = models.get_estoque_dep_ref_cor_tam(
        #     self.cursor, self.deposito, self.ref, self.cor, self.tam)
        # if len(l_estoque) == 0:
        #     self.estoque = 0
        # else:
        #     self.estoque = l_estoque[0]['estoque']
        #
        # self.ajuste = self.qtd - self.estoque
        # if self.ajuste == 0:
        #     raise SuspiciousOperation('estoque ok')
        #
        # self.sinal = 1 if self.ajuste > 0 else -1
        # self.ajuste *= self.sinal
        #
        # self.trans = self.transacoes[self.sinal]['codigo']
        # self.es = self.transacoes[self.sinal]['es']
        # self.descr = self.transacoes[self.sinal]['descr']
        #
        # hash_cache = ';'.join(map(format, (
        #     self.deposito,
        #     self.ref,
        #     self.cor,
        #     self.tam,
        #     self.qtd,
        #     time.strftime('%y%m%d'),
        #     request_user(self.request),
        #     self.request.session.session_key,
        # )))
        # hash_object = hashlib.md5(hash_cache.encode())
        # self.trail = hash_object.hexdigest()
        #
        # if 'conf_hash' in kwargs:
        #     self.conf_hash = kwargs['conf_hash']
        #     if self.trail != self.conf_hash:
        #         raise SuspiciousOperation('conf_hash')
        # else:
        #     self.conf_hash = None
        # self.executa = self.conf_hash is not None

        self.context.update({
            'deposito': self.deposito,
            'ref': self.ref,
            'cor': self.cor,
            'tam': self.tam,
            # 'qtd': self.qtd,
            # 'estoque': self.estoque,
        })

    def get(self, request, *args, **kwargs):
        try:
            self.pre_mount_context(request, **kwargs)
        except (SuspiciousOperation, ValueError) as e:
            if isinstance(e, ValueError):
                print('self.post(request, *args, **kwargs)')
            else:
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
                    return redirect('apoio_ao_erp')

        # self.context.update(self.mount_context())
        return render(request, self.template_name, self.context)
