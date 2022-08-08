from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from geral.functions import config_get_value
from utils.views import totalize_data
from utils.views import group_rowspan, totalize_grouped_data
from utils.table_defs import TableDefs

import produto.queries
import comercial.models

import lotes.models
from lotes.queries.pedido import faturavel_modelo as queries_faturavel_modelo
from lotes.forms.pedido import faturavel_modelo as forms_faturavel_modelo


class FaturavelModelo(View):

    def __init__(self, *args, **kwargs):
        super(FaturavelModelo, self).__init__(*args, **kwargs)
        self.Form_class = forms_faturavel_modelo.Form
        self.template_name = 'lotes/pedido/faturavel_modelo.html'
        self.title_name = 'Pedido faturável por modelo'

        self.table_defs = TableDefs(
            {
                'EMP_SIT': ["Sit. Emp."],
                'PEDIDO': ["Nº pedido"],
                'DATA': ["Data embarque"],
                'CLIENTE': ["Cliente"],
                'REF': ["Referência"],
                'QTD_EMP': ["Qtd. Emp", 'r'],
                'QTD_SOL': ["Qtd. Sol.", 'r'],
                'QTD': ["Qtd. pedida", 'r'],
                'QTD_FAT': ["Qtd. faturada", 'r'],
                'QTD_AFAT': ["Qtd. a faturar", 'r'],
                'PAC': ["Pacote", 'r'],
                'QTD_PAC': ["Qtd. pacote", 'r'],
                'FAT': ["Faturamento"],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )
        self.fields_ini = [
            'EMP_SIT',
            'PEDIDO',
            'DATA',
            'CLIENTE',
            'REF',
            'QTD_EMP',
            'QTD_SOL',
        ]
        self.fields_fat = [
            'QTD',
            'QTD_FAT',
        ]
        self.fields_afat = [
            'QTD_AFAT',
        ]
        self.fields_pac = [
            'PAC',
            'QTD_PAC',
        ]
        self.fields_fim = [
            'FAT',
        ]

    def mount_context(
            self, cursor, modelo, colecao, tam, cor,
            considera_lead, considera_pacote):
        context = {
            'modelo': modelo,
            'colecao': colecao,
            'tam': tam,
            'cor': cor,
            'considera_lead': considera_lead,
            'considera_pacote': considera_pacote,
        }
        if colecao:
            colecao = colecao.colecao
        
        lead = 0
        if modelo:
            lead = produto.queries.lead_de_modelo(cursor, modelo)

        lc_lead = 0
        if colecao:
            try:
                lc = lotes.models.RegraColecao.objects.get(colecao=colecao)
                lc_lead = lc.lead
            except lotes.models.RegraColecao.DoesNotExist:
                pass
        lead = max(lead, lc_lead)

        context.update({
            'lead': lead,
        })

        if considera_lead == 'n':
            lead = 0

        if lead == 0:
            busca_periodo = ''
            periodo = ''
        else:
            dias_alem_lead = config_get_value('DIAS-ALEM-LEAD', default=7)
            busca_periodo = lead + dias_alem_lead
            periodo = dias_alem_lead

        com_pac = considera_pacote == 's'

        data = queries_faturavel_modelo.query(
            cursor, modelo=modelo, periodo=':{}'.format(busca_periodo),
            cached=False, tam=tam, cor=cor, colecao=colecao, com_pac=com_pac)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Pedidos não encontrados',
            })
            return context

        pac_quant = {}
        if com_pac:
            pac_quant_data = comercial.models.MetaModeloReferencia.objects.filter(
                modelo=modelo,
                incl_excl='i',
            ).values('referencia', 'quantidade')
            if pac_quant_data:
                pac_quant = {
                    row['referencia']: row['quantidade']
                    for row in pac_quant_data
                }

        tot_qtd_fat = 0
        for row in data:
            row['PEDIDO|TARGET'] = '_blank'
            row['PEDIDO|LINK'] = reverse(
                'producao:pedido__get', args=[row['PEDIDO']])
            tot_qtd_fat += row['QTD_FAT']
            row['QTD_AFAT'] = row['QTD'] - row['QTD_FAT']
            if row['DATA'] is None:
                row['DATA'] = ''
            else:
                row['DATA'] = row['DATA'].date()
            if row['EMP_SIT_MIN'] == 0:
                row['EMP_SIT'] = 'Sem Emp.'
            else:
                if row['EMP_SIT_MIN'] == row['EMP_SIT_MAX']:
                    row['EMP_SIT'] = row['EMP_SIT_MIN']
                else:
                    row['EMP_SIT'] = f"{row['EMP_SIT_MIN']} a {row['EMP_SIT_MAX']}"
            if com_pac:
                if row['REF'] in pac_quant:
                    row['PAC'] = pac_quant[row['REF']]
                else:
                    row['PAC'] = 1
                row['QTD_PAC'] = row['QTD_AFAT'] * row['PAC']

        if com_pac:
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

        fields = self.fields_ini
        if tot_qtd_fat != 0:
            fields = fields + self.fields_fat
        fields = fields + self.fields_afat
        if com_pac:
            fields = fields + self.fields_pac
        fields = fields + self.fields_fim

        context.update(self.table_defs.hfs_dict(*fields))

        context.update({
            'periodo': periodo,
            'data': data,
            'group': group,
        })

        if lead != 0:
            data_pos = queries_faturavel_modelo.query(
                cursor, modelo=modelo, periodo='{}:'.format(busca_periodo),
                cached=False, colecao=colecao)
            if len(data_pos) != 0:
                for row in data_pos:
                    row['PEDIDO|TARGET'] = '_blank'
                    row['PEDIDO|LINK'] = reverse(
                        'producao:pedido__get', args=[row['PEDIDO']])
                    row['QTD_AFAT'] = row['QTD'] - row['QTD_FAT']
                    if row['DATA'] is None:
                        row['DATA'] = ''
                    else:
                        row['DATA'] = row['DATA'].date()

                totalize_data(data_pos, {
                    'sum': ['QTD_AFAT'],
                    'count': [],
                    'descr': {'REF': 'Total:'},
                    'row_style': 'font-weight: bold;',
                })

                if tot_qtd_fat == 0:
                    headers_pos = ['Nº do pedido', 'Data de embarque', 'Cliente',
                            'Referência', 'Quant. pedida', 'Faturamento']
                    fields_pos = ['PEDIDO', 'DATA', 'CLIENTE',
                            'REF', 'QTD_AFAT', 'FAT']
                    style_pos = {
                        5: 'text-align: right;',
                    }
                else:
                    headers_pos = ['Nº do pedido', 'Data de embarque', 'Cliente',
                            'Referência', 'Quant. pedida', 'Quant. faturada',
                            'Quant. a faturar', 'Faturamento']
                    fields_pos = ['PEDIDO', 'DATA', 'CLIENTE',
                            'REF', 'QTD', 'QTD_FAT',
                            'QTD_AFAT', 'FAT']
                    style_pos = {
                        5: 'text-align: right;',
                        6: 'text-align: right;',
                        7: 'text-align: right;',
                    }
                context.update({
                    'headers_pos': headers_pos,
                    'fields_pos': fields_pos,
                    'data_pos': data_pos,
                    'style_pos': style_pos,
                })

        return context

    def get(self, request, *args, **kwargs):
        if 'modelo' in kwargs:
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
        if 'modelo' in kwargs:
            form.data['modelo'] = kwargs['modelo']
        if form.is_valid():
            modelo = form.cleaned_data['modelo']
            colecao = form.cleaned_data['colecao']
            tam = form.cleaned_data['tam']
            cor = form.cleaned_data['cor']
            considera_lead = form.cleaned_data['considera_lead']
            considera_pacote = form.cleaned_data['considera_pacote']
            cursor = db_cursor_so(request)
            context.update(
                self.mount_context(
                    cursor, modelo, colecao, tam, cor, considera_lead, considera_pacote))
        context['form'] = form
        return render(request, self.template_name, context)
