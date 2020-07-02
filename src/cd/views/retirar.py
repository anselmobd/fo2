from pprint import pprint

from django.db import connections
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

import lotes.models
from lotes.views.lote.conserto_lote import dict_conserto_lote

import cd.forms


class Retirar(PermissionRequiredMixin, View):

    def __init__(self, mobile=False):
        self.mobile = mobile
        self.permission_required = 'lotes.can_inventorize_lote'
        self.Form_class = cd.forms.RetirarForm
        if self.mobile:
            self.template_name = 'cd/retirar_m.html'
        else:
            self.template_name = 'cd/retirar.html'
        self.title_name = 'Retirar lote inteiro'

    def mount_context(self, request, form):
        cursor = connections['so'].cursor()
        context = {}

        lote = form.cleaned_data['lote']
        periodo = lote[:4]
        ordem_confeccao = lote[-5:]
        identificado = form.cleaned_data['identificado']

        lote_sys = lotes.models.posicao_get_item(
            cursor, periodo, ordem_confeccao)

        try:
            lote_rec = lotes.models.Lote.objects.get(lote=lote)
        except lotes.models.Lote.DoesNotExist:
            context.update({'erro': 'Lote não encontrado'})
            return context

        endereco = lote_rec.local
        context.update({
            'op': lote_rec.op,
            'lote_referencia': lote_rec.lote,
            'referencia': lote_rec.referencia,
            'cor': lote_rec.cor,
            'tamanho': lote_rec.tamanho,
            'qtd': lote_rec.qtd,
            'local': lote_rec.local,
            })

        if identificado:
            form.data['identificado'] = None
            form.data['lote'] = None
            if lote != identificado:
                context.update({
                    'erro': 'A confirmação é bipando o mesmo lote. '
                            'Identifique o lote novamente.'})
                return context

            data = dict_conserto_lote(
                request, lote, '63', 'out', lote_rec.qtd)

            if data['error_level'] > 0:
                level = data['error_level']
                erro = data['msg']
                context.update({
                    'concerto_erro':
                        f'Erro ao retirar {lote_rec.qtd} '
                        f'peça{"s" if lote_rec.qtd > 1 else ""} do '
                        f'concerto: {level} - "{erro}"',
                })
                if level not in [1, 2]:
                    return context

            lote_rec.local = None
            lote_rec.local_usuario = request.user
            lote_rec.save()

            context['identificado'] = identificado
        else:
            context['lote'] = lote
            if lote_rec.local is not None:
                context['confirma'] = True
                form.data['identificado'] = form.data['lote']
            form.data['lote'] = None

        if not endereco:
            return context

        lotes_no_local = lotes.models.Lote.objects.filter(
            local=endereco).order_by(
                '-local_at'
                ).values(
                    'op', 'lote', 'qtd',
                    'referencia', 'cor', 'tamanho',
                    'local_at', 'local_usuario__username')
        if lotes_no_local:
            q_itens = 0
            for row in lotes_no_local:
                q_itens += row['qtd']
            context.update({
                'q_lotes': len(lotes_no_local),
                'q_itens': q_itens,
                'headers': ('Bipado em', 'Bipado por',
                            'Lote', 'Quant.',
                            'Ref.', 'Cor', 'Tam.', 'OP'),
                'fields': ('local_at', 'local_usuario__username',
                           'lote', 'qtd',
                           'referencia', 'cor', 'tamanho', 'op'),
                'data': lotes_no_local,
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


class RetirarMobile(Retirar):

    def __init__(self, mobile=True):
        super(RetirarMobile, self).__init__(mobile=mobile)
