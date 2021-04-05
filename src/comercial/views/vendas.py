from pprint import pprint
from datetime import datetime

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.functions import dec_month, dec_months

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
        self.Form_class = forms.VendasForm
        self.template_name = 'comercial/vendas.html'
        self.title_name = 'Vendas'

    def mount_context(self):
        ref = self.form.cleaned_data['ref']
        modelo = self.form.cleaned_data['modelo']
        infor = self.form.cleaned_data['infor']
        ordem = self.form.cleaned_data['ordem']
        periodo = self.form.cleaned_data['periodo']
        qtd_por_mes = self.form.cleaned_data['qtd_por_mes']

        cursor = db_cursor_so(self.request)

        if periodo not in self.periodo_cols_options:
            periodo = '0'
            self.context.update({
                'obs': 'Não há periodo de metas definido.',
            })
        periodo_cols=self.periodo_cols_options[periodo]      

        av = queries.AnaliseVendas(
            cursor, ref=ref, modelo=modelo, infor=infor, ordem=ordem,
            periodo_cols=periodo_cols, qtd_por_mes=qtd_por_mes=='m')
        data = av.data

        if infor == "ref":
            headers = ['Referência']
            fields = ['ref']
        elif infor == "tam":
            headers = ['Tamanho']
            fields = ['tam']
        elif infor == "cor":
            headers = ['Cor']
            fields = ['cor']
        else:
            headers = ['Modelo']
            fields = ['modelo']

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
