from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

import produto.forms
import produto.models


class GtinLog(View):
    Form_class = produto.forms.GtinLogForm
    template_name = 'produto/gtin/log.html'
    title_name = 'Log de alterações GTIN'

    def mount_context(self, cursor, ref, gtin):
        context = {
            'ref': ref,
            'gtin': gtin,
            }

        fields = [
            'colaborador__user__username',
            'quando',
            'produto__referencia',
            'cor__cor',
            'cor__descricao',
            'tamanho__tamanho__nome',
            'tamanho__descricao',
            'gtin',
        ]

        data = produto.models.GtinLog.objects
        if ref:
            data = data.filter(produto__referencia=ref)
        if gtin:
            data = data.filter(gtin=gtin)
        data = data.order_by('-quando').values(*fields)

        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context

        headers = [
            'Usuário',
            'Data hora',
            'Referência',
            'Cor',
            'Descr.',
            'Tamanho',
            'Descr.',
            'GTIN',
        ]

        context.update({
            'headers': headers,
            'fields': fields,
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
            ref = form.cleaned_data['ref']
            gtin = form.cleaned_data['gtin']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, ref, gtin))
        context['form'] = form
        return render(request, self.template_name, context)
