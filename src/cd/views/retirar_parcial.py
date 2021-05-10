from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

import lotes.models
import lotes.queries
from lotes.views.lote.conserto_lote import dict_conserto_lote

import cd.forms
import cd.views.gerais


class RetirarParcial(PermissionRequiredMixin, View):

    def __init__(self, mobile=False):
        self.mobile = mobile
        self.permission_required = 'lotes.can_inventorize_lote'
        self.Form_class = cd.forms.RetirarParcialForm
        if self.mobile:
            self.template_name = 'cd/retirar_parcial_m.html'
            self.title_name = 'Retirar parcial'
        else:
            self.template_name = 'cd/retirar_parcial.html'
            self.title_name = 'Retirar lote parcial'

    def mount_context(self, request, form):
        context = {}

        lote = form.cleaned_data['lote']
        quant_retirar = form.cleaned_data['quant']
        identificado = form.cleaned_data['identificado']

        lote_rec = lotes.models.Lote.objects.get(lote=lote)

        endereco = lote_rec.local
        context.update({
            'op': lote_rec.op,
            'lote_referencia': lote_rec.lote,
            'referencia': lote_rec.referencia,
            'cor': lote_rec.cor,
            'tamanho': lote_rec.tamanho,
            'qtd': lote_rec.qtd,
            'local': lote_rec.local,
            'quant_retirar': quant_retirar,
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
                request, lote, '63', 'out', quant_retirar)

            if data['error_level'] > 0:
                level = data['error_level']
                erro = data['msg']
                context.update({
                    'concerto_erro':
                        f'Erro ao retirar {quant_retirar} '
                        f'peça{"s" if quant_retirar > 1 else ""} do '
                        f'concerto: {level} - "{erro}"',
                })
                if level not in [1, 2]:
                    return context

            # retirada parcial não tira o lote do endereço, mas
            # ajusta quantidades
            lote_rec.conserto -= quant_retirar
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

        context.update(cd.views.gerais.lista_lotes_em(endereco))

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


class RetirarParcialMobile(RetirarParcial):

    def __init__(self, mobile=True):
        super(RetirarParcialMobile, self).__init__(mobile=mobile)
