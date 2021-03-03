import hashlib
import time
from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import redirect, render
from django.views import View

from fo2.connections import db_cursor_so

from geral.functions import request_user
from utils.functions import get_client_ip

import estoque.classes
from estoque import forms, queries
from estoque.functions import transfo2_num_doc, transfo2_num_doc_dt


class EditaEstoque(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'base.can_adjust_stock'
        self.Form_class = forms.EditaEstoqueForm
        self.template_name = 'estoque/edita_estoque.html'
        self.title_name = 'Ajuste de estoque'

        self.transacoes = estoque.classes.TransacoesDeAjuste()

    def start(self):
        self.context = {'titulo': self.title_name}
        self.cursor = db_cursor_so(self.request)

    def pre_mount_context(self, request, **kwargs):
        self.request = request

        self.deposito = kwargs['deposito']
        self.ref = kwargs['ref']
        self.cor = kwargs['cor']
        self.tam = kwargs['tam']
        self.qtd = kwargs['qtd']
        self.data = kwargs['data']
        self.hora = kwargs['hora']

        produto = queries.get_preco_medio_ref_cor_tam(
            self.cursor, self.ref, self.cor, self.tam)
        if len(produto) == 0:
            raise SuspiciousOperation('produto')

        self.preco_medio = produto[0]['preco_medio']

        l_estoque = queries.get_estoque_dep_ref_cor_tam(
            self.cursor, self.deposito, self.ref, self.cor, self.tam)
        if len(l_estoque) == 0:
            self.estoque = 0
        else:
            self.estoque = l_estoque[0]['estoque']

        self.movimento = 0
        if self.data is not None:
            d_tot_movi = queries.get_transfo2_deposito_ref(
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
        lista = queries.estoque_deposito_ref_modelo(
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

        num_doc = transfo2_num_doc(self.data, self.hora)
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
            'num_doc': num_doc,
            'anterior': anterior,
            'posterior': posterior,
        })

        transfs = queries.get_transfo2(
            self.cursor, self.deposito,
            ref=self.ref, cor=self.cor, tam=self.tam)
        if len(transfs) != 0:
            ult_num_doc = transfs[0]['numdoc']
            if int(num_doc) < ult_num_doc:
                ult_dt = transfo2_num_doc_dt(ult_num_doc)
                raise SuspiciousOperation(
                    'data inventario',
                    'Data/Hora não pode ser anterior ao do último '
                    'inventário ({}: {})'.format(ult_num_doc, ult_dt))

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
                if queries.insert_transacao_ajuste(
                        self.cursor,
                        self.deposito,
                        self.ref,
                        self.tam,
                        self.cor,
                        num_doc,
                        self.trans,
                        self.es,
                        self.ajuste,
                        self.preco_medio,
                        self.request.user,
                        get_client_ip(self.request)
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
            elif e.args[0] == 'conf_hash':
                self.context.update({
                    'mensagem':
                        'Hash informado inválido',
                })
            elif e.args[0] == 'data inventario':
                self.context.update({
                    'mensagem': e.args[1],
                })
            else:
                return False
        return True

    def get(self, request, *args, **kwargs):
        self.request = request
        self.start()

        get_data_inv = None
        if 'ajuste_inv_data' in request.COOKIES:
            get_data_inv = request.COOKIES.get('ajuste_inv_data')

        get_hora_inv = None
        if 'ajuste_inv_hora' in request.COOKIES:
            get_hora_inv = request.COOKIES.get('ajuste_inv_hora')

        initial = {}
        if get_data_inv is not None:
            initial.update({"data": get_data_inv})
        if get_hora_inv is not None:
            initial.update({"hora": get_hora_inv})
        self.form = self.Form_class(initial=initial)

        if 'qtd' in kwargs:
            if get_data_inv is not None:
                kwargs['data'] = get_data_inv
            if get_hora_inv is not None:
                kwargs['hora'] = get_hora_inv
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
        self.request = request
        self.start()
        self.form = self.Form_class(request.POST)

        if 'qtd' in kwargs:
            self.form.data['qtd'] = kwargs['qtd']
        if 'data' in kwargs:
            self.form.data['data'] = kwargs['data']
        if 'hora' in kwargs:
            self.form.data['hora'] = kwargs['hora']

        set_data_inv = None
        set_hora_inv = None
        if self.form.is_valid():
            qtd = self.form.cleaned_data['qtd']
            data = self.form.cleaned_data['data']
            hora = self.form.cleaned_data['hora']
            kwargs['qtd'] = qtd
            kwargs['data'] = data
            kwargs['hora'] = hora
            set_data_inv = data
            set_hora_inv = hora
            if not self.mount_context(request, **kwargs):
                return redirect('apoio_ao_erp')

        self.context['form'] = self.form
        response = render(request, self.template_name, self.context)
        if set_data_inv is None:
            response.delete_cookie('ajuste_inv_data')
        else:
            response.set_cookie('ajuste_inv_data', set_data_inv)
        if set_hora_inv is None:
            response.delete_cookie('ajuste_inv_hora')
        else:
            response.set_cookie('ajuste_inv_hora', set_hora_inv)
        return response
