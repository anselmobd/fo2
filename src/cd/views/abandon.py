from pprint import pprint

from django.db import connections
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

import lotes.models
import lotes.queries

import cd.forms
import cd.views.gerais


class LoteLocal(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_inventorize_lote'
        self.Form_class = cd.forms.LoteForm
        self.template_name = 'cd/lote_local.html'
        self.title_name = 'Inventariar'

    def mount_context(self, request, form):
        cursor = connections['so'].cursor()

        endereco = form.cleaned_data['endereco']
        lote = form.cleaned_data['lote']
        periodo = lote[:4]
        ordem_confeccao = lote[-5:]
        identificado = form.cleaned_data['identificado']
        end_conf = form.cleaned_data['end_conf']

        if end_conf == 'SAI':
            end_conf = None

        if endereco == 'SAI':
            endereco = None

        context = {'endereco': endereco}

        lote_sys = lotes.queries.lote.posicao_get_item(
            cursor, periodo, ordem_confeccao)
        if len(lote_sys) == 0:
            if endereco is not None:
                context.update({
                    'erro': 'Lote não encontrado no Systêxtil. Única ação '
                            'possivel é dar saída (Endereço "SAI").'})
                return context

        try:
            lote_rec = lotes.models.Lote.objects.get(lote=lote)
        except lotes.models.Lote.DoesNotExist:
            context.update({'erro': 'Lote não encontrado'})
            return context

        if lote_rec.referencia >= 'C0000':
            if endereco is not None:
                context.update({
                    'erro': 'Lote de MD. Única ação '
                            'possivel é dar saída (Endereço "SAI").'})
                return context

        context.update({
            'op': lote_rec.op,
            'referencia': lote_rec.referencia,
            'cor': lote_rec.cor,
            'tamanho': lote_rec.tamanho,
            'qtd_produzir': lote_rec.qtd_produzir,
            'local': lote_rec.local,
            })

        if len(lote_sys) != 0:
            if endereco is None:  # SAI
                estagios_aceitos = [63, 66, 999]
            else:  # endereça
                estagios_aceitos = [63, 66]
            if lote_rec.estagio not in estagios_aceitos:
                def e999(e):
                    return 'finalizado' if e == 999 else e
                context.update({
                    'erroestagio': map(e999, estagios_aceitos),
                    'estagio': e999(lote_rec.estagio),
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
