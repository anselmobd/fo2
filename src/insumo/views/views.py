import datetime
import math
import os
import re
import time
from operator import itemgetter
from pprint import pprint
from datetime import timedelta

from django.db import connections
from django.db.models import Q
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.template.loader import render_to_string
from django.core.cache import cache

from fo2 import settings

import systextil.models
from geral.models import Dispositivos, RoloBipado
from utils.cache import entkeys
from utils.functions import (
    fo2logger,
    max_not_None,
    min_not_None,
    my_make_key_cache,
    segunda,
)
from utils.functions.models import rows_to_dict_list, rows_to_dict_list_lower
from utils.views import totalize_grouped_data, group_rowspan

import insumo.functions
import insumo.queries as queries
import insumo.models as models
from insumo.forms import \
    EstoqueForm, \
    MapaRefsForm, \
    NecessidadeForm, \
    PrevisaoForm, \
    BipaRoloForm, \
    RolosBipadosForm, \
    ReceberForm, \
    MapaPorSemanaForm, \
    MapaPorSemanaNewForm, \
    MapaSemanalForm, \
    FiltroMpForm


def index(request):
    return render(request, 'insumo/index.html')


class Busca(View):
    Form_class = FiltroMpForm
    template_name = 'insumo/busca.html'
    title_name = 'Listagem de insumos'

    def mount_context(self, cursor, filtro, conta_estoque, tipo_conta_estoque):
        context = {'filtro': filtro}

        data = queries.lista_insumo(
            cursor, filtro, conta_estoque, tipo_conta_estoque)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhum insumo selecionado',
            })
        else:
            link = ('REF')
            for row in data:
                row['LINK'] = reverse('insumo:ref__get', args=[row['REF']])
            context.update({
                'headers': ('#', 'Nível', 'Referência', 'Descrição',
                            'Conta de estoque'),
                'fields': ('NUM', 'NIVEL', 'REF', 'DESCR',
                           'CONTA_ESTOQUE'),
                'data': data,
                'link': link,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'filtro' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'filtro' in kwargs:
            form.data['filtro'] = kwargs['filtro']
        if form.is_valid():
            filtro = form.cleaned_data['filtro']
            conta_estoque = form.cleaned_data['conta_estoque']
            tipo_conta_estoque = form.cleaned_data['tipo_conta_estoque']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, filtro, conta_estoque, tipo_conta_estoque))
        context['form'] = form
        return render(request, self.template_name, context)


def rolo_json(request, *args, **kwargs):
    dispositivo = Dispositivos.objects.filter(key=kwargs['origem'])
    if len(dispositivo) == 0:
        dispositivo = Dispositivos.objects.create(key=kwargs['origem'])
        dispositivo.save()
    else:
        dispositivo = dispositivo[0]
    barcode = re.sub("\D", "", kwargs['barcode'])[:9]
    cursor = connections['so'].cursor()
    data = queries.rolo_ref(cursor, barcode)
    if len(data) == 0:
        data = [{}]
    else:
        row = data[0]
        rolo_bipado = RoloBipado(
            dispositivo=dispositivo,
            rolo=row['ROLO'],
            referencia=row['REF'],
            tamanho=row['TAM'],
            cor=row['COR'],
            )
        rolo_bipado.save()

    return JsonResponse(data[0])


class RolosBipados(View):
    Form_class = RolosBipadosForm
    template_name = 'insumo/rolos_bipados.html'
    title_name = 'Rolos Bipados'

    def mount_context(self, cursor, dispositivo, ref, cor, data_de, data_ate):
        context = {}
        # Lista rolos
        rolos = RoloBipado.objects.select_related('dispositivo')
        filename = ''
        filenamesep = ''
        if dispositivo != '':
            rolos = rolos.filter(
                Q(dispositivo__nome__icontains=dispositivo)
                | Q(usuario__username__icontains=dispositivo)
                )
            context.update({
                'dispositivo': dispositivo,
            })
            filename += filenamesep + 'D_'+dispositivo
            filenamesep = '-'
        if ref != '':
            rolos = rolos.filter(referencia=ref)
            context.update({
                'ref': ref,
            })
            filename += filenamesep + 'R_'+ref
            filenamesep = '-'
        if cor != '':
            rolos = rolos.filter(cor__contains=cor)
            context.update({
                'cor': cor,
            })
            filename += filenamesep + 'C_'+cor
            filenamesep = '-'
        if data_de is not None:
            rolos = rolos.filter(date__gte=data_de)
            context.update({
                'data_de': data_de,
            })
            filename += filenamesep + 'DD_'+data_de.strftime("%Y.%m.%d")
            filenamesep = '-'
        if data_ate is not None:
            rolos = rolos.filter(date__lte=data_ate)
            context.update({
                'data_ate': data_ate,
            })
            filename += filenamesep + 'DA_'+data_ate.strftime("%Y.%m.%d")
            filenamesep = '-'
        filename += filenamesep + time.strftime("%Y.%m.%d-%H.%M.%S") + '.TXT'
        rolos = rolos.order_by('-date')
        if len(rolos) == 0:
            context.update({
                'msg_erro': 'Nenhum rolo selecionado',
            })
        else:
            rolos = rolos.values(
                'dispositivo__nome', 'usuario__username', 'rolo', 'date',
                'referencia', 'tamanho', 'cor')
            dir_filename = os.path.join('insumos_rolos_bipados', filename)
            arq = os.path.join(settings.MEDIA_ROOT, dir_filename)
            with open(arq, 'w') as f:
                for rolo in rolos:
                    print("{:06}{:09}".format(1, rolo['rolo']), file=f)
                    if not rolo['dispositivo__nome']:
                        rolo['dispositivo__nome'] = '-'
                    if not rolo['usuario__username']:
                        rolo['usuario__username'] = '-'
            context.update({
                'filename': dir_filename,
                'headers': ('Dispositivo', 'Usuário',
                            'Rolo', 'Data/hora',
                            'Referencia', 'Tamanho', 'Cor'),
                'fields': ('dispositivo__nome', 'usuario__username',
                           'rolo', 'date',
                           'referencia', 'tamanho', 'cor'),
                'data': rolos,
            })

        return context

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            dispositivo = form.cleaned_data['dispositivo']
            ref = form.cleaned_data['ref']
            cor = form.cleaned_data['cor']
            data_de = form.cleaned_data['data_de']
            data_ate = form.cleaned_data['data_ate']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, dispositivo, ref, cor, data_de, data_ate))
        context['form'] = form
        return render(request, self.template_name, context)


class BipaRolo(PermissionRequiredMixin, View):
    permission_required = 'geral.can_beep_rolo'
    Form_class = BipaRoloForm
    template_name = 'insumo/bipa_rolo.html'
    title_name = 'Bipa rolo'

    def mount_context(self, request, form):
        cursor = connections['so'].cursor()

        rolo = form.cleaned_data['rolo']
        identificado = form.cleaned_data['identificado']

        context = {}

        data = queries.rolo_ref(cursor, rolo)
        if len(data) == 0:
            context.update({'erro': 'Rolo não encontrado'})
            return context

        row = data[0]
        context.update({
            'rolo': row['ROLO'],
            'referencia': row['REF'],
            'cor': row['COR'],
            'tamanho': row['TAM'],
            })

        if identificado:
            form.data['identificado'] = None
            form.data['rolo'] = None
            if rolo != identificado:
                context.update({
                    'erro': 'A confirmação é bipando o mesmo rolo. '
                            'Identifique o rolo novamente.'})
                return context

            rolo_bipado = RoloBipado(
                usuario=request.user,
                rolo=row['ROLO'],
                referencia=row['REF'],
                tamanho=row['TAM'],
                cor=row['COR'],
                )
            rolo_bipado.save()

            context['identificado'] = identificado
        else:
            context['rolo'] = rolo
            context['confirma'] = True
            form.data['identificado'] = form.data['rolo']
            form.data['rolo'] = None

        return context

    def get(self, request, *args, **kwargs):
        if 'lote' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST.copy())
        if 'lote' in kwargs:
            form.data['lote'] = kwargs['lote']
        if form.is_valid():
            data = self.mount_context(request, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)


class Necessidade(View):
    Form_class = NecessidadeForm
    template_name = 'insumo/necessidade.html'
    title_name = 'Necessidade'

    def mount_context(
            self, cursor, op, data_corte, data_corte_ate, periodo_corte,
            data_compra, data_compra_ate, periodo_compra,
            insumo, conta_estoque,
            ref, conta_estoque_ref, colecao, quais):
        context = {}
        if not (op or data_corte or data_corte_ate or periodo_corte or
                data_compra or data_compra_ate or periodo_compra or
                insumo or conta_estoque or
                ref or conta_estoque_ref or colecao):
            context.update({
                'msg_erro': 'Especifique ao menos um filtro',
            })
            return context
        context.update({
            'op': op,
            'data_corte': data_corte,
            'data_corte_ate': data_corte_ate,
            'periodo_corte': periodo_corte,
            'data_compra': data_compra,
            'data_compra_ate': data_compra_ate,
            'periodo_compra': periodo_compra,
            'insumo': insumo,
            'conta_estoque': conta_estoque,
            'ref': ref,
            'conta_estoque_ref': conta_estoque_ref,
            'colecao': colecao,
            'quais': quais,
        })

        data = queries.necessidade(
            cursor, op, data_corte, data_corte_ate, periodo_corte,
            data_compra, data_compra_ate, periodo_compra,
            insumo, conta_estoque,
            ref, conta_estoque_ref, colecao, quais)

        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma necessidade de insumos encontrada',
            })
            return context

        for row in data:
            row['REF|LINK'] = reverse('insumo:ref__get', args=[row['REF']])
            row['OPS'] = re.sub(
                r'([1234567890]+)',
                r'<a href="/lotes/op/\1">\1&nbsp;<span '
                'class="glyphicon glyphicon-link" '
                'aria-hidden="true"></span></a>',
                str(row['OPS']))
            row['REFS'] = re.sub(
                r'([^, ]+)',
                r'<a href="{produto_ref}\1">\1&nbsp;<span '
                'class="glyphicon glyphicon-link" '
                'aria-hidden="true"></span></a>'.format(
                    produto_ref=reverse('produto:ref')),
                str(row['REFS']))
        context.update({
            'headers': ('Nível', 'Insumo', 'Descrição',
                        'Cor', 'Tamanho',
                        'Necessidade', 'Unid.',
                        'Produzido', 'OPs',
                        'Estoq. Mínimo', 'Reposição'),
            'fields': ('NIVEL', 'REF', 'DESCR',
                       'COR', 'TAM',
                       'QTD', 'UNID',
                       'REFS', 'OPS',
                       'STQ_MIN', 'REPOSICAO'),
            'safe': ('REFS', 'OPS'),
            'data': data,
        })

        return context

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            op = form.cleaned_data['op']
            data_corte = form.cleaned_data['data_corte']
            data_corte_ate = form.cleaned_data['data_corte_ate']
            periodo_corte = form.cleaned_data['periodo_corte']
            data_compra = form.cleaned_data['data_compra']
            data_compra_ate = form.cleaned_data['data_compra_ate']
            periodo_compra = form.cleaned_data['periodo_compra']
            insumo = form.cleaned_data['insumo']
            conta_estoque = form.cleaned_data['conta_estoque']
            ref = form.cleaned_data['ref']
            conta_estoque_ref = form.cleaned_data['conta_estoque_ref']
            colecao = form.cleaned_data['colecao']
            quais = form.cleaned_data['quais']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, op, data_corte, data_corte_ate, periodo_corte,
                data_compra, data_compra_ate, periodo_compra,
                insumo, conta_estoque,
                ref, conta_estoque_ref, colecao, quais))
        context['form'] = form
        return render(request, self.template_name, context)


class Receber(View):
    Form_class = ReceberForm
    template_name = 'insumo/receber.html'
    title_name = 'A Receber'

    def mount_context(self, cursor, insumo, conta_estoque, recebimento):
        context = {}
        # if not (insumo or conta_estoque):
        #     context.update({
        #         'msg_erro': 'Especifique ao menos um filtro',
        #     })
        #     return context
        context.update({
            'insumo': insumo,
            'conta_estoque': conta_estoque,
            'recebimento': recebimento,
        })

        data = queries.receber(cursor, insumo, conta_estoque, recebimento)

        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhum pedido de insumos encontrado',
            })
            return context

        max_digits = 0
        for row in data:
            row['REF|LINK'] = reverse('insumo:ref__get', args=[row['REF']])
            row['DT_ENTREGA'] = row['DT_ENTREGA'].date()
            num_digits = str(row['QTD_RECEBIDA'])[::-1].find('.')
            max_digits = max(max_digits, num_digits)
            num_digits = str(row['QTD_A_RECEBER'])[::-1].find('.')
            max_digits = max(max_digits, num_digits)

        group = ['NIVEL', 'REF', 'DESCR', 'COR', 'TAM']
        totalize_grouped_data(data, {
            'group': group,
            'sum': ['QTD_PEDIDA', 'QTD_RECEBIDA', 'QTD_A_RECEBER'],
            'count': [],
            'descr': {'DT_ENTREGA': 'Totais:'},
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(data, group)

        for row in data:
            row['P_RECEBIDO|DECIMALS'] = 1
            row['P_A_RECEBER|DECIMALS'] = 1
            row['QTD_RECEBIDA|DECIMALS'] = max_digits
            row['QTD_A_RECEBER|DECIMALS'] = max_digits

        context.update({
            'headers': ('Nível', 'Insumo', 'Descrição', 'Cor',
                        'Tamanho', 'Dt. Entrega',
                        'Qtd.Pedida', 'Qtd.Recebida', '%Recebido',
                        'Qtd.A receber', '%A receber', 'Pedidos'),
            'fields': ('NIVEL', 'REF', 'DESCR', 'COR',
                       'TAM', 'DT_ENTREGA',
                       'QTD_PEDIDA', 'QTD_RECEBIDA', 'P_RECEBIDO',
                       'QTD_A_RECEBER', 'P_A_RECEBER', 'PEDIDOS'),
            'style': {7: 'text-align: right;',
                      8: 'text-align: right;',
                      9: 'text-align: right;',
                      10: 'text-align: right;',
                      11: 'text-align: right;'},
            'group': group,
            'data': data,
        })

        return context

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            insumo = form.cleaned_data['insumo']
            conta_estoque = form.cleaned_data['conta_estoque']
            recebimento = form.cleaned_data['recebimento']
            cursor = connections['so'].cursor()
            context.update(
                self.mount_context(cursor, insumo, conta_estoque, recebimento))
        context['form'] = form
        return render(request, self.template_name, context)


class Estoque(View):
    Form_class = EstoqueForm
    template_name = 'insumo/estoque.html'
    title_name = 'Estoque'

    def mount_context(self, cursor, insumo, conta_estoque):
        context = {}
        if not (insumo or conta_estoque):
            context.update({
                'msg_erro': 'Especifique ao menos um filtro',
            })
            return context
        context.update({
            'insumo': insumo,
            'conta_estoque': conta_estoque,
        })

        data = queries.estoque(cursor, insumo, conta_estoque)

        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhum estoque de insumos encontrado',
            })
            return context

        group = ['NIVEL', 'REF', 'DESCR', 'COR', 'TAM']
        totalize_grouped_data(data, {
            'group': group,
            'sum': ['QUANT'],
            'count': [],
            'descr': {'DESCRICAO': 'Total:'}
        })
        group_rowspan(data, group)

        for row in data:
            # row['QUANT|STYLE'] = 'text-align: right;'
            row['REF|LINK'] = reverse('insumo:ref__get', args=[row['REF']])
            if row['ULT_ENTRADA']:
                row['ULT_ENTRADA'] = row['ULT_ENTRADA'].date()
            else:
                row['ULT_ENTRADA'] = ''
            if row['ULT_SAIDA']:
                row['ULT_SAIDA'] = row['ULT_SAIDA'].date()
            else:
                row['ULT_SAIDA'] = ''

        context.update({
            'headers': ('Nível', 'Insumo', 'Descrição', 'Cor', 'Tamanho',
                        'Depósito', 'Descrição',
                        'Quant.', 'Unid.',
                        'Dt.Última Entrada', 'Dt.Última Saída',
                        'Dt.Inventário'),
            'fields': ('NIVEL', 'REF', 'DESCR', 'COR', 'TAM',
                       'DEPOSITO', 'DESCRICAO',
                       'QUANT', 'UNID',
                       'ULT_ENTRADA', 'ULT_SAIDA',
                       'DT_INVENTARIO'),
            'style': {8: 'text-align: right;'},
            'group': group,
            'data': data,
        })

        return context

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            insumo = form.cleaned_data['insumo']
            conta_estoque = form.cleaned_data['conta_estoque']
            cursor = connections['so'].cursor()
            context.update(
                self.mount_context(cursor, insumo, conta_estoque))
        context['form'] = form
        return render(request, self.template_name, context)


class MapaPorRefs(View):
    Form_class = MapaRefsForm
    template_name = 'insumo/mapa_ref.html'
    title_name = 'Insumos para mapa de compras'

    def mount_context(self, cursor, insumo, conta_estoque, necessidade):
        context = {}
        # if not (insumo or conta_estoque):
        #     context.update({
        #         'msg_erro': 'Especifique ao menos um filtro',
        #     })
        #     return context
        context.update({
            'insumo': insumo,
            'conta_estoque': conta_estoque,
            'necessidade': necessidade,
        })

        data = queries.mapa_refs_simples(
            cursor, insumo, conta_estoque)

        if len(data) == 0:
            context.update({
                'msg_erro':
                    'Nenhum insumo selecionado',
            })
            return context
        for row in data:
            link = reverse(
                'insumo:mapa_compras',
                args=[row['NIVEL'], row['REF'], row['COR'], row['TAM']])
            row['REF|LINK'] = link
            row['COR|LINK'] = link
            row['TAM|LINK'] = link
            row['REF|TARGET'] = '_blank'
            row['COR|TARGET'] = '_blank'
            row['TAM|TARGET'] = '_blank'
            row['REF'] = row['REF'] + ' - ' + row['DESCR']
            row['COR'] = row['COR'] + ' - ' + row['DESCR_COR']
            row['TAM'] = row['TAM'] + ' - ' + row['DESCR_TAM']

        context.update({
            'headers': ['Nível', 'Insumo', 'Cor', 'Tamanho'],
            'fields': ['NIVEL', 'REF', 'COR', 'TAM'],
            'data': data,
        })

        return context

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            insumo = form.cleaned_data['insumo']
            conta_estoque = form.cleaned_data['conta_estoque']
            necessidade = 't'  # form.cleaned_data['necessidade']
            cursor = connections['so'].cursor()
            context.update(
                self.mount_context(cursor, insumo, conta_estoque, necessidade))
        context['form'] = form
        return render(request, self.template_name, context)


class MapaNecessidadeDetalhe(View):
    template_name = 'insumo/necessidade_detalhe.html'
    title_name = 'Detalhe de necessidade de insumo em uma semana'

    def __init__(self, *args, **kwargs):
        super(MapaNecessidadeDetalhe, self).__init__(*args, **kwargs)
        self.new_calc = True

    def mount_context(self, cursor, nivel, ref, cor, tam, semana):
        context = {}

        # Informações gerais
        data_id = queries.insumo_descr(cursor, nivel, ref, cor, tam)

        if len(data_id) == 0:
            context.update({
                'msg_erro': 'Item não encontrado',
            })
            return context

        for row in data_id:
            row['REF'] = row['REF'] + ' - ' + row['DESCR']
            row['COR'] = row['COR'] + ' - ' + row['DESCR_COR']
            if row['TAM'] != row['DESCR_TAM']:
                row['TAM'] = row['TAM'] + ' - ' + row['DESCR_TAM']

        context.update({
            'headers_id': ['Nível', 'Insumo', 'Cor', 'Tamanho', 'Unid.'],
            'fields_id': ['NIVEL', 'REF', 'COR', 'TAM', 'UNID'],
            'data_id': data_id,
        })

        # detalhes da necessidade
        data = queries.insumo_necessidade_detalhe(
            cursor, nivel, ref, cor, tam, semana, new_calc=self.new_calc)

        if len(data) != 0:
            max_digits = 0
            for row in data:
                num_digits = str(row['QTD_INSUMO'])[::-1].find('.')
                max_digits = max(max_digits, num_digits)

            for row in data:
                semana = row['SEMANA'].date()
                row['REF|LINK'] = reverse(
                    'produto:ref__get', args=[row['REF']])
                row['REF'] = row['REF'] + ' - ' + row['DESCR']
                row['OP|LINK'] = reverse('producao:op__get', args=[row['OP']])

            group = ['REF', 'DESCR']
            totalize_grouped_data(data, {
                'group': group,
                'sum': ['QTD_PRODUTO', 'QTD_INSUMO'],
                'count': [],
                'descr': {'OP': 'Totais:'},
                'flags': ['NO_TOT_1'],
                'global_sum': ['QTD_INSUMO'],
                'global_descr': {'QTD_PRODUTO': 'Total geral:'},
                'row_style': 'font-weight: bold;',
            })
            group_rowspan(data, group)

            for row in data:
                row['QTD_INSUMO|DECIMALS'] = max_digits

            context.update({
                'semana': semana,
                'headers': ['Produto a produzir', 'OP',
                            'Quantidade a produzir', 'Quantidade de insumo'],
                'fields': ['REF', 'OP',
                           'QTD_PRODUTO', 'QTD_INSUMO'],
                'style': {3: 'text-align: right;',
                          4: 'text-align: right;'},
                'group': group,
                'data': data,
            })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        cursor = connections['so'].cursor()
        context.update(
            self.mount_context(
                cursor, kwargs['nivel'], kwargs['ref'],
                kwargs['cor'], kwargs['tam'], kwargs['semana']))
        return render(request, self.template_name, context)


class MapaNecessidadeDetalheOld(MapaNecessidadeDetalhe):
    def __init__(self, *args, **kwargs):
        super(MapaNecessidadeDetalheOld, self).__init__(*args, **kwargs)
        self.new_calc = False


def float16digits(qtd):
    # str(qtd) retorna muito mais dígitos que o
    #   {{ field|floatformat:decimals }}
    # por isso crio um float com decimais limitadas a 16.
    # Esta rotina é bem burra e específica
    sqtd = str(qtd)
    if '.' in sqtd:
        sqtd = sqtd[:17]
    else:
        sqtd = sqtd[:16]
    return float(sqtd)


class Previsao(View):
    Form_class = PrevisaoForm
    template_name = 'insumo/previsao.html'
    title_name = 'Previsão'

    def mount_context(self, cursor, periodo):
        context = {}
        if not (periodo):
            context.update({
                'msg_erro': 'Especifique um periodo',
            })
            return context
        context.update({
            'periodo': periodo,
        })

        data = queries.previsao(cursor, periodo)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma previsao de produção encontrada',
            })
            return context

        context.update({
            'prev_descr': data[0]['PREV_DESCR'],
        })

        max_digits = 0
        for row in data:
            qtd = float16digits(row['QTD'])
            num_digits = str(qtd).strip('0')[::-1].find('.')
            max_digits = max(max_digits, num_digits)

        for row in data:
            row['REF|LINK'] = reverse('produto:ref__get', args=[row['REF']])
            if row['COR'] != row['COR_DESCR']:
                row['COR'] = '{} ({})'.format(row['COR'], row['COR_DESCR'])
            if row['TAM'] != row['TAM_DESCR']:
                row['TAM'] = '{} ({})'.format(row['TAM'], row['TAM_DESCR'])

        group = ['NIVEL', 'REF', 'REF_DESCR', 'ALT']
        totalize_grouped_data(data, {
            'group': group,
            'sum': ['QTD'],
            'count': [],
            'descr': {'TAM': 'Total:'},
        })
        group_rowspan(data, group)

        for row in data:
            row['QTD|DECIMALS'] = max_digits

        context.update({
            'headers': ('Nível', 'Referência', 'Descrição', 'Alternativa',
                        'Cor', 'Tamanho', 'Quantidade'),
            'fields': ('NIVEL', 'REF', 'REF_DESCR', 'ALT',
                       'COR', 'TAM', 'QTD'),
            'style': {7: 'text-align: right;'},
            'data': data,
            'group': group,
        })

        return context

    def get(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            periodo = form.cleaned_data['periodo']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, periodo))
        context['form'] = form
        return render(request, self.template_name, context)


class Necessidade1Previsao(View):
    template_name = 'insumo/necessidade_1_previsao.html'
    title_name = 'Necessidade de insumos da previsão'

    def mount_context(self, cursor, periodo):
        context = {}
        if not (periodo):
            context.update({
                'msg_erro': 'Especifique um periodo',
            })
            return context
        context.update({
            'periodo': periodo,
        })

        data = queries.previsao(cursor, periodo)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma previsao de produção encontrada',
            })
            return context

        context.update({
            'prev_descr': data[0]['PREV_DESCR'],
        })

        insumo = []
        while True:
            dual_nivel1 = ''
            union = ''
            for row in data:
                if row['NIVEL'] == '1':
                    dual_select = '''
                        SELECT
                          {nivel} NIVEL
                        , '{ref}' REF
                        , '{cor}' COR
                        , '{tam}' TAM
                        , {qtd} QTD
                        , {alt} ALT
                        FROM SYS.DUAL
                    '''.format(
                        nivel=row['NIVEL'],
                        ref=row['REF'],
                        cor=row['COR'],
                        tam=row['TAM'],
                        qtd=row['QTD'],
                        alt=row['ALT'],
                    )
                    dual_nivel1 += union + dual_select
                    union = ' UNION '
                else:
                    busca_insumo = [
                        item for item in insumo
                        if item['NIVEL'] == row['NIVEL']
                        and item['REF'] == row['REF']
                        and item['COR'] == row['COR']
                        and item['TAM'] == row['TAM']
                        and item['ALT'] == row['ALT']
                        ]
                    if busca_insumo == []:
                        insumo.append(row)
                    else:
                        busca_insumo[0]['QTD'] += row['QTD']
            if dual_nivel1 == '':
                break
            else:
                data = queries.insumos_de_produtos_em_dual(cursor, dual_nivel1)

        insumo = sorted(
            insumo, key=itemgetter('NIVEL', 'REF', 'ALT', 'COR', 'ORD_TAM'))

        max_digits = 0
        for row in data:
            qtd = float16digits(row['QTD'])
            num_digits = str(qtd).strip('0')[::-1].find('.')
            max_digits = max(max_digits, num_digits)

        for row in insumo:
            row['REF|LINK'] = reverse('insumo:ref__get', args=[row['REF']])
            if row['COR'] != row['COR_DESCR']:
                row['COR'] = '{} ({})'.format(row['COR'], row['COR_DESCR'])
            if row['TAM'] != row['TAM_DESCR']:
                row['TAM'] = '{} ({})'.format(row['TAM'], row['TAM_DESCR'])

        group = ['NIVEL', 'REF', 'REF_DESCR', 'ALT']
        totalize_grouped_data(insumo, {
            'group': group,
            'sum': ['QTD'],
            'count': [],
            'descr': {'TAM': 'Total:'},
            'flags': ['NO_TOT_1'],
            'row_style': 'font-weight: bold;',
        })
        group_rowspan(insumo, group)

        for row in insumo:
            row['QTD|DECIMALS'] = max_digits

        context.update({
            'headers': ('Nível', 'Insumo', 'Descrição', 'Alternativa',
                        'Cor', 'Tamanho', 'Quantidade'),
            'fields': ('NIVEL', 'REF', 'REF_DESCR', 'ALT',
                       'COR', 'TAM', 'QTD'),
            'style': {7: 'text-align: right;'},
            'data': insumo,
            'group': group,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        cursor = connections['so'].cursor()
        context.update(self.mount_context(cursor, kwargs['periodo']))
        return render(request, self.template_name, context)


class NecessidadesPrevisoes(View):
    template_name = 'insumo/necessidades_previsoes.html'
    title_name = 'Necessidades das Previsões'

    def mount_context(self, cursor):
        context = {}

        data = queries.previsao(cursor)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma previsao de produção encontrada',
            })
            return context

        previsoes = set()
        for row in data:
            previsoes.add((row['PREV_DESCR'], row['INI_PERIODO']))
        p_data = [{'PREV_DESCR': p[0], 'INI_PERIODO': p[1].date()}
                  for p in previsoes]
        p_data.sort(key=lambda prev: prev['PREV_DESCR'])
        context.update({
            'p_headers': ('Previsão', 'Início de período'),
            'p_fields': ('PREV_DESCR', 'INI_PERIODO'),
            'p_data': p_data,
        })

        insumo = []
        while True:
            dual_nivel1 = ''
            union = ''
            for row in data:
                if row['NIVEL'] == '1':
                    dual_select = '''
                        SELECT
                          {nivel} NIVEL
                        , '{ref}' REF
                        , '{cor}' COR
                        , '{tam}' TAM
                        , {qtd} QTD
                        , {alt} ALT
                        FROM SYS.DUAL
                    '''.format(
                        nivel=row['NIVEL'],
                        ref=row['REF'],
                        cor=row['COR'],
                        tam=row['TAM'],
                        qtd=row['QTD'],
                        alt=row['ALT'],
                    )
                    dual_nivel1 += union + dual_select
                    union = ' UNION '
                else:
                    busca_insumo = [
                        item for item in insumo
                        if item['NIVEL'] == row['NIVEL']
                        and item['REF'] == row['REF']
                        and item['COR'] == row['COR']
                        and item['TAM'] == row['TAM']
                        and item['ALT'] == row['ALT']
                        ]
                    if busca_insumo == []:
                        insumo.append(row)
                    else:
                        busca_insumo[0]['QTD'] += row['QTD']
            if dual_nivel1 == '':
                break
            else:
                data = queries.insumos_de_produtos_em_dual(cursor, dual_nivel1)

        insumo = sorted(
            insumo, key=itemgetter('NIVEL', 'REF', 'ALT', 'COR', 'ORD_TAM'))

        max_digits = 0
        for row in data:
            qtd = float16digits(row['QTD'])
            num_digits = str(qtd).strip('0')[::-1].find('.')
            max_digits = max(max_digits, num_digits)

        for row in insumo:
            row['REF|LINK'] = reverse('insumo:ref__get', args=[row['REF']])
            if row['COR'] != row['COR_DESCR']:
                row['COR'] = '{} ({})'.format(row['COR'], row['COR_DESCR'])
            if row['TAM'] != row['TAM_DESCR']:
                row['TAM'] = '{} ({})'.format(row['TAM'], row['TAM_DESCR'])

        group = ['NIVEL', 'REF', 'REF_DESCR', 'ALT']
        totalize_grouped_data(insumo, {
            'group': group,
            'sum': ['QTD'],
            'count': [],
            'descr': {'TAM': 'Total:'},
            'flags': ['NO_TOT_1'],
        })
        group_rowspan(insumo, group)

        for row in insumo:
            row['QTD|DECIMALS'] = max_digits

        context.update({
            'headers': ('Nível', 'Insumo', 'Descrição', 'Alternativa',
                        'Cor', 'Tamanho', 'Quantidade'),
            'fields': ('NIVEL', 'REF', 'REF_DESCR', 'ALT',
                       'COR', 'TAM', 'QTD'),
            'style': {7: 'text-align: right;'},
            'data': insumo,
            'group': group,
        })

        return context

    def get(self, request):
        context = {'titulo': self.title_name}
        cursor = connections['so'].cursor()
        context.update(self.mount_context(cursor))
        return render(request, self.template_name, context)


class MapaPorSemanaNew(View):
    Form_class = MapaPorSemanaNewForm
    template_name = 'insumo/mapa_sem_new.html'
    title_name = 'Mapa de compras por semana'

    def mount_context_pre(self, cursor, periodo, qtd_semanas):
        if periodo is None:
            return {}

        if qtd_semanas is None:
            qtd_semanas = 1
        periodo_atual = systextil.models.Periodo.confeccao.filter(
            periodo_producao=periodo
        ).values()
        periodo_ini = 0
        periodo_fim = 0
        if periodo_atual:
            periodo_ini = periodo_atual[0]['data_ini_periodo'].date()
            periodo_ini += timedelta(days=1)
            periodo_fim = periodo_ini+timedelta(weeks=qtd_semanas-1)
        periodo_ini_int = periodo_ini.year*10000 + \
            periodo_ini.month*100 + periodo_ini.day

        context = {'periodo': periodo,
                   'periodo_ini': periodo_ini,
                   'periodo_fim': periodo_fim,
                   'qtd_semanas': qtd_semanas,
                   'periodo_ini_int': periodo_ini_int,
                   }

        return context

    def mount_context(
            self, cursor, periodo, qtd_semanas, qtd_itens, nivel, uso, insumo,
            versao):
        cursor = connections['so'].cursor()
        data = queries.insumos_cor_tamanho_usados(
            cursor, qtd_itens, nivel, uso, insumo)
        refs = []
        for row in data:
            refs.append('{}.{}.{}.{}'.format(
                row['nivel'], row['ref'], row['cor'], row['tam']))

        context = {
            'refs': refs,
            'qtd_itens': qtd_itens,
            'nivel': nivel,
            'uso': uso,
            'insumo': insumo,
            'versao': versao,
        }

        return context

    def get(self, request, *args, **kwargs):
        if 'periodo' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            periodo = None
            qtd_semanas = None
            if form.fields['periodo'].initial:
                periodo = form.fields['periodo'].initial
            if form.fields['qtd_semanas'].initial:
                qtd_semanas = form.fields['qtd_semanas'].initial
            cursor = connections['so'].cursor()
            context.update(self.mount_context_pre(
                cursor, periodo, qtd_semanas))
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST.copy())
        if 'periodo' in kwargs:
            form.data['periodo'] = kwargs['periodo']
        if form.is_valid():
            periodo = form.cleaned_data['periodo']
            qtd_semanas = form.cleaned_data['qtd_semanas']
            qtd_itens = form.cleaned_data['qtd_itens']
            nivel = form.cleaned_data['nivel']
            uso = form.cleaned_data['uso']
            insumo = form.cleaned_data['insumo']
            versao = form.cleaned_data['versao']

            insumo = ' '.join(insumo.strip().upper().split())
            form.data['insumo'] = insumo

            cursor = connections['so'].cursor()
            context.update(self.mount_context_pre(
                cursor, periodo, qtd_semanas))
            context.update(self.mount_context(
                cursor, periodo, qtd_semanas, qtd_itens, nivel, uso, insumo,
                versao))
        context['form'] = form
        return render(request, self.template_name, context)


def mapa_novo_sem_ref_new(request, item, dtini, qtdsem):
    return mapa_sem_ref_new(request, item, dtini, qtdsem, 'N')


def mapa_sem_ref_new(request, item, dtini, qtdsem, versao='A'):

    def return_result(result):
        cached_result = result
        cache.set(key_cache, cached_result, timeout=entkeys._DAY*10)
        fo2logger.info('calculated '+key_cache)
        entkeys.add(key_cache, (nivel, ref, cor, tam), timeout=entkeys._DAY*10)
        return cached_result

    # key_cache = make_key_cache()
    key_cache = my_make_key_cache(
        'mapa_sem_ref_new', item, dtini, qtdsem, versao)
    cached_result = cache.get(key_cache)
    if cached_result is not None:
        fo2logger.info('cached '+key_cache)
        return cached_result

    template_name = 'insumo/mapa_sem_ref_new.html'

    nivel = item[0]
    ref = item[2:7]
    cor = item[8:14]
    tam = item[15:18]
    context = {
        'qtdsem': int(qtdsem),
        'versao': versao,
    }

    if len(item) == 2:
        context['th'] = True
    else:
        cursor = connections['so'].cursor()

        data = []

        if versao == 'A':
            datas = insumo.functions.mapa_por_insumo_dados(
                cursor, nivel, ref, cor, tam)
        else:
            datas = insumo.functions.new_mapa_por_insumo_dados(
                cursor, nivel, ref, cor, tam)

        if 'msg_erro' in datas:
            context.update({
                'data': data,
            })
            html = render_to_string(template_name, context)
            return HttpResponse(html)

        data_id = datas['data_id']
        drow = data_id[0]

        drow['REF'] = drow['REF'] + ' (' + drow['DESCR'] + ')'
        drow['COR'] = drow['COR'] + ' (' + drow['DESCR_COR'] + ')'
        if drow['TAM'] != drow['DESCR_TAM']:
            drow['TAM'] = drow['TAM'] + ' (' + drow['DESCR_TAM'] + ')'
        semanas = math.ceil(drow['REPOSICAO'] / 7)
        drow['REP_STR'] = '{}d.({}s.)'.format(drow['REPOSICAO'], semanas)
        drow['QUANT'] = round(drow['QUANT'])

        data_sug = datas['data_sug']
        semana_hoje = datas['semana_hoje']
        semana_recebimento = datas['semana_recebimento']
        dtsem = datetime.datetime.strptime(dtini, '%Y%m%d').date()

        data_adi = datas['data_adi']

        for i in range(int(qtdsem)):
            compra_atrasada = 0
            comprar = 0
            dt_compra = dtsem
            dt_chegada = None

            if len(data_sug) != 0:
                for row in data_sug:
                    if dtsem == semana_hoje and \
                            row['SEMANA_COMPRA'] < semana_hoje:
                        compra_atrasada += row['QUANT']
                        dt_compra = semana_hoje
                        dt_chegada = semana_recebimento
                    if row['SEMANA_COMPRA'] == dtsem:
                        comprar += row['QUANT']
                        dt_chegada = row['SEMANA_RECEPCAO']
                comprar = round(comprar)
                compra_atrasada = round(compra_atrasada)

            movido = round(sum(
                item['QUANT']
                for item in data_adi
                if item['SEMANA_DESTINO'] == dtsem))

            if dt_chegada is None:
                dt_chegada = '-'

            row = drow.copy()

            row.update({
                'nivel': nivel,
                'ref': ref,
                'cor': cor,
                'tam': tam,
                'tam_order': tam.zfill(3),
                'i': i+1,
                'compra_atrasada': compra_atrasada,
                'comprar': comprar,
                'compra_total': compra_atrasada + comprar,
                'dt_compra': dt_compra,
                'dt_chegada': dt_chegada,
                'movido': movido,
            })

            data.append(row)

            dtsem += datetime.timedelta(days=7)

        context.update({
            'data': data,
        })

    html = render_to_string(template_name, context)
    result = HttpResponse(html)
    return return_result(result)


class MapaPorSemana(View):
    Form_class = MapaPorSemanaForm
    template_name = 'insumo/mapa_sem.html'
    title_name = 'Mapa de compras por semana'

    def mount_context_pre(self, cursor, periodo, qtd_semanas):
        if periodo is None:
            return {}

        if qtd_semanas is None:
            qtd_semanas = 1
        periodo_atual = systextil.models.Periodo.confeccao.filter(
            periodo_producao=periodo
        ).values()
        periodo_ini = 0
        periodo_fim = 0
        if periodo_atual:
            periodo_ini = periodo_atual[0]['data_ini_periodo'].date()
            periodo_ini += timedelta(days=1)
            periodo_fim = periodo_ini+timedelta(weeks=qtd_semanas-1)
        periodo_ini_int = periodo_ini.year*10000 + \
            periodo_ini.month*100 + periodo_ini.day

        context = {'periodo': periodo,
                   'periodo_ini': periodo_ini,
                   'periodo_fim': periodo_fim,
                   'qtd_semanas': qtd_semanas,
                   'periodo_ini_int': periodo_ini_int,
                   }

        return context

    def mount_context(
            self, cursor, periodo, qtd_semanas, qtd_itens, nivel, uso, insumo):
        cursor = connections['so'].cursor()
        data = queries.insumos_cor_tamanho_usados(
            cursor, qtd_itens, nivel, uso, insumo)
        refs = []
        for row in data:
            refs.append('{}.{}.{}.{}'.format(
                row['nivel'], row['ref'], row['cor'], row['tam']))

        context = {
            'refs': refs,
            'qtd_itens': qtd_itens,
            'nivel': nivel,
            'uso': uso,
            'insumo': insumo,
        }

        return context

    def get(self, request, *args, **kwargs):
        if 'periodo' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            periodo = None
            if form.fields['periodo'].initial:
                periodo = form.fields['periodo'].initial
            qtd_semanas = None
            if form.fields['qtd_semanas'].initial:
                qtd_semanas = form.fields['qtd_semanas'].initial
            cursor = connections['so'].cursor()
            context.update(self.mount_context_pre(
                cursor, periodo, qtd_semanas))
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST.copy())
        if 'periodo' in kwargs:
            form.data['periodo'] = kwargs['periodo']
        if form.is_valid():
            periodo = form.cleaned_data['periodo']
            qtd_semanas = form.cleaned_data['qtd_semanas']
            qtd_itens = form.cleaned_data['qtd_itens']
            nivel = form.cleaned_data['nivel']
            uso = form.cleaned_data['uso']
            insumo = form.cleaned_data['insumo']

            insumo = ' '.join(insumo.strip().upper().split())
            form.data['insumo'] = insumo

            cursor = connections['so'].cursor()
            context.update(self.mount_context_pre(
                cursor, periodo, qtd_semanas))
            context.update(self.mount_context(
                cursor, periodo, qtd_semanas, qtd_itens, nivel, uso, insumo))
        context['form'] = form
        return render(request, self.template_name, context)


def mapa_sem_ref(request, item, dtini, nsem):
    template_name = 'insumo/mapa_sem_ref.html'
    context = {}
    if len(item) == 2:
        context['th'] = True
    else:
        nivel = item[0]
        ref = item[2:7]
        cor = item[8:14]
        tam = item[15:18]
        cursor = connections['so'].cursor()

        data = queries.insumo_descr(cursor, nivel, ref, cor, tam)
        drow = data[0]

        drow['REF'] = drow['REF'] + ' (' + drow['DESCR'] + ')'
        drow['COR'] = drow['COR'] + ' (' + drow['DESCR_COR'] + ')'
        if drow['TAM'] != drow['DESCR_TAM']:
            drow['TAM'] = drow['TAM'] + ' (' + drow['DESCR_TAM'] + ')'
        semanas = math.ceil(drow['REPOSICAO'] / 7)
        drow['REP_STR'] = '{}d. ({}s.)'.format(drow['REPOSICAO'], semanas)
        drow['QUANT'] = round(drow['QUANT'])

        # Necessidades
        data_ins = queries.insumo_necessidade_semana(
            cursor, nivel, ref, cor, tam, dtini, int(nsem) + semanas)
        necessidade = 0
        for row in data_ins:
            necessidade += row['QTD_INSUMO']
        necessidade = round(necessidade)

        # Previsões
        data_prev = queries.insumo_previsoes_semana_insumo(
            cursor, nivel, ref, cor, tam, dtini, int(nsem) + semanas)

        # Descontando das necessidades previtas as necessidades reais
        prev_idx = len(data_prev) - 1
        if prev_idx >= 0:
            for ness in reversed(data_ins):
                while prev_idx >= 0:
                    if data_prev[prev_idx]['DT_NECESSIDADE'] \
                            <= ness['SEMANA_NECESSIDADE']:
                        data_prev[prev_idx]['QTD'] -= ness['QTD_INSUMO']
                        break
                    else:
                        prev_idx -= 1

        previsao = 0
        for row in data_prev:
            previsao += row['QTD']
        previsao = round(previsao)

        # Recebimentos
        data_irs = queries.insumo_recebimento_semana(
            cursor, nivel, ref, cor, tam, dtini, int(nsem) + semanas)

        recebimentos = 0
        for row in data_irs:
            recebimentos += row['QTD_A_RECEBER']
        recebimentos = round(recebimentos)

        comprar = necessidade + previsao + drow['STQ_MIN'] \
            - drow['QUANT'] - recebimentos

        if comprar < 0:
            excesso = -comprar
            comprar = 0
        else:
            excesso = 0

        if comprar > 0:
            dt_chegada = datetime.date.today() + \
                datetime.timedelta(days=drow['REPOSICAO'])
        else:
            dt_chegada = ''

        context = {
            'data': data,
            'nivel': nivel,
            'ref': ref,
            'cor': cor,
            'tam': tam,
            'tam_order': tam.zfill(3),
            'necessidade': necessidade,
            'previsao': previsao,
            'recebimentos': recebimentos,
            'comprar': comprar,
            'dt_chegada': dt_chegada,
            'excesso': excesso,
        }
    html = render_to_string(template_name, context)
    return HttpResponse(html)


class MapaSemanal(View):
    Form_class = MapaSemanalForm
    template_name = 'insumo/mapa_semanal.html'
    title_name = 'Mapa de compras por semana (Rápido)'

    def mount_context_pre(self, cursor, periodo):
        if periodo is None:
            return {}

        periodo_atual = systextil.models.Periodo.confeccao.filter(
            periodo_producao=periodo
        ).values()
        self.periodo_ini = 0
        if periodo_atual:
            self.periodo_ini = periodo_atual[0]['data_ini_periodo'].date()
            self.periodo_ini += timedelta(days=1)
            periodo_ini_int = self.periodo_ini.year*10000 + \
                self.periodo_ini.month*100 + self.periodo_ini.day

            context = {'periodo': periodo,
                       'periodo_ini': self.periodo_ini,
                       'periodo_ini_int': periodo_ini_int,
                       }

        return context

    def mount_context(self, cursor, periodo, nivel, uso, insumo):
        semana_hoje = segunda(datetime.date.today())

        cursor = connections['so'].cursor()
        data = queries.insumos_cor_tamanho_usados(
            cursor, '0', nivel, uso, insumo)

        for row in data:
            info = queries.insumo_descr(
                cursor, row['nivel'], row['ref'], row['cor'], row['tam'])
            if info:
                rowi = info[0]

                row['REF'] = rowi['REF'] + ' (' + rowi['DESCR'] + ')'
                row['COR'] = rowi['COR'] + ' (' + rowi['DESCR_COR'] + ')'
                if rowi['TAM'] == rowi['DESCR_TAM']:
                    row['TAM'] = rowi['TAM'] + ' (' + rowi['DESCR_TAM'] + ')'
                else:
                    row['TAM'] = rowi['TAM']

                semanas = math.ceil(rowi['REPOSICAO'] / 7)
                row['REP_STR'] = '{}d.({}s.)'.format(
                    rowi['REPOSICAO'], semanas)
                row['STQ_MIN'] = round(rowi['STQ_MIN'])
                row['LOTE_MULTIPLO'] = round(rowi['LOTE_MULTIPLO'])
                row['QUANT'] = round(rowi['QUANT'])
                row['UNID'] = rowi['UNID']

                row['compra_atrasada'] = 0
                row['comprar'] = 0
                row['dt_chegada'] = ' '

                sc = models.SugestaoCompra.objects.filter(
                    nivel=row['nivel'],
                    referencia=row['ref'],
                    tamanho=row['tam'],
                    cor=row['cor'],
                ).order_by('-data').first()
                if sc:
                    scd = models.SugestaoCompraDatas.objects.filter(
                        sugestao=sc).order_by('data_compra').values()
                    for sugest in scd:
                        if sugest['data_compra'] < semana_hoje:
                            row['compra_atrasada'] += sugest['qtd']
                        elif sugest['data_compra'] == self.periodo_ini:
                            row['comprar'] = round(sugest['qtd'])
                            row['dt_chegada'] = sugest['data_recepcao']
                row['compra_atrasada'] = round(row['compra_atrasada'])

        context = {
            'data': data,
            'nivel': nivel,
            'uso': uso,
            'insumo': insumo,
        }

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}

        form = self.Form_class()
        periodo = None
        if form.fields['periodo'].initial:
            periodo = form.fields['periodo'].initial
        context['form'] = form

        cursor = connections['so'].cursor()
        context.update(self.mount_context_pre(cursor, periodo))

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}

        form = self.Form_class(request.POST.copy())
        if form.is_valid():
            periodo = form.cleaned_data['periodo']
            nivel = form.cleaned_data['nivel']
            uso = form.cleaned_data['uso']
            insumo = form.cleaned_data['insumo']

            insumo = ' '.join(insumo.strip().upper().split())
            form.data['insumo'] = insumo

            cursor = connections['so'].cursor()
            context.update(self.mount_context_pre(cursor, periodo))
            context.update(self.mount_context(
                cursor, periodo, nivel, uso, insumo))

        context['form'] = form
        return render(request, self.template_name, context)
