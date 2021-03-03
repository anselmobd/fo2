import copy
from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import totalize_grouped_data, group_rowspan

from lotes.forms import DistribuicaoForm
import lotes.queries.producao


class Distribuicao(View):
    Form_class = DistribuicaoForm
    template_name = 'lotes/distribuicao.html'
    title_name = 'Distribuição Tecelagem'

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

        data = lotes.queries.producao.distribuicao(
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
            # estagio = form.cleaned_data['estagio']
            estagio = '22'
            data_de = form.cleaned_data['data_de']
            data_ate = form.cleaned_data['data_ate']
            familia = form.cleaned_data['familia']
            cursor = db_cursor_so(request)
            context.update(
                self.mount_context(
                    cursor, estagio, data_de, data_ate, familia))
        context['form'] = form
        return render(request, self.template_name, context)
