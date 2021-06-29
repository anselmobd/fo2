from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import group_rowspan

import lotes.forms as forms
import lotes.queries as queries


class PeriodoAlter(View):
    Form_class = forms.PeriodoAlterForm
    template_name = 'lotes/analise/periodo_alter.html'
    title_name = 'Por período e alternativa'

    def mount_context(self, cursor, periodo_de, periodo_ate, alternativa):
        # A ser produzido
        context = {}
        if periodo_ate is None:
            periodo_ate = periodo_de

        data = queries.analise.periodo_alter_qtd(
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
        form.data = form.data.copy()
        if 'periodo' in kwargs:
            form.data['periodo_de'] = kwargs['periodo']
            form.data['periodo_ate'] = kwargs['periodo']
        if form.is_valid():
            periodo_de = form.cleaned_data['periodo_de']
            periodo_ate = form.cleaned_data['periodo_ate']
            alternativa = form.cleaned_data['alternativa']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(
                cursor, periodo_de, periodo_ate, alternativa))
        context['form'] = form
        return render(request, self.template_name, context)
