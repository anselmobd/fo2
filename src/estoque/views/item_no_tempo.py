import datetime
from pprint import pprint

from django.db import connections
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from utils.views import totalize_data
from utils.functions import untuple_keys_concat
from utils.functions.views import cleanned_fields_to_context

import lotes.models
import lotes.queries.pedido
import lotes.queries.analise

from estoque import forms
from estoque import queries
from estoque.functions import (
    transfo2_num_doc,
    transfo2_num_doc_dt,
    )


class ItemNoTempo(View):

    Form_class = forms.ItemNoTempoForm
    template_name = 'estoque/item_no_tempo.html'
    title_name = 'Item no tempo'

    cleanned_fields_to_context = cleanned_fields_to_context

    def __init__(self):
        self.context = {'titulo': self.title_name}

    def mount_context(self):
        cursor = connections['so'].cursor()

        self.context.update({
            'item': '{ref}.{tam}.{cor}'.format(**self.context)
        })

        if self.context['periodo'] == '0':
            apartirde = None
        else:
            periodo = int(self.context['periodo'])
            delta = datetime.timedelta(days=-periodo*31)
            apartirde = datetime.date.today()+delta
        self.context.update({
            'apartirde': apartirde
        })

        estoque_list = queries.get_estoque_dep_ref_cor_tam(
            cursor, *(self.context[f] for f in [
                'deposito', 'ref', 'cor', 'tam']))
        if len(estoque_list) > 0:
            estoque = estoque_list[0]['estoque']
        else:
            estoque = 0

        self.context.update({
            'estoque': estoque,
            })

        dados = queries.item_no_tempo(
            cursor, *(self.context[f] for f in [
                'ref', 'tam', 'cor', 'deposito', 'apartirde']))

        for row in dados:
            if (row['doc'] // 1000000) == 702:
                row['data'] = transfo2_num_doc_dt(row['doc'])
                if apartirde is not None and row['data'].date() < apartirde:
                    row['data'] = None

        dados = [row for row in dados
                 if row['data'] is not None]

        if len(dados) == 0:
            self.context.update({'erro': 'Nenhuma transação'})

        dados = sorted(
            dados, key=lambda i: i['data'], reverse=True)

        dados_limpo = []
        row_key_anterior = []
        for row in dados:
            row_key = row.copy()
            del(row_key['data'])
            del(row_key['qtd'])
            del(row_key['qtd_sinal'])
            if self.context['agrupa'] == 'S' and row_key == row_key_anterior:
                dados_limpo[-1]['dt_ini'] = row['data']
                dados_limpo[-1]['conta'] += 1
                dados_limpo[-1]['qtd'] += row['qtd']
                dados_limpo[-1]['qtd_sinal'] += row['qtd_sinal']
            else:
                row['dt_ini'] = row['data']
                row['conta'] = 1
                dados_limpo.append(row)
            row_key_anterior = row_key
        dados = dados_limpo

        estoque_no_tempo = estoque
        for row in dados:
            row['estoque'] = estoque_no_tempo
            estoque_no_tempo -= row['qtd_sinal']

            if row['es'] == 'E':
                row['qtd_e'] = row['qtd']
                row['qtd_s'] = '.'
            else:
                row['qtd_e'] = '.'
                row['qtd_s'] = row['qtd']

            row['tipo'] = row['proc']
            tipo_doc = ''
            if (row['doc'] // 1000000) == 702:
                row['tipo'] = 'Ajuste por inventário'
                row['proc'] = '_'
            elif (row['doc'] // 1000000) == 802:
                row['tipo'] = 'Transferência entre depósitos'
                row['proc'] = '_'
                tipo_doc = '802'
            else:
                if row['proc'] in ('estq_f015'):
                    row['tipo'] = 'Movimentação de estoques'
                elif row['proc'] in ('estq_f950'):
                    row['tipo'] = 'Acerto de estoques'
                elif row['proc'] in ('fatu_f146'):
                    row['tipo'] = 'Cancelamento de NF de saída'
                    tipo_doc = 'nfs'
                elif row['proc'] in ('fatu_f194'):
                    row['tipo'] = 'Faturamento de pedido'
                    tipo_doc = 'nfs'
                elif row['proc'] in ('obrf_f015'):
                    row['tipo'] = 'Itens de NF de terceiros de entrada'
                    tipo_doc = 'nfe'
                elif row['proc'] in ('obrf_f025'):
                    row['tipo'] = 'Item de NF de saída'
                    tipo_doc = 'nfs'
                elif row['proc'] in ('obrf_f055'):
                    row['tipo'] = 'Item NF própria de entrada'
                    tipo_doc = 'nfe'
                elif row['proc'] in ('obrf_f060'):
                    row['tipo'] = 'Cancelamento de NF própria de entrada'
                    tipo_doc = 'nfe'
                elif row['proc'] in ('obrf_f484'):
                    row['tipo'] = 'Baixa da OC por pacote'
                    tipo_doc = 'op'
                elif row['proc'] in ('pcpc_f045'):
                    row['tipo'] = 'Produção de OC'
                    tipo_doc = 'op'
                elif row['proc'] in ('pcpc_f046'):
                    row['tipo'] = 'Estorno de Estágio da OP (Pacote)'
                    tipo_doc = 'op'
                elif row['proc'] in ('pcpc_f072'):
                    row['tipo'] = 'Baixa/Estorno da OC'
                    tipo_doc = 'op'
                elif row['proc'] in ('pcpc_f230'):
                    row['tipo'] = 'Baixa da OP por estagio'
                    tipo_doc = 'op'

            row['trans_descr'] = row['trans_descr'].capitalize()
            if tipo_doc == '':
                row['ped'] = '.'
                row['cliente'] = '.'
            else:
                row['doc|TARGET'] = '_blank'

            if tipo_doc == 'nfs':
                row['doc|LINK'] = reverse(
                    'contabil:nota_fiscal__get', args=[row['doc']])
            elif tipo_doc == 'op':
                row['doc|LINK'] = reverse(
                    'producao:op__get', args=[row['doc']])
            elif tipo_doc == '802':
                row['doc|LINK'] = reverse(
                    'estoque:lista_movs__get', args=[row['doc']])

            if row['ped'] is None or row['ped'] == 0:
                row['ped'] = '.'
            if row['ped'] != '.':
                row['ped|TARGET'] = '_blank'
                row['ped|LINK'] = reverse(
                    'producao:pedido__get', args=[row['ped']])
                if row['stat_ped'] != 0:
                    row['ped'] = f"{row['ped']}'{row['stat_ped']}"

            if row['cnpj_9'] == 0:
                row['cliente'] = '.'

            if row['cliente'] != '.':
                if row['fantasia'] is not None and row['fantasia'] != '':
                    row['cliente'] = row['fantasia']

            if row['data'] != row['dt_ini']:
                dt_ini = row['dt_ini'].strftime('%d/%m/%Y %H:%M:%S')
                if row['data'].date() == row['dt_ini'].date():
                    dt_fim_hora = row['data'].strftime('%H:%M:%S')
                    row['data'] = f"{dt_ini} - {dt_fim_hora}"
                else:
                    dt_fim = row['data'].strftime('%d/%m/%Y %H:%M:%S')
                    row['data'] = f"{dt_ini} - {dt_fim}"

        headers = ['Data/hora', 'Usuário', 'Tela', 'Tipo de movimentação',
                   'Trans.', 'Descrição', 'Cliente', 'Documento', 'Pedido']
        if self.context['agrupa'] == 'S':
            headers += ['Nº Trans.']
        headers += ['Entrada', 'Saída', 'Estoque']

        fields = ['data', 'usuario', 'proc', 'tipo',
                  'trans', 'trans_descr', 'cliente', 'doc', 'ped']
        if self.context['agrupa'] == 'S':
            fields += ['conta']
        fields += ['qtd_e', 'qtd_s', 'estoque']

        if self.context['agrupa'] == 'S':
            style = {10: 'text-align: center;',
                     11: 'color: green;',
                     12: 'color: brown;',
                     (7, 8, 11, 12, 13): 'text-align: right;'}
        else:
            style = {10: 'color: green;',
                     11: 'color: brown;',
                     (7, 8, 10, 11, 12): 'text-align: right;'}

        self.context.update({
            'headers': headers,
            'fields': fields,
            'style': untuple_keys_concat(style),
            'dados': dados,
            })

        p_dados = lotes.queries.pedido.pedido_faturavel_modelo(
            cursor, cached=False,
            **{f: self.context[f] for f in [
                'ref', 'cor', 'tam', 'deposito']}
            )

        qtd_ped = 0
        if len(p_dados) > 0:
            p_dados.insert(0, p_dados[0].copy())
            for i, row in enumerate(p_dados):
                if i == 0:
                    row['PEDIDO'] = 'Estoque atual'
                    row['DATA'] = ''
                    row['CLIENTE'] = ''
                    row['FAT'] = ''
                    row['QTD_AFAT'] = ''
                    estoque_no_tempo = estoque
                else:
                    row['PEDIDO|TARGET'] = '_blank'
                    row['PEDIDO|LINK'] = reverse(
                        'producao:pedido__get', args=[row['PEDIDO']])
                    row['DATA'] = row['DATA'].date()
                    row['QTD_AFAT'] = row['QTD'] - row['QTD_FAT']
                    qtd_ped += row['QTD_AFAT']
                    estoque_no_tempo -= row['QTD_AFAT']

                row['ESTOQUE'] = estoque_no_tempo

            self.context.update({
                'p_headers': [
                    'Nº do pedido', 'Data de embarque', 'Cliente',
                    'Faturamento', 'Quant. pedida', 'Estoque'],
                'p_fields': [
                    'PEDIDO', 'DATA', 'CLIENTE',
                    'FAT', 'QTD_AFAT', 'ESTOQUE'],
                'p_style': {
                    5: 'text-align: right;',
                    6: 'text-align: right;',
                    },
                'p_dados': p_dados,
                })

        oc_dados = lotes.queries.analise.quant_estagio(
            cursor, only=[57, 63], group='op',
            **{f: self.context[f] for f in [
                'ref', 'cor', 'tam', 'deposito']})

        qtd_op_cd = 0
        if len(oc_dados) > 0:

            for row in oc_dados:
                qtd_op_cd += row['QUANT']
                row['ORDEM_PRODUCAO|TARGET'] = '_blank'
                row['ORDEM_PRODUCAO|LINK'] = reverse(
                    'producao:op__get', args=[row['ORDEM_PRODUCAO']])
                if row['PEDIDO_VENDA'] == 0:
                    row['PEDIDO_VENDA'] = '.'
                else:
                    row['PEDIDO_VENDA|TARGET'] = '_blank'
                    row['PEDIDO_VENDA|LINK'] = reverse(
                        'producao:pedido__get', args=[row['PEDIDO_VENDA']])

            totalize_data(oc_dados, {
                'sum': ['QUANT'],
                'descr': {'PEDIDO_VENDA': 'Total:'}})

            self.context.update({
                'oc_headers': [
                    'OP', 'Pedido', 'Quantidade'],
                'oc_fields': [
                    'ORDEM_PRODUCAO', 'PEDIDO_VENDA', 'QUANT'],
                'oc_style': {
                    3: 'text-align: right;',
                    },
                'oc_dados': oc_dados,
                })

        op_dados = lotes.queries.analise.quant_estagio(
            cursor, less=[57, 63], group='op',
            **{f: self.context[f] for f in [
                'ref', 'cor', 'tam', 'deposito']})

        qtd_op_prod = 0
        if len(op_dados) > 0:

            for row in op_dados:
                qtd_op_prod += row['QUANT']
                row['ORDEM_PRODUCAO|TARGET'] = '_blank'
                row['ORDEM_PRODUCAO|LINK'] = reverse(
                    'producao:op__get', args=[row['ORDEM_PRODUCAO']])
                if row['PEDIDO_VENDA'] == 0:
                    row['PEDIDO_VENDA'] = '.'
                else:
                    row['PEDIDO_VENDA|TARGET'] = '_blank'
                    row['PEDIDO_VENDA|LINK'] = reverse(
                        'producao:pedido__get', args=[row['PEDIDO_VENDA']])

            totalize_data(op_dados, {
                'sum': ['QUANT'],
                'descr': {'PEDIDO_VENDA': 'Total:'}})

            self.context.update({
                'op_headers': [
                    'OP', 'Pedido', 'Quantidade'],
                'op_fields': [
                    'ORDEM_PRODUCAO', 'PEDIDO_VENDA', 'QUANT'],
                'op_style': {
                    3: 'text-align: right;',
                    },
                'op_dados': op_dados,
                })

        self.context.update({
            'estoque_futuro': estoque - qtd_ped + qtd_op_cd + qtd_op_prod
            })

    def get(self, request, *args, **kwargs):
        if 'deposito' in kwargs:
            return self.post(request, *args, **kwargs)
        self.context['form'] = self.Form_class()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        if 'deposito' in kwargs:
            initial = {
                "ref": kwargs['ref'],
                "cor": kwargs['cor'],
                "tam": kwargs['tam'],
                "deposito": kwargs['deposito'],
                "periodo": '6',
                "agrupa": 'S',
            }
            self.context['form'] = self.Form_class(initial)
        else:
            self.context['form'] = self.Form_class(request.POST)
        if self.context['form'].is_valid():
            self.cleanned_fields_to_context()
            self.context['form'] = self.Form_class(self.context)
            self.mount_context()
        return render(request, self.template_name, self.context)
