from pprint import pprint
from datetime import datetime

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.functions import dec_month, dec_months, untuple_keys_concat
from utils.views import totalize_data

import comercial.forms as forms
import comercial.models as models
import comercial.queries as queries


class Vendas(O2BaseGetPostView):

    _periodo_cols_options = None

    @property
    def periodo_cols_options(self):
        if self._periodo_cols_options:
            return self._periodo_cols_options

        self._periodo_cols_options = {
            '0': None,
            '3612': {
                '3 meses': '3:',
                '6 meses': '6:',
                '1 ano': '12:',
                '2 anos': '24:',
            },
            'a123': {
                'Mês atual': '0:',
                'Mês passado': '1:0',
                '2 meses atrás': '2:1',
                '3 meses atrás': '3:2',
            },
        }

        meta_cols = {}
        nfs = list(models.ModeloPassadoPeriodo.objects.filter(
            modelo_id=1).order_by('ordem').values())
        if len(nfs) == 0:
            return self._periodo_cols_options

        data_nfs = list(nfs)

        n_mes = 0
        hoje = datetime.today()
        mes = dec_month(hoje, 1)
        for i, row in enumerate(data_nfs):
            range = '{}:{}'.format(
                n_mes+row['meses'], n_mes)
            n_mes += row['meses']    

            mes_fim = mes.strftime("%m/%Y")
            mes = dec_months(mes, row['meses']-1)
            mes_ini = mes.strftime("%m/%Y")
            mes = dec_month(mes)
            if row['meses'] == 1:
                descr = mes_ini
            else:
                if mes_ini[-4:] == mes_fim[-4:]:
                    descr = '{} - {}'.format(mes_fim[:2], mes_ini)
                else:
                    descr = '{} - {}'.format(mes_fim, mes_ini)

            meta_cols[descr] = range

        if meta_cols:
            self._periodo_cols_options['meta'] = meta_cols

        return self._periodo_cols_options

    def __init__(self, *args, **kwargs):
        super(Vendas, self).__init__(*args, **kwargs)
        self.cleaned_data2self = True
        self.Form_class = forms.VendasForm
        self.template_name = 'comercial/vendas.html'
        self.title_name = 'Vendas'

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        if self.periodo not in self.periodo_cols_options:
            self.periodo = '0'
            self.context.update({
                'obs': 'Não há periodo de metas definido.',
            })
        periodo_cols=self.periodo_cols_options[self.periodo]      

        av = queries.AnaliseVendas(
            cursor, ref=self.ref, modelo=self.modelo, infor=self.infor, ordem=self.ordem,
            periodo_cols=periodo_cols,
            qtd_por_mes=(self.qtd_por_mes=='m'),
            com_venda=(self.lista=='venda'))
        data = av.data

        for row in data:
            if 'dt_max' in row:
                if row['dt_max'] is None:
                    row['dt_max'] = '-'
            if 'dt_min' in row:
                if row['dt_min'] is None:
                    row['dt_min'] = '-'
            if 'qtd_mes' not in row or row['qtd_mes'] is None:
                row['qtd_mes'] = 0

        infor_fields = {
            'nf': {
                'headers': ['Nota fiscal', 'Data'],
                'fields': ['nf', 'dt_min'],
            }
        }

        if self.infor in infor_fields:
            headers = infor_fields[self.infor]['headers']
        else:
            headers = [dict(self.Form_class.base_fields['infor'].choices)[self.infor]]

        if self.infor in infor_fields:
            fields = infor_fields[self.infor]['fields']
        else:
            fields = [self.infor]

        sum_fields = []
        if periodo_cols:
            style = untuple_keys_concat({
                tuple(range(2, 2+len(periodo_cols))): 'text-align: right;',
            })

            for col in periodo_cols:
                headers.append(col)
                fields.append(queries.str2col_name(col))
                sum_fields.append(queries.str2col_name(col))
        else:
            fields += ['qtd']
            sum_fields += ['qtd']
            if self.infor == 'nf':
                headers += ['Quantidade']
                style = {
                    3: 'text-align: right;',
                }
            else:
                headers += ['Total vendido']
                if self.qtd_por_mes == 'm':
                    headers += ['Última venda', 'Primeira venda', 'Quantidade por mês']
                    fields += ['dt_max', 'dt_min', 'qtd_mes']
                    style = untuple_keys_concat({
                        tuple(range(2, 6)): 'text-align: right;',
                    })
                else:
                    style = {
                        2: 'text-align: right;',
                    }

        if self.infor == 'nf':
            for row in data:
                row['nf|LINK'] = reverse(
                    'contabil:nota_fiscal__get', args=[row['nf']])

        if data:
            totalize_data(data, {
                'sum': sum_fields,
                'descr': {fields[0]: 'Total:'},
                'row_style': 'font-weight: bold;',
            })

        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'style': style,
        })
