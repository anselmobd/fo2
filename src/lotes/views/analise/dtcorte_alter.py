import re

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import group_rowspan

import lotes.forms as forms
import lotes.models as models
import lotes.queries as queries


class DtCorteAlter(View):
    Form_class = forms.DtCorteAlterForm
    template_name = 'lotes/analise/dtcorte_alter.html'
    title_name = 'Por data de corte e alternativa'

    def mount_context(self, cursor, data_de, data_ate, alternativa):
        # A ser produzido
        context = {}
        if data_ate is None:
            data_ate = data_de

        data = queries.analise.dtcorte_alter_qtd(
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
                if row['PERIODO_INI'] is not None:
                    row['PERIODO_INI'] = row['PERIODO_INI'].date()
                if row['PERIODO_FIM'] is not None:
                    row['PERIODO_FIM'] = row['PERIODO_FIM'].date()
                if row['DATA_CORTE'] is not None:
                    row['DATA_CORTE'] = row['DATA_CORTE'].date()
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
                'style': {7: 'text-align: right;'},
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
            cursor = db_cursor_so(request)
            context.update(self.mount_context(
                cursor, data_de, data_ate, alternativa))
        context['form'] = form
        return render(request, self.template_name, context)
