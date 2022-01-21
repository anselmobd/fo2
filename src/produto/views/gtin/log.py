from pprint import pprint

from django.shortcuts import render
from django.views import View

import produto.forms
import produto.models


class GtinLog(View):
    Form_class = produto.forms.GtinLogForm
    template_name = 'produto/gtin/log.html'
    title_name = 'Log de alterações GTIN'

    def mount_context(self, ref, gtin, usuario):
        context = {
            'ref': ref,
            'gtin': gtin,
            'usuario': usuario,
            }

        data = produto.models.GtinLog.objects
        if ref:
            data = data.filter(produto__referencia=ref)
        if gtin:
            data = data.filter(gtin=gtin)
        if usuario:
            data = data.filter(colaborador__user__username=usuario)
        data = data.order_by('-quando').values(
            'colaborador__user__username',
            'quando',
            'produto__referencia',
            'cor__cor',
            'cor__descricao',
            'tamanho__tamanho__nome',
            'tamanho__descricao',
            'gtin',
        )

        if len(data) == 0:
            context.update({'erro': 'Nada selecionado'})
            return context
        
        for row in data:
            if row['tamanho__tamanho__nome'] == row['tamanho__descricao']:
                row['tamanho'] = row['tamanho__descricao']
            else:
                row['tamanho'] = ' '.join([
                    row['tamanho__tamanho__nome'],
                    row['tamanho__descricao'],
                ])
            if row['cor__cor'] == row['cor__descricao']:
                row['cor'] = row['cor__cor']
            else:
                row['cor'] = ' '.join([
                    row['cor__cor'],
                    row['cor__descricao'],
                ])

        headers = [
            'Usuário',
            'Data hora',
            'GTIN',
            'Referência',
            'Cor',
            'Tamanho',
        ]
        fields = [
            'colaborador__user__username',
            'quando',
            'gtin',
            'produto__referencia',
            'cor',
            'tamanho',
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
            usuario = form.cleaned_data['usuario']
            context.update(self.mount_context(ref, gtin, usuario))
        context['form'] = form
        return render(request, self.template_name, context)
