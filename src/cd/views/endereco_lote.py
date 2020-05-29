from pprint import pprint

from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

import lotes.models

import cd.forms


class EnderecoLote(View):

    def __init__(self):
        self.Form_class = cd.forms.AskLoteForm
        self.template_name = 'cd/endereco_lote.html'
        self.title_name = 'Verifica endereço de Lote'

    def mount_context(self, request, form):
        lote = form.cleaned_data['lote']

        context = {'lote': lote}

        try:
            lote_rec = lotes.models.Lote.objects.get(lote=lote)
        except lotes.models.Lote.DoesNotExist:
            context.update({'erro': 'Lote não encontrado'})
            return context

        if lote_rec.local is None or lote_rec.local == '':
            local = 'Não endereçado'
            lotes_no_local = -1
        else:
            local = lote_rec.local
            lotes_no_local = len(lotes.models.Lote.objects.filter(
                local=lote_rec.local))

        context.update({
            'op': lote_rec.op,
            'referencia': lote_rec.referencia,
            'cor': lote_rec.cor,
            'tamanho': lote_rec.tamanho,
            'qtd_produzir': lote_rec.qtd_produzir,
            'local': local,
            'q_lotes': lotes_no_local,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'lote' in kwargs and kwargs['lote'] is not None:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'lote' in kwargs and kwargs['lote'] is not None:
            form.data['lote'] = kwargs['lote']
        if form.is_valid():
            data = self.mount_context(request, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)


def dict_endereco_lote(lote):
    data = {
        'lote': lote,
    }

    try:
        lote_rec = lotes.models.Lote.objects.get(lote=lote)

        data.update({
            'op': lote_rec.op,
            'referencia': lote_rec.referencia,
            'cor': lote_rec.cor,
            'tamanho': lote_rec.tamanho,
            'qtd_produzir': lote_rec.qtd_produzir,
        })

        if lote_rec.local is None or lote_rec.local == '':
            data.update({
                'error_level': 2,
                'msg': 'Lote não endereçado',
            })
        else:
            local = lote_rec.local
            lotes_no_local = len(lotes.models.Lote.objects.filter(
                local=lote_rec.local))

            data.update({
                'error_level': 0,
                'local': local,
                'q_lotes': lotes_no_local,
                'msg': f'OK',
            })

    except lotes.models.Lote.DoesNotExist:
        data.update({
            'error_level': 1,
            'msg': 'Lote não encontrado',
        })

    return data


def ajax_endereco_lote(request, lote):
    data = dict_endereco_lote(lote)

    return JsonResponse(data, safe=False)
