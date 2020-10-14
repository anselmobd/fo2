from pprint import pprint

from django.db import connections
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.views import View

import lotes.models
import lotes.queries
from lotes.views.lote.conserto_lote import dict_conserto_lote

import cd.forms
import cd.views.gerais


class Enderecar(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_inventorize_lote'
        self.Form_class = cd.forms.EnderecarForm
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

        lote_rec = lotes.models.Lote.objects.get(lote=lote)
        qtd_livre = lote_rec.qtd - lote_rec.conserto

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
            'qtd_livre': qtd_livre,
            'conserto': lote_rec.conserto,
            })

        estagios_aceitos = [63]
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

            level = 999
            if lote_rec.conserto == 0:
                # se lote não tem quantidade endereçada,
                # então endereça (coloca qtd total em conserto)
                data = dict_conserto_lote(
                    request, lote, '63', 'in', qtd_livre)

                if data['error_level'] > 0:
                    level = data['error_level']
                    erro = data['msg']
                    context.update({
                        'concerto_erro':
                            f'Erro ao inserir {qtd_livre} '
                            f'peça{"s" if qtd_livre > 1 else ""} no '
                            f'concerto: {level} - "{erro}"',
                    })
                    if level not in [1, 2, 3]:
                        return context

            if level == 0:
                context['qtd_livre'] = 0
                lote_rec.conserto += qtd_livre
            lote_rec.local = endereco
            lote_rec.local_usuario = request.user
            lote_rec.save()

            context['identificado'] = identificado
        else:
            context['lote'] = lote
            if lote_rec.local != endereco or qtd_livre != 0:
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

    def __init__(self):
        super(EnderecarMobile, self).__init__()
        self.template_name = 'cd/enderecar_m.html'
