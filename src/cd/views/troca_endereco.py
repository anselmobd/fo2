from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

import lotes.models
from geral.functions import has_permission

import cd.forms


class TrocaEndereco(PermissionRequiredMixin, View):

    def __init__(self, mobile=False):
        self.mobile = mobile
        self.permission_required = 'lotes.can_relocate_lote'
        self.Form_class = cd.forms.TrocaEnderecoForm
        if self.mobile:
            self.template_name = 'cd/troca_endereco_m.html'
        else:
            self.template_name = 'cd/troca_endereco.html'
        self.title_name = 'Trocar endereço'

    def get_lotes_no_local(self, endereco, count=False):
        lotes_no_local = lotes.models.Lote.objects.filter(
            local=endereco)

        if count:
            return lotes_no_local.count()

        lotes_no_local = lotes_no_local.values(
                    'op', 'lote', 'qtd_produzir',
                    'referencia', 'cor', 'tamanho',
                    'local_at', 'local_usuario__username')
        lotes_no_local = lotes_no_local.order_by(
            'referencia', 'cor', 'ordem_tamanho', 'op', 'lote'
            )
        return lotes_no_local

    def mount_context(self, request, form):
        endereco_de = form.cleaned_data['endereco_de']
        endereco_para = form.cleaned_data['endereco_para']

        context = {'endereco_de': endereco_de,
                   'endereco_para': endereco_para}

        count_lotes_de = self.get_lotes_no_local(endereco_de, count=True)
        if count_lotes_de == 0:
            context.update({'erro': 'Endereço antigo está vazio'})
            return context

        count_lotes_para = self.get_lotes_no_local(endereco_para, count=True)
        if count_lotes_para != 0:
            context.update({'erro': 'Endereço novo NÃO está vazio'})
            return context

        if request.POST.get("troca"):
            context.update({'confirma': True})
            busca_endereco = endereco_de
            form.data['identificado_de'] = endereco_de
            form.data['identificado_para'] = endereco_para

        else:
            if form.data['identificado_de'] != endereco_de or \
                    form.data['identificado_para'] != endereco_para:
                context.update({
                    'erro': 'Não altere os endereços na confirmação. '
                            'Digite-os novamente.'})
                form.data['endereco_de'] = None
                form.data['endereco_para'] = None
                return context

            lotes_recs = lotes.models.Lote.objects.filter(
                local=endereco_de)

            for lote in lotes_recs:
                lote.local = endereco_para
                lote.local_usuario = request.user
                lote.save()
            form.data['endereco_de'] = None
            form.data['endereco_para'] = None
            busca_endereco = endereco_para

        lotes_no_local = self.get_lotes_no_local(busca_endereco)
        q_lotes = len(lotes_no_local)

        q_itens = 0
        for row in lotes_no_local:
            q_itens += row['qtd_produzir']
        context.update({
            'q_lotes': q_lotes,
            'q_itens': q_itens,
            'data': lotes_no_local,
            })
        context.update({
            'headers': ('Referência', 'Tamanho', 'Cor',
                        'OP', 'Lote', 'Em',
                        'Por'),
            'fields': ('referencia', 'tamanho', 'cor',
                       'op', 'lote', 'local_at',
                       'local_usuario__username'),
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
            data = self.mount_context(request, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)


class TrocaEnderecoMobile(TrocaEndereco):

    def __init__(self, mobile=True):
        super(TrocaEnderecoMobile, self).__init__(mobile=mobile)
