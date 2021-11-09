from pprint import pprint
import datetime
from datetime import timedelta
import pytz
from operator import itemgetter

from django.utils import timezone
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView, O2BaseGetView
from utils.functions import untuple_keys_concat
from geral.functions import get_empresa

from logistica.models import *
from logistica.queries import get_chave_pela_nf
from logistica.forms import *


def index(request):
    if get_empresa(request) == 'agator':
        return render(request, 'logistica/index_agator.html')
    else:
        return render(request, 'logistica/index.html')


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
                    'style': untuple_keys_concat({
                        tuple(range(1, 11)): 'text-align: center;',
                        (14, 15, 16, 17): 'text-align: right;',
                    }),
                    'dados': dados,
                    'quant': len(dados),
                })
        self.context.update({
            'passo_context': passo_context, })


def notafiscal_nf(request, *args, **kwargs):
    if 'nf' not in kwargs or kwargs['nf'] is None:
        return redirect('logistica:index')

    cursor = db_cursor_so(request)
    data_nf = get_chave_pela_nf(cursor, kwargs['nf'])
    if len(data_nf) == 0:
        return redirect('logistica:index')

    return redirect(
        'logistica:notafiscal_chave', data_nf[0]['NUMERO_DANF_NFE'])
