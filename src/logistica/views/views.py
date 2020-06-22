import sys
from pprint import pprint
import datetime
from datetime import timedelta
import pytz
from operator import itemgetter

from django.db import connections
from django.utils import timezone
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from django.db.models import When, F, Q
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from utils.functions.models import rows_to_dict_list
from base.views import O2BaseGetPostView, O2BaseGetView

from .models import *
from .queries import get_nf_pela_chave, get_chave_pela_nf
from .forms import *


def index(request):
    return render(request, 'logistica/index.html')


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

        select = select.order_by('-numero')
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

            context.update({
                'headers': ('No.', 'Faturamento', 'Venda', 'Ativa',
                            'Devolvida', 'Posição',
                            'Atraso', 'Saída', 'Agendada',
                            'Entregue', 'UF', 'CNPJ', 'Cliente',
                            'Transp.', 'Vol.', 'Valor', 'Observação',
                            'Pedido', 'Ped.Cliente'),
                'fields': ('numero', 'faturamento', 'venda', 'ativa',
                           'nf_devolucao', 'posicao__nome',
                           'atraso', 'saida', 'entrega',
                           'confirmada', 'uf', 'dest_cnpj', 'dest_nome',
                           'transp_nome', 'volumes', 'valor', 'observacao',
                           'pedido', 'ped_cliente'),
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
        # if 'dia' in kwargs:
        #     data = '{dia}/{mes}/{ano}'.format(**kwargs)
        #     form.data['data_de'] = data  # não funciona
        #     form.data['data_ate'] = data
        if form.is_valid():
            context.update(self.mount_context(form.cleaned_data, form))
        context['form'] = form
        result = render(request, self.template_name, context)
        return result


class NotafiscalEmbarcando(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(NotafiscalEmbarcando, self).__init__(*args, **kwargs)
        self.template_name = 'logistica/notafiscal_embarcando.html'
        self.title_name = 'Notas fiscais entregues ao apoio'

    def mount_context(self):
        fields = [f.get_attname() for f in NotaFiscal._meta.get_fields()]
        nfs = NotaFiscal.objects.filter(posicao_id=2).order_by('numero')
        data = list(nfs.values(*fields, 'posicao__nome'))
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Nenhuma NF entregues ao apoio',
            })

        for row in data:
            row['numero|LINK'] = reverse(
                'logistica:notafiscal_nf', args=[row['numero']])
            row['numero|TARGET'] = '_BLANK'
            if row['saida'] is None:
                row['saida'] = '-'
                row['atraso'] = (
                    timezone.now() - row['faturamento']).days
            else:
                row['atraso'] = (
                    row['saida'] - row['faturamento'].date()).days
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
            row['atraso_order'] = -row['atraso']
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

        self.context.update({
            'headers': ('No.', 'Faturamento', 'Venda', 'Ativa',
                        'Devolvida', 'Posição',
                        'Atraso', 'Saída', 'Agendada',
                        'Entregue', 'UF', 'CNPJ', 'Cliente',
                        'Transp.', 'Vol.', 'Valor', 'Observação',
                        'Pedido', 'Ped.Cliente'),
            'fields': ('numero', 'faturamento', 'venda', 'ativa',
                       'nf_devolucao', 'posicao__nome',
                       'atraso', 'saida', 'entrega',
                       'confirmada', 'uf', 'dest_cnpj', 'dest_nome',
                       'transp_nome', 'volumes', 'valor', 'observacao',
                       'pedido', 'ped_cliente'),
            'data': data,
            'quant': len(data),
        })


class NotafiscalMovimentadas(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(NotafiscalMovimentadas, self).__init__(*args, **kwargs)
        self.Form_class = NfPosicaoForm
        self.template_name = 'logistica/notafiscal_movimentadas.html'
        self.title_name = 'Notas fiscais movimentadas'

    def mount_context(self):
        data = self.form.cleaned_data['data']
        posicao = self.form.cleaned_data['posicao']

        if data is None and posicao is None:
            return

        if data is None:
            if posicao.id != 2:
                self.context.update({
                    'msg_erro': 'Sem data, '
                                'só pode pesquisar "Entregue ao apoio"'})
                return

        nfs_mov = PosicaoCargaAlteracaoLog.objects
        if data is not None:
            nfs_mov = nfs_mov.filter(time__contains=data)
        if posicao is not None:
            nfs_mov = nfs_mov.filter(
                Q(inicial=posicao) | Q(final=posicao))
        nfs_mov = nfs_mov.distinct().values()
        if len(nfs_mov) == 0:
            self.context.update({
                'msg_erro': 'Nenhum movimento de NF encontrado'})
            return

        fields = [f.get_attname() for f in NotaFiscal._meta.get_fields()]

        passo_context = []
        if posicao is None:
            n_passos = 1
        else:
            n_passos = 2
        for passo in range(n_passos):
            nfs_mov = PosicaoCargaAlteracaoLog.objects
            if data is not None:
                nfs_mov = nfs_mov.filter(time__contains=data)
            if passo == 0:
                if posicao is None:
                    descr = ''
                else:
                    descr = ' para a posição selecionada'
                    nfs_mov = nfs_mov.filter(final=posicao)
            else:
                descr = ' para fora da posição selecionada'
                if posicao is not None:
                    nfs_mov = nfs_mov.filter(inicial=posicao)
            nfs_mov = nfs_mov.distinct().values()

            if len(nfs_mov) != 0:
                numeros = set()
                for log in nfs_mov:
                    numeros.add(log['numero'])

                nfs = NotaFiscal.objects
                if posicao is None:
                    nfs = nfs.filter(
                        numero__in=numeros).order_by('posicao__id', '-numero')
                else:
                    nfs = nfs.filter(posicao_id=posicao.id)
                    nfs = nfs.filter(numero__in=numeros).order_by('-numero')

                dados = list(nfs.values(*fields, 'posicao__nome'))

                for row in dados:
                    row['numero|LINK'] = reverse(
                        'logistica:notafiscal_nf', args=[row['numero']])
                    row['numero|TARGET'] = '_BLANK'
                    if row['saida'] is None:
                        row['saida'] = '-'
                        if row['faturamento'] is not None:
                            row['atraso'] = (
                                timezone.now() - row['faturamento']).days
                        else:
                            row['atraso'] = 999
                    else:
                        if row['faturamento'] is not None:
                            row['atraso'] = (
                                row['saida'] - row['faturamento'].date()).days
                        else:
                            row['atraso'] = 999
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
                    row['atraso_order'] = -row['atraso']
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

                passo_context.append({
                    'descr': descr,
                    'data': data,
                    'posicao': posicao,
                    'headers': ('No.', 'Faturamento', 'Venda', 'Ativa',
                                'Devolvida', 'Posição',
                                'Atraso', 'Saída', 'Agendada',
                                'Entregue', 'UF', 'Cliente',
                                'Transp.', 'Vol.', 'Valor',
                                'Pedido', 'Ped.Cliente'),
                    'fields': ('numero', 'faturamento', 'venda', 'ativa',
                               'nf_devolucao', 'posicao__nome',
                               'atraso', 'saida', 'entrega',
                               'confirmada', 'uf', 'dest_nome',
                               'transp_nome', 'volumes', 'valor',
                               'pedido', 'ped_cliente'),
                    'dados': dados,
                    'quant': len(dados),
                })
        self.context.update({
            'passo_context': passo_context, })


def notafiscal_nf(request, *args, **kwargs):
    if 'nf' not in kwargs or kwargs['nf'] is None:
        return redirect('logistica:index')

    cursor = connections['so'].cursor()
    data_nf = get_chave_pela_nf(cursor, kwargs['nf'])
    if len(data_nf) == 0:
        return redirect('logistica:index')

    return redirect(
        'logistica:notafiscal_chave', data_nf[0]['NUMERO_DANF_NFE'])
