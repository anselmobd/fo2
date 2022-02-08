from pprint import pprint
from operator import itemgetter

from django.utils import timezone
from django.shortcuts import render
from django.views import View
from django.urls import reverse

from base.paginator import paginator_basic
from utils.functions import ldict_coalesce, ldict_if_else
from utils.functions.dict import dict_firsts

from logistica.models import NotaFiscal
from logistica.forms import NotafiscalRelForm


class NotafiscalRel(View):
    Form_class = NotafiscalRelForm
    template_name = 'logistica/notafiscal_rel.html'
    title_name = 'Consulta de datas de NF'

    def mount_context(self, form, form_obj):
        context = dict(form)
        context.update({
            'data_saida': dict(form_obj.fields['data_saida'].choices)[form['data_saida']],
            'posicao': '' if form['posicao'] is None else form['posicao'].nome,
        })

        select = NotaFiscal.objects.xfilter(**form)
        data = list(select.values(
            *[f.get_attname() for f in NotaFiscal._meta.get_fields()],
            'posicao__nome',
        ))

        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma NF encontrada',
            })
        else:

            context.update({
                'data_length': len(data),
            })

            for row in data:
                if row['saida'] is None:
                    row['atraso'] = (
                        timezone.now() - row['faturamento']).days
                else:
                    row['atraso'] = (
                        row['saida'] - row['faturamento'].date()).days

            if form['ordem'] == 'A':
                data.sort(key=itemgetter('atraso'), reverse=True)

            data = paginator_basic(data, form['por_pagina'], form['page'])

            for row in data:
                row['numero|LINK'] = reverse(
                    'logistica:notafiscal_nf', args=[row['numero']])
                row['numero|TARGET'] = '_BLANK'
                if row['quantidade']:
                    row['quantidade'] = int(round(row['quantidade']))
                row['tipo'] = dict(NotaFiscal.TIPO_NOTA)[row['tipo']]

            ldict_coalesce(data,
                [
                    [['saida', 'entrega', 'quantidade'], '-'],
                    [['observacao', 'ped_cliente'], ' '],
                    [['nf_devolucao'], 'Não'],
                ]
            )
            ldict_if_else(data,
                [
                    [['confirmada', 'natu_venda'], 'Sim', 'Não'],
                    [['ativa'], 'Ativa', 'Cancelada'],
                ]
            )

            style_center = 'text-align: center;'
            style_right = 'text-align: right;'
            faturamento_cor = 'color: green !important;'
            saida_cor = 'color: darkorange !important;'
            entrega_cor = 'color: blue !important;'
            observacao_cor = 'color: red !important;'
            columns = {
                'numero':
                    'NF',
                'faturamento':
                    ('Faturamento', faturamento_cor),
                'natu_venda':
                    ('Venda', style_center),
                'tipo':
                    ('Tipo', style_center),
                'ativa':
                    ('Ativa', style_center),
                'nf_devolucao':
                    ('Devolvida', style_center),
                'posicao__nome':
                    ('Posição', style_center),
                'atraso':
                    ('Atraso', style_center),
                'saida':
                    ('Saída', style_center + saida_cor),
                'entrega':
                    ('Agendada', style_center + entrega_cor),
                'confirmada':
                    ('Entregue', style_center),
                'uf':
                    'UF',
                'dest_cnpj':
                    'CNPJ',
                'dest_nome':
                    'Cliente',
                'transp_nome':
                    'Transp.',
                'volumes':
                    ('Vol.', style_right),
                'valor':
                    ('Valor', style_right),
                'quantidade':
                    ('Qtd.', style_right),
                'observacao':
                    ('Observação', observacao_cor),
                'pedido':
                    'Pedido',
                'ped_cliente':
                    'Ped.Cliente',
            }

            if form['ordem'] == 'A':
                columns = dict_firsts(columns, ['atraso'])
            elif form['ordem'] == 'P':
                columns = dict_firsts(columns, ['pedido', 'ped_cliente'])

            fields = columns.keys()
            headers = map(
                lambda x : x[0] if isinstance(x, tuple) else x,
                columns.values()
            )
            style = {}
            for idx, value in enumerate(columns.values()):
                if isinstance(value, tuple):
                    style[idx+1] = value[1]
            pprint(style)
            context.update({
                'headers': headers,
                'fields': fields,
                'style': style,
                'data': data,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'dia' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            context.update(self.mount_context(form.cleaned_data, form))
        context['form'] = form
        result = render(request, self.template_name, context)
        return result
