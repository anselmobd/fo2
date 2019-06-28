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

    def mount_context(self, cursor, tipo_roteiro, cliente, deposito):
        context = {
            'tipo_roteiro': tipo_roteiro,
            'deposito': deposito,
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

        data = models.totais_estagios(cursor, tipo_roteiro, cnpj9, deposito)
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

        produtos = ['PA', 'PG', 'PB']
        headers = mount_dict(
            ['Estágio'], ['Lotes', 'Itens', 'Peças'],
            ' ', produtos + ['MD', 'MP', ''])
        quant_fields = mount_dict(
            [], ['LOTES', 'QUANT', 'PECAS'],
            '_', produtos + ['MD', 'MP', ''])
        fields = ['ESTAGIO'] + quant_fields

        giro_lotes = mount_dict([], ['LOTES'], '_', produtos)
        giro_quant = mount_dict([], ['QUANT'], '_', produtos)
        giro_pecas = mount_dict([], ['PECAS'], '_', produtos)
        nao_giro_lotes = mount_dict([], ['LOTES'], '_', ['MD', 'MP'])
        nao_giro_quant = mount_dict([], ['QUANT'], '_', ['MD', 'MP'])
        nao_giro_pecas = mount_dict([], ['PECAS'], '_', ['MD', 'MP'])
        nao_giro_fields = nao_giro_lotes+nao_giro_quant+nao_giro_pecas

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

        def red_columns(dicti):
            for field in ['LOTES', 'QUANT', 'PECAS']:
                dicti['{}|STYLE'.format(field)] = 'color: red;'

        def init_total(titulo, dicti, subtotal=False):
            total_dict = dicti[0].copy()
            total_dict['ESTAGIO'] = titulo
            for field in quant_fields:
                total_dict[field] = 0
            if not subtotal:
                total_dict['|STYLE'] = 'font-weight: bold;'
                red_columns(total_dict)
            return total_dict

        def soma_fields(tot_dict, data, fields):
            for row in data:
                for field in fields:
                    tot_dict[field] += row[field]

        data_p = [
            r for r in data if r['CODIGO_ESTAGIO'] in estagio_programacao]
        if len(data_p) > 0:
            red_columns(data_p[0])
            context.update({
                'data_p': data_p,
            })

        data_d = [
            r for r in data if r['CODIGO_ESTAGIO'] not in estagio_nao_producao]
        total_producao_giro = None
        if len(data_d) > 0:
            total_producao = init_total('Total em produção', data_d)
            total_producao_giro = init_total(
                'Total em produção (giro)', data_d, subtotal=True)
            soma_fields(total_producao, data_d, quant_fields)
            soma_fields(
                total_producao_giro, data_d, giro_lotes+giro_quant+giro_pecas)
            data_d.append(total_producao)
            context.update({
                'data_d': data_d,
            })

        data_e = [r for r in data if r['CODIGO_ESTAGIO'] in estagio_estoque]
        total_estoque_giro = None
        if len(data_e) > 0:
            total_estoque = init_total('Total em estoque', data_e)
            total_estoque_giro = init_total(
                'Total em estoque (giro)', data_e, subtotal=True)
            soma_fields(total_estoque, data_e, quant_fields)
            soma_fields(
                total_estoque_giro, data_e, giro_lotes+giro_quant+giro_pecas)
            data_e.append(total_estoque)
            context.update({
                'data_e': data_e,
            })

        data_v = [
            r for r in data if r['CODIGO_ESTAGIO'] in estagio_vendido]
        if len(data_v) > 0:
            red_columns(data_v[0])
            context.update({
                'data_v': data_v,
            })

        total_geral = init_total('Total geral', data)
        soma_fields(total_geral, data, quant_fields)
        context.update({
            'data_t': [total_geral],
        })

        def soma_row_columns(dicti, tot_field, fields):
            for column in fields:
                dicti[tot_field] += dicti[column]

        def soma_os_3_totais(dicti):
            soma_row_columns(dicti, 'LOTES', giro_lotes)
            soma_row_columns(dicti, 'QUANT', giro_quant)
            soma_row_columns(dicti, 'PECAS', giro_pecas)

        data_giro = []
        if total_producao_giro is not None:
            soma_os_3_totais(total_producao_giro)
            data_giro.append(total_producao_giro)
        if total_estoque_giro is not None:
            soma_os_3_totais(total_estoque_giro)
            data_giro.append(total_estoque_giro)

        if len(data_giro) > 0:
            total_giro = init_total('Total em giro', data_giro)
            soma_fields(total_giro, data_giro, quant_fields)
            data_giro.append(total_giro)

            headers_g = headers.copy()
            for field in nao_giro_fields:
                headers_g[fields.index(field)] = '-'
            for row in data_giro:
                for field in nao_giro_fields:
                    row[field] = ' '

            context.update({
                'headers_g': headers_g,
                'data_g': data_giro,
            })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        tipo_roteiro = 'p'
        cliente = ''
        deposito = ''
        cursor = connections['so'].cursor()
        context.update(
            self.mount_context(cursor, tipo_roteiro, cliente, deposito))
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            tipo_roteiro = form.cleaned_data['tipo_roteiro']
            cliente = form.cleaned_data['cliente']
            deposito = form.cleaned_data['deposito']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, tipo_roteiro, cliente, deposito))
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
