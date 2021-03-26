from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

import comercial.forms as forms
import comercial.queries as queries


class Vendas(O2BaseGetPostView):

    periodo_cols_options = {
        '0': None,
        '3612': {
            '3 meses': '3:',
            '6 meses': '6:',
            '1 ano': '12:',
            '2 anos': '24:',
        },
        '1234': {
            'Mês anterior': '1:0',
            '2 meses antes': '3:1',
            '3 meses antes': '6:3',
            '4 meses antes': '10:6',
        },
    }

    def __init__(self, *args, **kwargs):
        super(Vendas, self).__init__(*args, **kwargs)
        self.Form_class = forms.VendasForm
        self.template_name = 'comercial/vendas.html'
        self.title_name = 'Vendas'

    def mount_context(self):
        ref = self.form.cleaned_data['ref']
        modelo = self.form.cleaned_data['modelo']
        periodo = self.form.cleaned_data['periodo']
        qtd_por_mes = self.form.cleaned_data['qtd_por_mes']

        cursor = db_cursor_so(self.request)

        periodo_cols=self.periodo_cols_options[periodo]

        av = queries.AnaliseVendas(
            cursor, ref=ref, modelo=modelo, por='qtd_ref',
            periodo_cols=periodo_cols, qtd_por_mes=qtd_por_mes=='m')
        data = av.data

        headers = ['Referência']
        fields = ['ref']

        if periodo_cols:
            for col in periodo_cols:
                headers.append(col)
                fields.append(queries.str2col_name(col))
        else:
            headers += ['Quantidade']
            fields += ['qtd']
            if qtd_por_mes == 'm':
                headers += ['Última venda', 'Primeira venda', 'Quantidade por mês']
                fields += ['dt_max', 'dt_min', 'qtd_mes']

        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })
