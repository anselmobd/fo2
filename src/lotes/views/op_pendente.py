from django.shortcuts import render
from django.db import connections
from django.views import View

from fo2.template import group_rowspan
from utils.views import totalize_data

from lotes.forms import OpPendenteForm
import lotes.models as models


class OpPendente(View):
    Form_class = OpPendenteForm
    template_name = 'lotes/op_pendente.html'
    title_name = 'Ordens pendentes por estágio'

    def mount_context(self, cursor, estagio, periodo_de, periodo_ate):
        data = models.op_pendente(cursor, estagio, periodo_de, periodo_ate)
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
            link = ('OP')
            for row in data:
                row['LINK'] = '/lotes/op/{}'.format(row['OP'])
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
                    'Data início', 'Data final',
                    'Referência', 'OP', 'Data de corte',
                    'Quant. peças', 'Quant. lotes',
                    'Total de lotes',
                    '% Antes', '% No estágio', '% Depois', '% Finalizado'),
                'fields': (
                    'ESTAGIO', 'PERIODO', 'DATA_INI', 'DATA_FIM',
                    'REF', 'OP', 'DT_CORTE', 'QTD', 'LOTES', 'QTD_LOTES',
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
        if 'estagio' in kwargs:
            form.data['estagio'] = kwargs['estagio']
        if form.is_valid():
            estagio = form.cleaned_data['estagio']
            periodo_de = form.cleaned_data['periodo_de']
            periodo_ate = form.cleaned_data['periodo_ate']
            cursor = connections['so'].cursor()
            context.update(
                self.mount_context(cursor, estagio, periodo_de, periodo_ate))
        context['form'] = form
        return render(request, self.template_name, context)
