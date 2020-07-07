from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

import lotes.models
from geral.functions import has_permission

import cd.forms


class TrocaLocal(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_relocate_lote'
        self.Form_class = cd.forms.TrocaLocalForm
        self.template_name = 'cd/troca_local.html'
        self.title_name = 'Trocar endereço'

    def get_lotes_no_local(self, endereco, count=False):
        if endereco[1] == '%':
            lotes_no_local = lotes.models.Lote.objects.filter(
                local__startswith=endereco[0])
        else:
            lotes_no_local = lotes.models.Lote.objects.filter(
                local=endereco)
        if count:
            return lotes_no_local.count()
        if endereco[1] == '%':
            lotes_no_local = lotes_no_local.values(
                        'local', 'op', 'lote', 'qtd_produzir',
                        'referencia', 'cor', 'tamanho',
                        'local_at', 'local_usuario__username')
            lotes_no_local = lotes_no_local.order_by(
                'local', 'referencia', 'cor', 'ordem_tamanho', 'op', 'lote'
                )
        else:
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

        if endereco_de[1] == '%':
            if has_permission(request, 'lotes.can_uninventorize_road'):
                context.update({'rua': endereco_de[0]})
            else:
                context['erro'] = \
                    'Usuário não tem direito de tirar do CD uma rua inteira.'
                return context

        count_lotes_de = self.get_lotes_no_local(endereco_de, count=True)
        if count_lotes_de == 0:
            context.update({'erro': 'Endereço antigo está vazio'})
            return context

        count_lotes_para = self.get_lotes_no_local(endereco_para, count=True)
        if count_lotes_para != 0:
            context.update({'erro': 'Endereço novo NÃO está vazio'})
            return context

        q_lotes = 0
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

            if endereco_para == 'SAI':
                lotes_no_local = self.get_lotes_no_local(endereco_de)
                q_lotes = len(lotes_no_local)

            if endereco_de[1] == '%':
                lotes_recs = lotes.models.Lote.objects.filter(
                    local__startswith=endereco_de[0])
            else:
                lotes_recs = lotes.models.Lote.objects.filter(
                    local=endereco_de)
            for lote in lotes_recs:
                if endereco_para == 'SAI':
                    lote.local = None
                else:
                    lote.local = endereco_para
                lote.local_usuario = request.user
                lote.save()
            form.data['endereco_de'] = None
            form.data['endereco_para'] = None
            busca_endereco = endereco_para

        if q_lotes == 0:
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
        if endereco_de[1] == '%':
            context.update({
                'headers': ('Endereço', 'Referência', 'Tamanho', 'Cor',
                            'OP', 'Lote', 'Em',
                            'Por'),
                'fields': ('local', 'referencia', 'tamanho', 'cor',
                           'op', 'lote', 'local_at',
                           'local_usuario__username'),
                })
        else:
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
