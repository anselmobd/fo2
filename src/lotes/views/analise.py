import re

from django.shortcuts import render
from django.db import connections
from django.views import View

from fo2.template import group_rowspan

from lotes.forms import AnPeriodoAlterForm, AnDtCorteAlterForm
import lotes.models as models


class AnPeriodoAlter(View):
    Form_class = AnPeriodoAlterForm
    template_name = 'lotes/an_periodo_alter.html'
    title_name = 'Por período e alternativa'

    def mount_context(self, cursor, periodo_de, periodo_ate, alternativa):
        # A ser produzido
        context = {}
        if periodo_ate is None:
            periodo_ate = periodo_de

        data = models.an_periodo_alter_qtd(
            cursor, periodo_de, periodo_ate, alternativa)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Sem produção no período',
            })
        else:
            context.update({
                'periodo_de': periodo_de,
                'periodo_ate': periodo_ate,
            })
            for row in data:
                row['PERIODO_INI'] = row['PERIODO_INI'].date()
                row['PERIODO_FIM'] = row['PERIODO_FIM'].date()
                row['DATA_CORTE'] = row['DATA_CORTE'].date()
                if row['ORDEM_TOTAL'] == 1:
                    row['DATA_CORTE'] = 'TOTAL'
                else:
                    if row['DATA_CORTE'] is None:
                        row['DATA_CORTE'] = 'Não definida'
            group = ('PERIODO', 'PERIODO_INI', 'PERIODO_FIM',
                     'ALT', 'TIPO')
            group_rowspan(data, group)
            context.update({
                'headers': (
                    'Período', 'Período Início', 'Período Fim',
                    'Alternativa', 'Tipo', 'Data do Corte', 'Quantidade',
                    'No. OPs'),
                'fields': (
                    'PERIODO', 'PERIODO_INI', 'PERIODO_FIM',
                    'ALT', 'TIPO', 'DATA_CORTE', 'QTD', 'NUM_OPS'),
                'style': {7: 'text-align: right;',
                          8: 'text-align: right;'},
                'group': group,
                'data': data,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'periodo' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'periodo' in kwargs:
            form.data['periodo_de'] = kwargs['periodo']
            form.data['periodo_ate'] = kwargs['periodo']
        if form.is_valid():
            periodo_de = form.cleaned_data['periodo_de']
            periodo_ate = form.cleaned_data['periodo_ate']
            alternativa = form.cleaned_data['alternativa']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, periodo_de, periodo_ate, alternativa))
        context['form'] = form
        return render(request, self.template_name, context)


class AnDtCorteAlter(View):
    Form_class = AnDtCorteAlterForm
    template_name = 'lotes/an_dtcorte_alter.html'
    title_name = 'Por data de corte e alternativa'

    def mount_context(self, cursor, data_de, data_ate, alternativa):
        # A ser produzido
        context = {}
        if data_ate is None:
            data_ate = data_de

        data = models.an_dtcorte_alter_qtd(
            cursor, data_de, data_ate, alternativa)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Sem produção na data',
            })
        else:
            context.update({
                'data_de': data_de,
                'data_ate': data_ate,
            })
            total = {}
            for row in data:
                if row['ORDEM_TOTAL'] == 1:
                    row['PERIODO'] = 'TOTAL'
                    row['PERIODO_INI'] = ''
                    row['PERIODO_FIM'] = ''
                    row['OPS'] = ''
                    key = '{}#{}'.format(row['ALT'], row['TIPO_ORDEM'])
                    if key not in total:
                        total[key] = {
                            'ALT': row['ALT'],
                            'TIPO': row['TIPO'],
                            'QTD': 0,
                        }
                    total[key]['QTD'] += row['QTD']
                else:
                    if row['DATA_CORTE'] is None:
                        row['DATA_CORTE'] = 'Não definida'
                row['OPS'] = re.sub(
                    r'([1234567890]+)',
                    r'<a href="/lotes/op/\1">\1&nbsp;<span '
                    'class="glyphicon glyphicon-link" '
                    'aria-hidden="true"></span></a>',
                    row['OPS'])

            data_tot = [total[key] for key in sorted(total)]
            context.update({
                't_headers': ('Alternativa', 'Tipo', 'Quantidade'),
                't_fields': ('ALT', 'TIPO', 'QTD'),
                't_data': data_tot,
            })

            group = ('DATA_CORTE', 'ALT', 'TIPO')
            group_rowspan(data, group)
            context.update({
                'headers': (
                    'Data do Corte', 'Alternativa', 'Tipo',
                    'Período', 'Período Início', 'Período Fim', 'Quantidade',
                    'OPs'),
                'fields': (
                    'DATA_CORTE', 'ALT', 'TIPO',
                    'PERIODO', 'PERIODO_INI', 'PERIODO_FIM', 'QTD', 'OPS'),
                'safe': ('OPS',),
                'group': group,
                'data': data,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'data' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'data' in kwargs:
            form.data['data_de'] = kwargs['data']
            form.data['data_ate'] = kwargs['data']
        if form.is_valid():
            data_de = form.cleaned_data['data_de']
            data_ate = form.cleaned_data['data_ate']
            alternativa = form.cleaned_data['alternativa']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, data_de, data_ate, alternativa))
        context['form'] = form
        return render(request, self.template_name, context)
