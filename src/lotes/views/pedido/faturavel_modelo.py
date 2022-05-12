from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from geral.functions import config_get_value
from utils.views import totalize_data

import produto.queries

import lotes.forms as forms
import lotes.models
import lotes.queries as queries


class PedidoFaturavelModelo(View):
    Form_class = forms.BuscaPedidoForm
    template_name = 'lotes/pedido_faturavel_modelo.html'
    title_name = 'Pedido faturável por modelo'

    def mount_context(self, cursor, modelo, colecao, tam, cor, considera_lead):
        context = {
            'modelo': modelo,
            'colecao': colecao,
            'tam': tam,
            'cor': cor,
            'considera_lead': considera_lead,
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

        data = queries.pedido.pedido_faturavel_modelo(
            cursor, modelo=modelo, periodo=':{}'.format(busca_periodo),
            cached=False, tam=tam, cor=cor, colecao=colecao)
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
                    'descr': {'REF': 'Total:'}})

                context.update({
                    'data_pos': data_pos,
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
            cursor = db_cursor_so(request)
            context.update(
                self.mount_context(cursor, modelo, colecao, tam, cor, considera_lead))
        context['form'] = form
        return render(request, self.template_name, context)
