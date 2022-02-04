from pprint import pprint
from datetime import datetime, timedelta
import pytz
from operator import itemgetter

from django.utils import timezone
from django.shortcuts import render
from django.views import View
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from utils.functions import untuple_keys_concat
from utils.functions.dict import dict_firsts

from logistica.models import NotaFiscal
from logistica.forms import NotafiscalRelForm


class NotafiscalRel(View):
    Form_class = NotafiscalRelForm
    template_name = 'logistica/notafiscal_rel.html'
    title_name = 'Consulta de datas de NF'

    def mount_context(self, form, form_obj):
        if form['por_pagina']:
            linhas_pagina = form['por_pagina']
        else:
            linhas_pagina = 100
        paginas_vizinhas = 5
        local = pytz.timezone("America/Sao_Paulo")

        context = {
            'linhas_pagina': linhas_pagina,
            'paginas_vizinhas': paginas_vizinhas,
        }

        fields = [f.get_attname() for f in NotaFiscal._meta.get_fields()]

        context.update(form)

        context.update({
            'data_saida': [
                ord[1] for ord in form_obj.fields['data_saida'].choices
                if ord[0] == form['data_saida']][0],
        })

        select = NotaFiscal.objects.xfilter(**form)

        if form['posicao'] is not None:
            select = select.filter(posicao_id=form['posicao'].id)
            context.update({
                'posicao': form['posicao'].nome,
            })
        if form['tipo'] != '-':
            select = select.filter(tipo=form['tipo'])
            context.update({
                'tipo': form['tipo'],
            })

        data = list(select.values(*fields, 'posicao__nome'))
        data_length = len(data)

        if data_length == 0:
            context.update({
                'msg_erro': 'Nenhuma NF encontrada',
            })
        else:

            context.update({
                'data_length': data_length,
            })

            for row in data:
                if row['saida'] is None:
                    row['saida'] = '-'
                    row['atraso'] = (
                        timezone.now() - row['faturamento']).days
                else:
                    row['atraso'] = (
                        row['saida'] - row['faturamento'].date()).days
                row['atraso_order'] = -row['atraso']

            if form['ordem'] == 'A':
                data.sort(key=itemgetter('atraso_order'))

            paginator = Paginator(data, linhas_pagina)
            try:
                data = paginator.page(form['page'])
            except PageNotAnInteger:
                data = paginator.page(1)
            except EmptyPage:
                data = paginator.page(paginator.num_pages)

            for row in data:
                row['numero|LINK'] = reverse(
                    'logistica:notafiscal_nf', args=[row['numero']])
                row['numero|TARGET'] = '_BLANK'
                if row['entrega'] is None:
                    row['entrega'] = '-'
                if row['confirmada']:
                    row['confirmada'] = 'S'
                else:
                    row['confirmada'] = 'N'
                if row['observacao'] is None:
                    row['observacao'] = ' '
                if row['ped_cliente'] is None:
                    row['ped_cliente'] = ' '
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
