from pprint import pprint
import copy

from django.shortcuts import render
from django.db import connections
from django.views import View

from utils.views import totalize_grouped_data
from fo2.template import group_rowspan

from lotes.forms import DistribuicaoForm
import lotes.models as models


class Distribuicao(View):
    Form_class = DistribuicaoForm
    template_name = 'lotes/distribuicao.html'
    title_name = 'Distribuição'

    def mount_context(self, cursor, estagio, data_de, data_ate, familia):
        if data_ate is None and data_de is not None:
            data_ate = data_de
        familia_divisao = -1
        if familia:
            familia_divisao = familia.divisao_producao

        context = {
            'estagio': estagio,
            'data_de': data_de,
            'data_ate': data_ate,
            'familia': familia,
            }

        data = models.distribuicao(
            cursor, estagio, data_de, data_ate, familia_divisao)

        group = ['DATA', 'FAMILIA']
        totalize_grouped_data(data, {
            'group': group,
            'sum': ['LOTES', 'PECAS'],
            'count': [],
            'descr': {'COR': 'Totais:'},
        })
        group_rowspan(data, group)

        context.update({
            'headers': ('Data', 'Família', 'OP', 'Referência',
                        'Tamanho', 'Cor', 'Lotes', 'Peças'),
            'fields': ('DATA', 'FAMILIA', 'OP', 'REF',
                       'TAM', 'COR', 'LOTES', 'PECAS'),
            'data': data,
            'group': group,
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
            estagio = form.cleaned_data['estagio']
            data_de = form.cleaned_data['data_de']
            data_ate = form.cleaned_data['data_ate']
            familia = form.cleaned_data['familia']
            cursor = connections['so'].cursor()
            context.update(
                self.mount_context(
                    cursor, estagio, data_de, data_ate, familia))
        context['form'] = form
        return render(request, self.template_name, context)
