from pprint import pprint
import datetime
from operator import itemgetter

from django.db import connections
from django.utils import timezone
from django.shortcuts import render
from django.views import View
from django.db.models import When, F, Q
from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.models import rows_to_dict_list

from .models import *
from .queries import get_nf_pela_chave
from .forms import NotafiscalRelForm, NotafiscalChaveForm


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

        select = select.order_by('-numero')
        data = list(select.values())
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma NF encontrada',
            })
        else:
            for row in data:
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
                            'Devolvida', 'Atraso', 'Saída', 'Agendada',
                            'Entregue', 'UF', 'CNPJ', 'Cliente',
                            'Transp.', 'Vol.', 'Valor', 'Observação',
                            'Pedido', 'Ped.Cliente'),
                'fields': ('numero', 'faturamento', 'venda', 'ativa',
                           'nf_devolucao', 'atraso', 'saida', 'entrega',
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


class NotafiscalChave(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'logistica.can_beep_shipment'
        self.Form_class = NotafiscalChaveForm
        self.template_name = 'logistica/notafiscal_chave.html'
        self.title_name = 'Informação sobre NF bipando DANFE'

    def mount_context(self, form):
        context = {
            'chave': form['chave'],
        }
        cursor = connections['so'].cursor()
        data_nf = get_nf_pela_chave(cursor, form['chave'])
        if len(data_nf) == 0:
            context.update({
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
                    nota_fiscal.save()

                    nota_fiscal.posicao_id = pos_carga_alt['final_id']
                    nota_fiscal.save()

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
            if status == 'ATIVA':
                pos_alt = list(PosicaoCargaAlteracao.objects.filter(
                    inicial_id=row['posicao_id']).order_by('-ordem').values())
                for alt in pos_alt:
                    acoes.append({
                        'name': 'alt_{}'.format(alt['id']),
                        'descr': alt['descricao'],
                    })

            context.update({
                'status': status,
                'nf_devolucao': nf_devolucao,
                'acoes': acoes,
                'posicao': row['posicao__nome'],
                'headers1': ('No.', 'Faturamento', 'Venda', 'Ativa',
                             'Devolvida', 'Atraso',
                             'Saída', 'Agendada', 'Entregue',),
                'fields1': ('numero', 'faturamento', 'venda', 'ativa',
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

        return context

    def get(self, request, *args, **kwargs):
        self.request = request
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.request = request
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            context.update(self.mount_context(form.cleaned_data))
        context['form'] = form
        return render(request, self.template_name, context)
