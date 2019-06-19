from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.urls import reverse
from django.views import View

import produto.queries

import lotes.forms as forms
import lotes.models as models


class TotalEstagio(View):
    Form_class = forms.TotaisEstagioForm
    template_name = 'lotes/total_estagio.html'
    title_name = 'Totais gerais dos estágios'

    def mount_context(self, cursor, tipo_roteiro, cliente):
        context = {
            'tipo_roteiro': tipo_roteiro,
        }

        if cliente:
            data_c = produto.queries.busca_cliente_de_produto(cursor, cliente)
            if len(data_c) == 1:
                row = data_c[0]
                cnpj9 = row['cnpj9']
                cliente_full = '{:08d}/{:04d}-{:02d} {}'.format(
                    row['cnpj9'],
                    row['cnpj4'],
                    row['cnpj2'],
                    row['cliente'],
                )
                context.update({
                    'cliente': cliente,
                    'cliente_full': cliente_full,
                })
            else:
                context.update({
                    'msg_erro': 'Cliente não encontrado',
                })
                return context
        else:
            cnpj9 = None

        data = models.totais_estagios(cursor, tipo_roteiro, cnpj9)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Sem quantidades',
            })
            return context

        headers = ['Estágio',
                   'Lotes PA', 'Lotes PG', 'Lotes PB', 'Lotes MD', 'Lotes MP',
                   'Lotes',
                   'Itens PA', 'Itens PG', 'Itens PB', 'Itens MD', 'Itens MP',
                   'Itens',
                   'Peças PA', 'Peças PG', 'Peças PB', 'Peças MD', 'Peças MP',
                   'Peças',
                   ]
        fields = ['ESTAGIO',
                  'LOTES_PA', 'LOTES_PG', 'LOTES_PB', 'LOTES_MD', 'LOTES_MP',
                  'LOTES',
                  'QUANT_PA', 'QUANT_PG', 'QUANT_PB', 'QUANT_MD', 'QUANT_MP',
                  'QUANT',
                  'PECAS_PA', 'PECAS_PG', 'PECAS_PB', 'PECAS_MD', 'PECAS_MP',
                  'PECAS',
                  ]
        style_r = 'text-align: right;'
        style_bl = 'border-left-style: solid; border-left-width: ' \
            'thin; border-color: lightgray;'
        style_b = 'font-weight: bold;'
        style_number = style_r + style_bl
        style_total = style_number + style_b
        style = {}
        for i in range(2, 20):
            style[i] = style_number
        style.update({
             7: style_total,
             13: style_total,
             19: style_total,
        })
        quant_fields = [
            'LOTES_PA', 'QUANT_PA', 'PECAS_PA',
            'LOTES_PG', 'QUANT_PG', 'PECAS_PG',
            'LOTES_PB', 'QUANT_PB', 'PECAS_PB',
            'LOTES_MD', 'QUANT_MD', 'PECAS_MD',
            'LOTES_MP', 'QUANT_MP', 'PECAS_MP',
            'LOTES', 'QUANT', 'PECAS']
        giro_lotes = [
            'LOTES_PA',
            'LOTES_PG',
            'LOTES_PB',
            'LOTES_MD']
        giro_quant = [
            'QUANT_PA',
            'QUANT_PG',
            'QUANT_PB',
            'QUANT_MD']
        giro_pecas = [
            'PECAS_PA',
            'PECAS_PG',
            'PECAS_PB',
            'PECAS_MD']

        estagio_programacao = [3]
        estagio_estoque = [57, 60, 63]
        estagio_vendido = [66]
        estagio_nao_producao = \
            estagio_programacao + estagio_estoque + estagio_vendido

        data_p = [
            r for r in data if r['CODIGO_ESTAGIO'] in estagio_programacao]
        for row in data_p:
            for field in quant_fields:
                if field in ['LOTES', 'QUANT', 'PECAS']:
                    row['{}|STYLE'.format(field)] = 'color: red;'
        context.update({
            'headers_p': headers,
            'fields_p': fields,
            'data_p': data_p,
            'style_p': style,
        })

        total_giro = data[0].copy()
        total_giro['ESTAGIO'] = 'Total em produção e em estoque'
        total_giro['|STYLE'] = 'font-weight: bold;'
        for field in quant_fields:
            total_giro[field] = 0

        data_d = [
            r for r in data if r['CODIGO_ESTAGIO'] not in estagio_nao_producao]
        total_producao = data[0].copy()
        total_producao['ESTAGIO'] = 'Total em produção'
        total_producao['|STYLE'] = 'font-weight: bold;'
        for field in quant_fields:
            total_producao[field] = 0
        for row in data_d:
            for field in quant_fields:
                total_producao[field] += row[field]
                if field in ['LOTES', 'QUANT', 'PECAS']:
                    total_producao['{}|STYLE'.format(field)] = 'color: red;'
            for field in quant_fields:
                if field in giro_lotes+giro_quant+giro_pecas:
                    total_giro[field] += row[field]
                if field in ['LOTES', 'QUANT', 'PECAS']:
                    total_giro['{}|STYLE'.format(field)] = 'color: red;'
        data_d.append(total_producao)
        context.update({
            'headers_d': headers,
            'fields_d': fields,
            'data_d': data_d,
            'style_d': style,
        })

        data_e = [
            r for r in data if r['CODIGO_ESTAGIO'] in estagio_estoque]
        total_estoque = data[0].copy()
        total_estoque['ESTAGIO'] = 'Total em estoque'
        total_estoque['|STYLE'] = 'font-weight: bold;'
        for field in quant_fields:
            total_estoque[field] = 0
        for row in data_e:
            for field in quant_fields:
                total_estoque[field] += row[field]
                if field in ['LOTES', 'QUANT', 'PECAS']:
                    total_estoque['{}|STYLE'.format(field)] = 'color: red;'
            for field in quant_fields:
                if field in giro_lotes+giro_quant+giro_pecas:
                    total_giro[field] += row[field]
                if field in ['LOTES', 'QUANT', 'PECAS']:
                    total_giro['{}|STYLE'.format(field)] = 'color: red;'
        data_e.append(total_estoque)
        context.update({
            'headers_e': headers,
            'fields_e': fields,
            'data_e': data_e,
            'style_e': style,
        })

        data_v = [
            r for r in data if r['CODIGO_ESTAGIO'] in estagio_vendido]
        for row in data_v:
            for field in quant_fields:
                if field in ['LOTES', 'QUANT', 'PECAS']:
                    row['{}|STYLE'.format(field)] = 'color: red;'
        context.update({
            'headers_v': headers,
            'fields_v': fields,
            'data_v': data_v,
            'style_v': style,
        })

        total_geral = data[0].copy()
        total_geral['ESTAGIO'] = 'Total geral'
        total_geral['|STYLE'] = 'font-weight: bold;'
        for field in quant_fields:
            total_geral[field] = 0
        for row in data:
            for field in quant_fields:
                total_geral[field] += row[field]
                if field in ['LOTES', 'QUANT', 'PECAS']:
                    total_geral['{}|STYLE'.format(field)] = 'color: red;'
        context.update({
            'headers_t': headers,
            'data_t': [total_geral],
            'fields_t': fields,
            'style_t': style,
        })

        for column in giro_lotes:
            total_giro['LOTES'] += total_giro[column]
        for column in giro_quant:
            total_giro['QUANT'] += total_giro[column]
        for column in giro_pecas:
            total_giro['PECAS'] += total_giro[column]
        headers_g = headers.copy()
        headers_g[fields.index('LOTES_MP')] = '-'
        headers_g[fields.index('QUANT_MP')] = '-'
        headers_g[fields.index('PECAS_MP')] = '-'
        total_giro['LOTES_MP'] = ' '
        total_giro['QUANT_MP'] = ' '
        total_giro['PECAS_MP'] = ' '
        context.update({
            'headers_g': headers_g,
            'data_g': [total_giro],
            'fields_g': fields,
            'style_g': style,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        tipo_roteiro = 'p'
        cliente = ''
        cursor = connections['so'].cursor()
        context.update(self.mount_context(cursor, tipo_roteiro, cliente))
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            tipo_roteiro = form.cleaned_data['tipo_roteiro']
            cliente = form.cleaned_data['cliente']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, tipo_roteiro, cliente))
        context['form'] = form
        return render(request, self.template_name, context)


class QuantEstagio(View):
    Form_class = forms.QuantEstagioForm
    template_name = 'lotes/quant_estagio.html'
    title_name = 'Quantidades por estágio'

    def mount_context(self, cursor, estagio, ref, tipo):
        context = {
            'estagio': estagio,
            'ref': ref,
            'tipo': tipo,
        }

        data = models.quant_estagio(cursor, estagio, ref, tipo)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Sem produtos no estágio',
            })
            return context

        total = data[0].copy()
        total['REF'] = ''
        total['TAM'] = ''
        total['COR'] = 'Total:'
        total['|STYLE'] = 'font-weight: bold;'
        quant_fields = ['LOTES', 'QUANT']
        for field in quant_fields:
            total[field] = 0
        for row in data:
            for field in quant_fields:
                total[field] += row[field]
        data.append(total)
        context.update({
            'headers': ('Produto', 'Tamanho', 'Cor', 'Lotes', 'Quantidade'),
            'fields': ('REF', 'TAM', 'COR', 'LOTES', 'QUANT'),
            'data': data,
            'style': {4: 'text-align: right;',
                      5: 'text-align: right;'},
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'estagio' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'estagio' in kwargs:
            form.data['estagio'] = kwargs['estagio']
        if form.is_valid():
            estagio = form.cleaned_data['estagio']
            ref = form.cleaned_data['ref']
            tipo = form.cleaned_data['tipo']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, estagio, ref, tipo))
        context['form'] = form
        return render(request, self.template_name, context)
