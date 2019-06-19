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

        def mount_dict(dic, pre, sep, pos):
            for pr in pre:
                for po in pos:
                    dic.append(pr+(sep if po else '')+po)
            return dic

        pa_a_md = ['PA', 'PG', 'PB', 'MD']
        headers = mount_dict(
            ['Estágio'], ['Lotes', 'Itens', 'Peças'],
            ' ', pa_a_md + ['MP', ''])
        quant_fields = mount_dict(
            [], ['LOTES', 'QUANT', 'PECAS'],
            '_', pa_a_md + ['MP', ''])
        fields = ['ESTAGIO'] + quant_fields

        giro_lotes = mount_dict([], ['LOTES'], '_', pa_a_md)
        giro_quant = mount_dict([], ['QUANT'], '_', pa_a_md)
        giro_pecas = mount_dict([], ['PECAS'], '_', pa_a_md)

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

        context.update({
            'headers': headers,
            'fields': fields,
            'style': style,
        })

        estagio_programacao = [3]
        estagio_estoque = [57, 60, 63]
        estagio_vendido = [66]
        estagio_nao_producao = \
            estagio_programacao + estagio_estoque + estagio_vendido

        def red_columns(dict):
            for field in ['LOTES', 'QUANT', 'PECAS']:
                dict['{}|STYLE'.format(field)] = 'color: red;'

        def init_total(titulo, dict):
            total_dict = dict[0].copy()
            total_dict['ESTAGIO'] = titulo
            total_dict['|STYLE'] = 'font-weight: bold;'
            for field in quant_fields:
                total_dict[field] = 0
            red_columns(total_dict)
            return total_dict

        def soma_fields(tot_dict, data, fields):
            for row in data:
                for field in fields:
                    tot_dict[field] += row[field]

        data_p = [
            r for r in data if r['CODIGO_ESTAGIO'] in estagio_programacao]
        red_columns(data_p[0])
        context.update({
            'data_p': data_p,
        })

        total_giro = init_total('Total em produção e em estoque', data)

        data_d = [
            r for r in data if r['CODIGO_ESTAGIO'] not in estagio_nao_producao]
        total_producao = init_total('Total em produção', data)
        soma_fields(total_producao, data_d, quant_fields)
        soma_fields(total_giro, data_d, giro_lotes+giro_quant+giro_pecas)
        data_d.append(total_producao)
        context.update({
            'data_d': data_d,
        })

        data_e = [r for r in data if r['CODIGO_ESTAGIO'] in estagio_estoque]
        total_estoque = init_total('Total em estoque', data)
        soma_fields(total_estoque, data_e, quant_fields)
        soma_fields(total_giro, data_e, giro_lotes+giro_quant+giro_pecas)
        data_e.append(total_estoque)
        context.update({
            'data_e': data_e,
        })

        data_v = [
            r for r in data if r['CODIGO_ESTAGIO'] in estagio_vendido]
        red_columns(data_v[0])
        context.update({
            'data_v': data_v,
        })

        total_geral = init_total('Total geral', data)
        soma_fields(total_geral, data, quant_fields)
        context.update({
            'data_t': [total_geral],
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
