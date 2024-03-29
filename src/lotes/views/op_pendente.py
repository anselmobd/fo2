from pprint import pprint

from django.shortcuts import render
from django.views import View
from django.urls import reverse

from fo2.connections import db_cursor_so

from utils.views import totalize_data, group_rowspan

from lotes.forms import OpPendenteForm
import lotes.models as models
import lotes.queries as queries


class OpPendente(View):

    def __init__(self):
        super().__init__()
        self.Form_class = OpPendenteForm
        self.template_name = 'lotes/op_pendente.html'
        self.title_name = 'Ordens pendentes por estágio'

    def mount_context(self, cursor, estagio, periodo_de, periodo_ate,
                      data_de, data_ate, colecao, situacao, tipo):
        if colecao:
            filtra_colecao = colecao.colecao
        else:
            filtra_colecao = None
        data = queries.op.op_pendente(
            cursor, estagio, periodo_de, periodo_ate, data_de, data_ate,
            filtra_colecao, situacao, tipo)
        context = {}
        if len(data) == 0:
            context.update({
                'msg_erro': 'Sem pendências',
            })
        else:
            context.update({
                'estagio': estagio,
            })
            if periodo_de != 0:
                context.update({
                    'periodo_de': periodo_de,
                })
            if periodo_ate != 9999:
                context.update({
                    'periodo_ate': periodo_ate,
                })
            if data_de is not None:
                context.update({
                    'data_de': data_de,
                })
            if data_ate is not None:
                context.update({
                    'data_ate': data_ate,
                })
            if colecao is not None:
                context.update({
                    'colecao': colecao.descr_colecao,
                })
            if situacao is not None:
                context.update({
                    'situacao': situacao,
                })
            if tipo is not None:
                context.update({
                    'tipo': tipo,
                })
            link = ('OP')
            for row in data:
                row['LINK'] = reverse('producao:op__get', args=[row['OP']])
                row['DATA_INI'] = row['DATA_INI'].date()
                row['DATA_FIM'] = row['DATA_FIM'].date()
                if row['DT_CORTE'] is None:
                    row['DT_CORTE'] = ' '
                else:
                    row['DT_CORTE'] = row['DT_CORTE'].date()

                total = \
                    row['LOTES_ANTES'] + \
                    row['LOTES'] + \
                    row['LOTES_DEPOIS']
                row['PERC_ANTES'] = round(
                    row['LOTES_ANTES'] / row['QTD_LOTES'] * 100, 2)
                row['PERC_LOTES'] = round(
                    row['LOTES'] / row['QTD_LOTES'] * 100, 2)
                row['PERC_DEPOIS'] = round(
                    row['LOTES_DEPOIS'] / row['QTD_LOTES'] * 100, 2)
                row['PERC_FINALIZADO'] = round(
                    100 - row['PERC_ANTES'] - row['PERC_LOTES'] -
                    row['PERC_DEPOIS'], 2)
                row['PERC_FINALIZADO'] = abs(row['PERC_FINALIZADO'])
            totalize_data(data, {
                'sum': ['QTD', 'LOTES'],
                'count': ['OP'],
                'descr': {'REF': 'Qtd. OPs:', 'DT_CORTE': 'Totais:'}})

            context.update({
                'headers': (
                    'Estágio', 'Período',
                    'Data início', 'Data final', 'Coleção',
                    'Referência', 'OP', 'Sit.', 'Data de corte',
                    'Quant. peças', 'Quant. lotes',
                    'Total de lotes',
                    '% Antes', '% No estágio', '% Depois', '% Finalizado'),
                'fields': (
                    'ESTAGIO', 'PERIODO', 'DATA_INI', 'DATA_FIM', 'COLECAO',
                    'REF', 'OP', 'SITUACAO', 'DT_CORTE',
                    'QTD', 'LOTES', 'QTD_LOTES',
                    'PERC_ANTES', 'PERC_LOTES', 'PERC_DEPOIS',
                    'PERC_FINALIZADO'),
                'data': data,
                'link': link,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'estagio' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        form.data = form.data.copy()
        if 'estagio' in kwargs:
            form.data['estagio'] = kwargs['estagio']
        if form.is_valid():
            estagio = form.cleaned_data['estagio']
            periodo_de = form.cleaned_data['periodo_de']
            periodo_ate = form.cleaned_data['periodo_ate']
            data_de = form.cleaned_data['data_de']
            data_ate = form.cleaned_data['data_ate']
            colecao = form.cleaned_data['colecao']
            situacao = form.cleaned_data['situacao']
            tipo = form.cleaned_data['tipo']
            cursor = db_cursor_so(request)
            context.update(
                self.mount_context(cursor, estagio, periodo_de, periodo_ate,
                                   data_de, data_ate, colecao, situacao, tipo))
        context['form'] = form
        return render(request, self.template_name, context)
