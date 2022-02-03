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
            'ordem': form['ordem'],
        }

        fields = [f.get_attname() for f in NotaFiscal._meta.get_fields()]

        if form['listadas'] == 'V':
            select = NotaFiscal.objects.filter(
                natu_venda=True).filter(ativa=True)
            context.update({
                'listadas': 'V',
            })
        else:
            select = NotaFiscal.objects
            context.update({
                'listadas': 'T',
            })
        if form['data_de']:
            datatime_de = datetime.combine(
                form['data_de'], datetime.min.time())
            local_dt = local.localize(datatime_de, is_dst=None)
            # local_dt = local.localize(form['data_de'])
            # local_dt = form['data_de']
            dt_de = local_dt.astimezone(pytz.utc)
            select = select.filter(
                faturamento__gte=dt_de
                )
            context.update({
                'data_de': form['data_de'],
            })
        if form['data_ate']:
            datatime_ate = datetime.combine(
                form['data_ate'] + timedelta(days=1), datetime.min.time())
            local_dt = local.localize(datatime_ate, is_dst=None)
            dt_ate = local_dt.astimezone(pytz.utc)
            select = select.filter(
                faturamento__lte=dt_ate
                )
            context.update({
                'data_ate': form['data_ate'],
            })
        if form['uf']:
            select = select.filter(uf=form['uf'])
            context.update({
                'uf': form['uf'],
            })
        if form['nf']:
            select = select.filter(numero=form['nf'])
            context.update({
                'nf': form['nf'],
            })
        if form['transportadora']:
            condition = Q(transp_nome__icontains=form['transportadora'])
            select = select.filter(condition)
            context.update({
                'transportadora': form['transportadora'],
            })
        if form['cliente']:
            condition = Q(dest_nome__icontains=form['cliente']) | \
                        Q(dest_cnpj__contains=form['cliente'])
            select = select.filter(condition)
            context.update({
                'cliente': form['cliente'],
            })
        if form['pedido']:
            select = select.filter(pedido=form['pedido'])
            context.update({
                'pedido': form['pedido'],
            })
        if form['ped_cliente']:
            select = select.filter(ped_cliente=form['ped_cliente'])
            context.update({
                'ped_cliente': form['ped_cliente'],
            })
        if form['entregue'] != 'T':
            select = select.filter(confirmada=form['entregue'] == 'S')
            context.update({
                'entregue': form['entregue'],
            })
        if form['data_saida'] != 'N':
            select = select.filter(saida__isnull=form['data_saida'] == 'S')
            context.update({
                'data_saida': [
                    ord[1] for ord in form_obj.fields['data_saida'].choices
                    if ord[0] == form['data_saida']][0],
            })
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

        if form['ordem'] == 'N':
            select = select.order_by('-numero')
        elif form['ordem'] == 'P':
            select = select.order_by('pedido')

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

            context.update({
                'headers': ('NF', 'Faturamento', 'Venda', 'Tipo', 'Ativa',
                            'Devolvida', 'Posição',
                            'Atraso', 'Saída', 'Agendada',
                            'Entregue', 'UF', 'CNPJ', 'Cliente',
                            'Transp.', 'Vol.', 'Valor', 'Qtd.',
                            'Observação', 'Pedido', 'Ped.Cliente'),
                'fields': ('numero', 'faturamento', 'venda', 'tipo', 'ativa',
                           'nf_devolucao', 'posicao__nome',
                           'atraso', 'saida', 'entrega',
                           'confirmada', 'uf', 'dest_cnpj', 'dest_nome',
                           'transp_nome', 'volumes', 'valor', 'quantidade',
                           'observacao', 'pedido', 'ped_cliente'),
                'style': untuple_keys_concat({
                    (15, 16, 17): 'text-align: right;',
                    (3, 4, 5, 6, 7, 8, 9, 10): 'text-align: center;',
                }),
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
