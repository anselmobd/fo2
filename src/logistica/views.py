from pprint import pprint
import datetime
from operator import itemgetter

from django.db import connections
from django.utils import timezone
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from django.db.models import When, F, Q
from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.models import rows_to_dict_list
from base.views import O2BaseGetPostView, O2BaseGetView

from .models import *
from .queries import get_nf_pela_chave, get_chave_pela_nf
from .forms import *


def index(request):
    context = {}
    return render(request, 'logistica/index.html', context)


class NotafiscalRel(View):
    Form_class = NotafiscalRelForm
    template_name = 'logistica/notafiscal_rel.html'
    title_name = 'Controle de data de saída de NF'

    def mount_context(self, form, form_obj):
        # A ser produzido
        context = {}
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
            select = select.filter(
                faturamento__date__gte=form['data_de']
                )
            context.update({
                'data_de': form['data_de'],
            })
        if form['data_ate']:
            select = select.filter(
                faturamento__date__lte=form['data_ate']
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
        if form['cliente']:
            condition = Q(dest_nome__icontains=form['cliente']) | \
                        Q(dest_cnpj__contains=form['cliente'])
            select = select.filter(condition)
            context.update({
                'cliente': form['cliente'],
            })
        if form['transportadora']:
            condition = Q(transp_nome__icontains=form['transportadora'])
            select = select.filter(condition)
            context.update({
                'transportadora': form['transportadora'],
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
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma NF encontrada',
            })
        else:
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
                    row['ativa'] = 'Sim'
                else:
                    row['ativa'] = 'Não'
                if row['nf_devolucao'] is None:
                    row['nf_devolucao'] = 'Não'
            if form['ordem'] == 'A':
                data.sort(key=itemgetter('atraso_order'))
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
        if 'dia' in kwargs:
            data = '{dia}/{mes}/{ano}'.format(**kwargs)
            form.data['data_de'] = data
            form.data['data_ate'] = data
        if form.is_valid():
            context.update(self.mount_context(form.cleaned_data, form))
        context['form'] = form
        return render(request, self.template_name, context)


class NotafiscalChave(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(NotafiscalChave, self).__init__(*args, **kwargs)
        self.permission_required = 'logistica.can_beep_shipment'
        self.Form_class = NotafiscalChaveForm
        self.template_name = 'logistica/notafiscal_chave.html'
        self.title_name = 'Movimenta NF por chave'
        self.get_args = ['chave']

    def mount_context(self):
        self.context.update({
            'chave': self.form.cleaned_data['chave'],
        })
        cursor = connections['so'].cursor()
        data_nf = get_nf_pela_chave(cursor, self.form.cleaned_data['chave'])
        if len(data_nf) == 0:
            self.context.update({
                'msg_erro': 'Nenhuma NF encontrada',
            })
        else:
            nf = data_nf[0]['NUM_NOTA_FISCAL']

            alt_action = [
                k for k in self.request.POST.keys() if k.startswith('alt_')]
            if alt_action:
                nota_fiscal = NotaFiscal.objects.get(numero=nf)

                num_action = alt_action[0].split('_')[1]
                pos_carga_alt = PosicaoCargaAlteracao.objects.values().get(
                    id=num_action)

                if nota_fiscal.posicao_id == pos_carga_alt['inicial_id']:
                    if pos_carga_alt['efeito_id'] == 2:
                        nota_fiscal.saida = timezone.now()
                    elif pos_carga_alt['efeito_id'] == 3:
                        nota_fiscal.saida = None
                    elif pos_carga_alt['efeito_id'] == 4:
                        if nota_fiscal.entrega is None:
                            nota_fiscal.entrega = timezone.now()
                        nota_fiscal.confirmada = True
                    elif pos_carga_alt['efeito_id'] == 5:
                        nota_fiscal.confirmada = False
                    nota_fiscal.save()

                    nota_fiscal.posicao_id = pos_carga_alt['final_id']
                    nota_fiscal.save()

                    pca_log = PosicaoCargaAlteracaoLog(
                        numero=nf, user=self.request.user)
                    pca_log.inicial_id = pos_carga_alt['inicial_id']
                    pca_log.final_id = pos_carga_alt['final_id']
                    pca_log.saida = nota_fiscal.saida
                    pca_log.save()

            fields = [f.get_attname() for f in NotaFiscal._meta.get_fields()]
            row = NotaFiscal.objects.values(
                *fields, 'posicao__nome').get(numero=nf)

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
                status = 'ATIVA'
                row['ativa'] = 'Sim'
            else:
                status = 'CANCELADA'
                row['ativa'] = 'Não'
            if row['nf_devolucao'] is None:
                row['nf_devolucao'] = 'Não'
                nf_devolucao = ''
            else:
                nf_devolucao = row['nf_devolucao']
                status = 'DEVOLVIDA'

            acoes = []
            pos_alt = list(PosicaoCargaAlteracao.objects.filter(
                inicial_id=row['posicao_id']).order_by('-ordem').values())
            for alt in pos_alt:
                if (not alt['so_nfs_ativas']) or status == 'ATIVA':
                    acoes.append({
                        'name': 'alt_{}'.format(alt['id']),
                        'descr': alt['descricao'],
                    })

            self.context.update({
                'status': status,
                'nf': row['numero'],
                'nf_devolucao': nf_devolucao,
                'acoes': acoes,
                'posicao': row['posicao__nome'],
                'headers1': ('Faturamento', 'Venda', 'Ativa',
                             'Devolvida', 'Atraso',
                             'Saída', 'Agendada', 'Entregue',),
                'fields1': ('faturamento', 'venda', 'ativa',
                            'nf_devolucao', 'atraso',
                            'saida', 'entrega', 'confirmada'),
                'data1': [row],
                'headers2': ('UF', 'CNPJ', 'Cliente', 'Transp.',
                             'Vol.', 'Valor', 'Observação',
                             'Pedido', 'Ped.Cliente'),
                'fields2': ('uf', 'dest_cnpj', 'dest_nome', 'transp_nome',
                            'volumes', 'valor', 'observacao',
                            'pedido', 'ped_cliente'),
                'data2': [row],
            })

            datalog = list(
                PosicaoCargaAlteracaoLog.objects.filter(
                    numero=nf).order_by('-time').values(
                        'numero', 'time', 'user',
                        'inicial__nome', 'final__nome', 'saida')
            )
            for row in datalog:
                if row['saida'] is None:
                    row['saida'] = '-'
            self.context.update({
                'headerslog': ('Hora', 'Usuário',
                               'Posição inicial', 'Posição final',
                               'Data de saída'),
                'fieldslog': ('time', 'user',
                              'inicial__nome', 'final__nome',
                              'saida'),
                'datalog': datalog,
            })


class NotafiscalEmbarcando(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(NotafiscalEmbarcando, self).__init__(*args, **kwargs)
        self.template_name = 'logistica/notafiscal_embarcando.html'
        self.title_name = 'Notas fiscais embarcando'

    def mount_context(self):
        fields = [f.get_attname() for f in NotaFiscal._meta.get_fields()]
        nfs = NotaFiscal.objects.filter(posicao_id=2).order_by('numero')
        data = list(nfs.values(*fields, 'posicao__nome'))
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Nenhuma NF embarcando',
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
                row['ativa'] = 'Sim'
            else:
                row['ativa'] = 'Não'
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
        for passo in range(2):
            nfs_mov = PosicaoCargaAlteracaoLog.objects
            if data is not None:
                nfs_mov = nfs_mov.filter(time__contains=data)
            if passo == 0:
                descr = ' para a posição selecionada'
                if posicao is not None:
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

                nfs = NotaFiscal.objects.filter(
                    posicao_id=posicao.id, numero__in=numeros
                    ).order_by('-numero')
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
                        row['ativa'] = 'Sim'
                    else:
                        row['ativa'] = 'Não'
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
