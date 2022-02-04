from pprint import pprint
from operator import itemgetter

from django.utils import timezone
from django.shortcuts import render
from django.views import View
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from utils.functions import ldict_coalesce
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
            'data_saida': [
                ord[1] for ord in form_obj.fields['data_saida'].choices
                if ord[0] == form['data_saida']][0],
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

            paginas_vizinhas = 5
            context.update({
                'data_length': len(data),
                'paginas_vizinhas': paginas_vizinhas,
            })

            for row in data:
                if row['saida'] is None:
                    row['atraso'] = (
                        timezone.now() - row['faturamento']).days
                else:
                    row['atraso'] = (
                        row['saida'] - row['faturamento'].date()).days
                row['atraso_order'] = -row['atraso']

            if form['ordem'] == 'A':
                data.sort(key=itemgetter('atraso_order'))

            paginator = Paginator(data, form['por_pagina'])
            try:
                data = paginator.page(form['page'])
            except PageNotAnInteger:
                data = paginator.page(1)
            except EmptyPage:
                data = paginator.page(paginator.num_pages)

            ldict_coalesce(data,
                [
                    [['saida', 'entrega'], '-'],
                    [['observacao', 'ped_cliente'], ' ']
                ]
            )

            for row in data:
                row['numero|LINK'] = reverse(
                    'logistica:notafiscal_nf', args=[row['numero']])
                row['numero|TARGET'] = '_BLANK'
                if row['confirmada']:
                    row['confirmada'] = 'S'
                else:
                    row['confirmada'] = 'N'
                if row['natu_venda']:
                    row['venda'] = 'Sim'
                else:
                    row['venda'] = 'Não'
                if row['ativa']:
                    row['ativa'] = 'Ativa'
                else:
                    row['ativa'] = 'Cancelada'
                if row['nf_devolucao'] is None:
                    row['nf_devolucao'] = 'Não'
                if row['quantidade'] is None:
                    row['quantidade'] = '-'
                else:
                    row['quantidade'] = int(round(row['quantidade']))
                if row['tipo'] == 'a':
                    row['tipo'] = 'Atacado'
                elif row['tipo'] == 'v':
                    row['tipo'] = 'Varejo'
                else:
                    row['tipo'] = 'Outras'

            style_center = 'text-align: center;'
            style_right = 'text-align: right;'
            columns = {
                'numero':
                    'NF',
                'faturamento':
                    'Faturamento',
                'venda':
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
                    ('Saída', style_center),
                'entrega':
                    ('Agendada', style_center),
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
                    'Observação',
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
