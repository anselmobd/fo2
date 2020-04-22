from pprint import pprint
import copy

from django.shortcuts import render
from django.db import connections
from django.urls import reverse
from django.views import View

from geral.functions import config_get_value
from utils.views import totalize_grouped_data, totalize_data, group_rowspan

import produto.queries

import lotes.forms as forms
import lotes.models as models
import lotes.queries as queries


class Pedido(View):
    Form_class = forms.PedidoForm
    template_name = 'lotes/pedido.html'
    title_name = 'Pedido'

    def mount_context(self, cursor, pedido):
        context = {'pedido': pedido}

        # informações gerais
        data = models.ped_inform(cursor, pedido)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Pedido não encontrado',
            })
        else:
            for row in data:
                row['DT_EMISSAO'] = row['DT_EMISSAO'].date()
                row['DT_EMBARQUE'] = row['DT_EMBARQUE'].date()
                if row['OBSERVACAO'] is None:
                    row['OBSERVACAO'] = '-'
            context.update({
                'headers': ('Data de emissão', 'Data de embarque',
                            'Cliente', 'Código do pedido no cliente'),
                'fields': ('DT_EMISSAO', 'DT_EMBARQUE',
                           'CLIENTE', 'PEDIDO_CLIENTE'),
                'data': data,
            })
            context.update({
                'headers2': ('Status do pedido', 'Situação da venda',
                             'Observação'),
                'fields2': ('STATUS_PEDIDO', 'SITUACAO_VENDA',
                            'OBSERVACAO'),
                'data2': data,
            })

            # Depósitos
            d_data = models.ped_dep_qtd(cursor, pedido)
            context.update({
                'd_headers': ('Depósito', 'Quantidade'),
                'd_fields': ('DEPOSITO', 'QTD'),
                'd_data': d_data,
            })

            # OPs
            o_data = models.ped_op(cursor, pedido)
            for row in o_data:
                row['ORDEM_PRODUCAO|LINK'] = '/lotes/op/{}'.format(
                    row['ORDEM_PRODUCAO'])
                row['REFERENCIA_PECA|LINK'] = reverse(
                    'produto:ref__get', args=[row['REFERENCIA_PECA']])
                if row['ORDEM_PRINCIPAL'] == 0:
                    row['ORDEM_PRINCIPAL'] == ''
                else:
                    row['ORDEM_PRINCIPAL|LINK'] = '/lotes/op/{}'.format(
                        row['ORDEM_PRINCIPAL'])
                row['DT_DIGITACAO'] = row['DT_DIGITACAO'].date()
                if row['DT_CORTE'] is None:
                    row['DT_CORTE'] = '-'
                else:
                    row['DT_CORTE'] = row['DT_CORTE'].date()
                if row['SITUACAO'] == 9:
                    row['SITUACAO'] = 'Cancelada'
                else:
                    row['SITUACAO'] = 'Ativa'
            context.update({
                'o_headers': ('Stuação', 'OP', 'Tipo',
                              'Referência', 'OP principal', 'Quantidade',
                              'Data Digitação', 'Data Corte'),
                'o_fields': ('SITUACAO', 'ORDEM_PRODUCAO', 'TIPO',
                             'REFERENCIA_PECA', 'ORDEM_PRINCIPAL', 'QTD',
                             'DT_DIGITACAO', 'DT_CORTE'),
                'o_data': o_data,
            })

            # NFs
            nf_data = models.ped_nf(cursor, pedido)
            for row in nf_data:
                row['NF|LINK'] = reverse(
                    'contabil:nota_fiscal__get', args=[row['NF']])
                if row['SITUACAO'] == 1:
                    row['SITUACAO'] = 'Ativa'
                else:
                    row['SITUACAO'] = 'Cancelada'

                if row['NF_DEVOLUCAO'] is None:
                    row['NF_DEVOLUCAO'] = '-'
                else:
                    row['SITUACAO'] += '/Devolvida'

            context.update({
                'nf_headers': ('NF', 'Data', 'Situação', 'Valor',
                               'NF Devolução'),
                'nf_fields': ('NF', 'DATA', 'SITUACAO', 'VALOR',
                              'NF_DEVOLUCAO'),
                'nf_data': nf_data,
            })

            # Grade
            g_header, g_fields, g_data, g_total = queries.pedido.sortimento(
                cursor, pedido=pedido)
            if len(g_data) != 0:
                g_style = {}
                for i in range(1, len(g_fields)):
                    i_column = i + 1
                    g_style[i_column] = \
                        'border-left-style: solid;' \
                        'border-left-width: thin;' \
                        'text-align: right;'

                context.update({
                    'g_headers': g_header,
                    'g_fields': g_fields,
                    'g_data': g_data,
                    'g_style': g_style,
                    'g_total': g_total,
                })

        return context

    def get(self, request, *args, **kwargs):
        if 'pedido' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'pedido' in kwargs:
            form.data['pedido'] = kwargs['pedido']
        if form.is_valid():
            pedido = form.cleaned_data['pedido']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, pedido))
        context['form'] = form
        return render(request, self.template_name, context)


class PedidoFaturavelModelo(View):
    Form_class = forms.BuscaPedidoForm
    template_name = 'lotes/pedido_faturavel_modelo.html'
    title_name = 'Pedido faturável por modelo'

    def mount_context(self, cursor, modelo):
        context = {
            'modelo': modelo,
        }

        lead = produto.queries.lead_de_modelo(cursor, modelo)

        context.update({
            'lead': lead,
        })
        if lead == 0:
            busca_periodo = ''
            periodo = ''
        else:
            dias_alem_lead = config_get_value('DIAS-ALEM-LEAD', default=7)
            busca_periodo = lead + dias_alem_lead
            periodo = dias_alem_lead

        data = queries.pedido.pedido_faturavel_modelo(
            cursor, modelo=modelo, periodo=':{}'.format(busca_periodo),
            cached=False)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Pedidos não encontrados',
            })
            return context

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

        totalize_data(data, {
            'sum': ['QTD_AFAT'],
            'descr': {'REF': 'Total:'}})

        if tot_qtd_fat == 0:
            headers = ['Nº do pedido', 'Data de embarque', 'Cliente',
                       'Referência', 'Quant. pedida', 'Faturamento']
            fields = ['PEDIDO', 'DATA', 'CLIENTE',
                      'REF', 'QTD_AFAT', 'FAT']
            style = {
                5: 'text-align: right;',
            }
        else:
            headers = ['Nº do pedido', 'Data de embarque', 'Cliente',
                       'Referência', 'Quant. pedida', 'Quant. faturada',
                       'Quant. a faturar', 'Faturamento']
            fields = ['PEDIDO', 'DATA', 'CLIENTE',
                      'REF', 'QTD', 'QTD_FAT',
                      'QTD_AFAT', 'FAT']
            style = {
                5: 'text-align: right;',
                6: 'text-align: right;',
                7: 'text-align: right;',
            }

        context.update({
            'periodo': periodo,
            'headers': headers,
            'fields': fields,
            'data': data,
            'style': style,
        })

        if lead != 0:
            data_pos = queries.pedido.pedido_faturavel_modelo(
                cursor, modelo=modelo, periodo='{}:'.format(busca_periodo),
                cached=False)
            if len(data_pos) != 0:
                for row in data_pos:
                    row['PEDIDO|TARGET'] = '_blank'
                    row['PEDIDO|LINK'] = reverse(
                        'producao:pedido__get', args=[row['PEDIDO']])
                    if row['DATA'] is None:
                        row['DATA'] = ''
                    else:
                        row['DATA'] = row['DATA'].date()

                totalize_data(data_pos, {
                    'sum': ['QTD'],
                    'count': [],
                    'descr': {'REF': 'Total:'}})

                context.update({
                    'data_pos': data_pos,
                })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            modelo = form.cleaned_data['modelo']
            cursor = connections['so'].cursor()
            context.update(
                self.mount_context(cursor, modelo))
        context['form'] = form
        return render(request, self.template_name, context)
