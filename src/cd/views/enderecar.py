from pprint import pprint

from django.db import connections
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

import lotes.models
from lotes.views.lote.conserto_lote import dict_conserto_lote

import cd.forms
import cd.views.gerais


class Enderecar(PermissionRequiredMixin, View):

    def __init__(self, mobile=False):
        self.mobile = mobile
        self.permission_required = 'lotes.can_inventorize_lote'
        self.Form_class = cd.forms.EnderecarForm
        if self.mobile:
            self.template_name = 'cd/enderecar_m.html'
        else:
            self.template_name = 'cd/enderecar.html'
        self.title_name = 'Endereçar'

    def mount_context(self, request, form):
        cursor = connections['so'].cursor()

        endereco = form.cleaned_data['endereco']
        lote = form.cleaned_data['lote']
        periodo = lote[:4]
        ordem_confeccao = lote[-5:]
        identificado = form.cleaned_data['identificado']
        end_conf = form.cleaned_data['end_conf']

        context = {'endereco': endereco}

        lote_sys = lotes.models.posicao_get_item(
            cursor, periodo, ordem_confeccao)

        lote_rec = lotes.models.Lote.objects.get(lote=lote)

        if lote_rec.referencia >= 'C0000':
            context.update({
                'erro': 'Lote de MD não pode ser endereçado no CD.'})
            return context

        context.update({
            'op': lote_rec.op,
            'referencia': lote_rec.referencia,
            'cor': lote_rec.cor,
            'tamanho': lote_rec.tamanho,
            'qtd_produzir': lote_rec.qtd_produzir,
            'local': lote_rec.local,
            })

        estagios_aceitos = [63]
        if lote_rec.estagio not in estagios_aceitos:
            context.update({
                'erroestagio': estagios_aceitos,
                'estagio': lote_rec.estagio,
                })
            return context

        if identificado:
            form.data['identificado'] = None
            form.data['lote'] = None
            if endereco != end_conf:
                context.update({
                    'erro': 'Não altere o endereço após a identificação.'})
                return context

            if lote != identificado:
                context.update({
                    'erro': 'A confirmação é bipando o mesmo lote. '
                            'Identifique o lote novamente.'})
                return context

            lote_rec.local = endereco
            lote_rec.local_usuario = request.user
            lote_rec.save()

            context['identificado'] = identificado
        else:
            context['lote'] = lote
            if lote_rec.local != endereco:
                context['confirma'] = True
                form.data['identificado'] = form.data['lote']
                form.data['end_conf'] = form.data['endereco']
            form.data['lote'] = None

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


class EnderecarMobile(Enderecar):

    def __init__(self, mobile=True):
        super(EnderecarMobile, self).__init__(mobile=mobile)
