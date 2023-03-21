from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import totalize_grouped_data, group_rowspan

from lotes.queries.op import op_perda
from lotes.forms.perda import OpPerdaForm


class OpPerda(View):

    def __init__(self):
        super().__init__()
        self.Form_class = OpPerdaForm
        self.template_name = 'lotes/perda.html'
        self.title_name = 'Perdas de produção'

    def mount_context(self, cursor, data_de, data_ate, colecao, detalhe):
        context = {
            'data_de': data_de,
            'data_ate': data_ate,
            'colecao': colecao,
            'detalhe': detalhe,
        }
        colecao_codigo = colecao.colecao if colecao else None

        data = op_perda.query(
            cursor, data_de, data_ate, colecao_codigo, detalhe)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma perda de produção encontrada',
            })
            return context

        for row in data:
            row['OP|LINK'] = reverse('producao:op__get', args=[row['OP']])
            if 'REF' in row:
                row['REF|LINK'] = reverse('produto:ref__get', args=[row['REF']])
            row['PERC'] = row['QTD'] / row['QTDOP'] * 100
            row['PERC|DECIMALS'] = 2

        if detalhe in ['ref', 'item']:
            group = ['REF', 'COLECAO']
        elif detalhe == 'col':
            group = ['COLECAO']

        totalize_grouped_data(data, {
            'group': group,
            'sum': ['QTD'],
            'count': [],
            'descr': {'OP': 'Total:'},
            'flags': ['NO_TOT_1'],
            'global_sum': ['QTD'],
            'global_descr': {'OP': 'Total geral:'},
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(data, group)

        if detalhe == 'ref':
            headers = ("Referência", "Coleção", "OP", "Quantidade OP", "Perda OP", "%")
            fields = ('REF', 'COLECAO', 'OP', 'QTDOP', 'QTD', 'PERC')
            style = {
                4: 'text-align: right;',
                5: 'text-align: right;',
                6: 'text-align: right;',
            }
        elif detalhe == 'item':
            headers = ("Referência", "Coleção", "Cor", "Tamanho", "OP", "Quantidade OP item", "Perda OP item", "%")
            fields = ('REF', 'COLECAO', 'COR', 'TAM', 'OP', 'QTDOP', 'QTD', 'PERC')
            style = {
                6: 'text-align: right;',
                7: 'text-align: right;',
                8: 'text-align: right;',
            }
        elif detalhe == 'col':
            headers = ("Coleção", "OP", "Quantidade OP", "Perda OP", "%")
            fields = ('COLECAO', 'OP', 'QTDOP', 'QTD', 'PERC')
            style = {
                3: 'text-align: right;',
                4: 'text-align: right;',
                5: 'text-align: right;',
            }
        
        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'group': group,
            'style': style,
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
            data_de = form.cleaned_data['data_de']
            data_ate = form.cleaned_data['data_ate']
            colecao = form.cleaned_data['colecao']
            detalhe = form.cleaned_data['detalhe']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(
                cursor, data_de, data_ate, colecao, detalhe))
        context['form'] = form
        return render(request, self.template_name, context)
