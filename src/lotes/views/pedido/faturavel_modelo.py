from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from geral.functions import config_get_value
from utils.views import group_rowspan, totalize_grouped_data
from utils.table_defs import TableDefs

import produto.queries
import comercial.models

import lotes.models
from lotes.queries.pedido import faturavel_modelo as queries_faturavel_modelo
from lotes.forms.pedido import faturavel_modelo as forms_faturavel_modelo


class FaturavelModelo(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(FaturavelModelo, self).__init__(*args, **kwargs)
        self.Form_class = forms_faturavel_modelo.Form
        self.template_name = 'lotes/pedido/faturavel_modelo.html'
        self.title_name = 'Pedido faturável por modelo'
        self.cleaned_data2self = True
        self.get_args = ['modelo']

        self.table_defs = TableDefs(
            {
                'EMP_SIT': ["Sit. Emp."],
                'PEDIDO': ["Nº pedido"],
                'DATA': ["Data embarque"],
                'CLIENTE': ["Cliente"],
                'REF': ["Referência"],
                'QTD_EMP': ["Qtd. Emp", 'r'],
                'QTD_SOL': ["Qtd. Sol.", 'r'],
                'QTD': ["Qtd. pedida", 'r', 1],
                'QTD_FAT': ["Qtd. faturada", 'r', 1],
                'QTD_AFAT': ["Qtd. a faturar", 'r'],
                'PAC': ["Pacote", 'r', 2],
                'QTD_PAC': ["Qtd. pacote", 'r', 2],
                'FAT': ["Faturamento"],
            },
            ['header', '+style', 'flags_bitmap'],
            style = {'_': 'text-align'},
        )

        self._pac_quant = None

    @property
    def pac_quant(self):
        if self._pac_quant is None:
            pac_quant_data = comercial.models.MetaModeloReferencia.objects.filter(
                modelo=self.modelo,
                incl_excl='i',
            ).values('referencia', 'quantidade')
            self._pac_quant = {
                row['referencia']: row['quantidade']
                for row in pac_quant_data
            } if pac_quant_data else {}
        return self._pac_quant

    def monta_dados(self, data):
        tot_qtd_fat = 0
        for row in data:
            row['PEDIDO|TARGET'] = '_blank'
            row['PEDIDO|LINK'] = reverse(
                'producao:pedido__get', args=[row['PEDIDO']])
            tot_qtd_fat += row['QTD_FAT']
            row['QTD_AFAT'] = row['QTD'] - row['QTD_FAT']
            row['DATA'] = row['DATA'].date() if row['DATA'] else ''
            if row['EMP_SIT_MIN'] == 0:
                row['EMP_SIT'] = 'Sem Emp.'
            else:
                if row['EMP_SIT_MIN'] == row['EMP_SIT_MAX']:
                    row['EMP_SIT'] = row['EMP_SIT_MIN']
                else:
                    row['EMP_SIT'] = f"{row['EMP_SIT_MIN']} a {row['EMP_SIT_MAX']}"
            if self.com_pac:
                if row['REF'] in self.pac_quant:
                    row['PAC'] = self.pac_quant[row['REF']]
                else:
                    row['PAC'] = 1
                row['QTD_PAC'] = row['QTD_AFAT'] * row['PAC']

        if self.com_pac:
            tot_sum_fields = ['QTD_EMP', 'QTD_SOL', 'QTD_PAC']
        else:
            tot_sum_fields = ['QTD_AFAT', 'QTD_EMP', 'QTD_SOL']

        group = ['EMP_SIT']
        totalize_grouped_data(data, {
            'group': group,
            'sum': tot_sum_fields,
            'count': [],
            'descr': {'PEDIDO': 'Total:'},
            'flags': ['NO_TOT_1'],
            'global_sum': tot_sum_fields,
            'global_descr': {'EMP_SIT': 'Total geral:'},
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(data, group)

        flags_bitmap =  (tot_qtd_fat != 0) + (self.com_pac * 2)
        dados = self.table_defs.hfs_dict(bitmap=flags_bitmap)
        dados.update({
            'data': data,
            'group': group,
        })
        return dados

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        codigo_colecao = self.colecao.colecao if self.colecao else None
        
        lead = 0
        if self.modelo:
            lead = produto.queries.lead_de_modelo(cursor, self.modelo)

        lc_lead = 0
        if self.colecao:
            try:
                lc = lotes.models.RegraColecao.objects.get(colecao=codigo_colecao)
                lc_lead = lc.lead
            except lotes.models.RegraColecao.DoesNotExist:
                pass
        lead = max(lead, lc_lead)

        self.context.update({
            'lead': lead,
        })

        if self.considera_lead == 's':
            dias_alem_lead = config_get_value('DIAS-ALEM-LEAD', default=7)
            self.context['dias_alem_lead'] = dias_alem_lead
            busca_periodo = lead + dias_alem_lead
        else:
            busca_periodo = ''

        self.com_pac = self.considera_pacote == 's'

        data = queries_faturavel_modelo.query(
            cursor, modelo=self.modelo, periodo=':{}'.format(busca_periodo),
            cached=False, tam=self.tam, cor=self.cor,
            colecao=codigo_colecao, com_pac=self.com_pac)
        if data:
            self.context.update({
                'dados_pre': self.monta_dados(data),
            })

        if self.considera_lead == 's':
            data_pos = queries_faturavel_modelo.query(
                cursor, modelo=self.modelo, periodo='{}:'.format(busca_periodo),
                cached=False, tam=self.tam, cor=self.cor,
                colecao=codigo_colecao, com_pac=self.com_pac)
            if data_pos:
                self.context.update({
                    'dados_pos': self.monta_dados(data_pos),
                })
