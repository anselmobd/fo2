import datetime
import math
import os
import re
import time
from operator import itemgetter
from pprint import pprint

from django.db import connections
from django.db.models import Q
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from fo2 import settings
from fo2.models import rows_to_dict_list
from fo2.template import group_rowspan

from geral.models import Dispositivos, RoloBipado
from utils.forms import FiltroForm
from utils.functions import segunda, max_not_None, min_not_None
from utils.views import totalize_grouped_data

import insumo.models as models
from .forms import \
    EstoqueForm, \
    MapaRefsForm, \
    NecessidadeForm, \
    PrevisaoForm, \
    RefForm, \
    RoloForm, \
    RolosBipadosForm, \
    ReceberForm


def index(request):
    return render(request, 'insumo/index.html')


class Ref(View):
    Form_class = RefForm
    template_name = 'insumo/ref.html'
    title_name = 'Insumos'

    def mount_context(self, cursor, item):
        context = {'item': item}

        if len(item) == 5:
            data = models.item_count_nivel(cursor, item)
            row = data[0]
            if row['COUNT'] > 1:
                context.update({
                    'msg_erro':
                        'Referência de insumo ambígua. Informe o nível.',
                })
                return context
            elif row['COUNT'] == 1:
                nivel = row['NIVEL']
                ref = item
        else:
            nivel = item[0]
            ref = item[-5:]
            data = models.item_count_nivel(cursor, ref, nivel)
            row = data[0]
        if row['COUNT'] == 0:
            context.update({
                'msg_erro': 'Referência de insumo não encontrada',
            })
            return context
        context.update({
            'nivel': nivel,
            'ref': ref,
        })

        # Informações básicas
        data = models.ref_inform(cursor, nivel, ref)
        context.update({
            'headers': ('Descrição', 'Unidade de medida', 'Conta de estoque',
                        'NCM', 'Código Contábil'),
            'fields': ('DESCR', 'UM', 'CONTA_ESTOQUE',
                       'NCM', 'CODIGO_CONTABIL'),
            'data': data,
        })

        # Informações básicas - tecidos
        if nivel == '2':
            context.update({
                'm_headers': ('Linha de produto', 'Coleção',
                              'Artigo de produo', 'Tipo de produto'),
                'm_fields': ('LINHA', 'COLECAO',
                             'ARTIGO', 'TIPO_PRODUTO'),
                'm_data': data,
            })

        # Cores
        c_data = models.ref_cores(cursor, nivel, ref)
        if len(c_data) != 0:
            context.update({
                'c_headers': ('Cor', 'Descrição'),
                'c_fields': ('COR', 'DESCR'),
                'c_data': c_data,
            })

        # Tamanhos
        t_data = models.ref_tamanhos(cursor, nivel, ref)
        if len(t_data) != 0:
            context.update({
                't_headers': ('Tamanho', 'Descrição', 'Complemento'),
                't_fields': ('TAM', 'DESCR', 'COMPL'),
                't_data': t_data,
            })

        # Parametros
        p_data = models.ref_parametros(cursor, nivel, ref)
        if len(p_data) != 0:
            context.update({
                'p_headers': ('Tamanho', 'Cor', 'Depósito', 'Estóque mínimo',
                              'Estoque máximo', 'Lead'),
                'p_fields': ('TAM', 'COR', 'DEPOSITO', 'ESTOQUE_MINIMO',
                             'ESTOQUE_MAXIMO', 'LEAD'),
                'p_data': p_data,
            })

        # Usado em
        u_data = models.ref_usado_em(cursor, nivel, ref)
        u_link = ('REF')
        for row in u_data:
            row['LINK'] = '/produto/ref/{}'.format(row['REF'])
        if len(u_data) != 0:
            context.update({
                'u_headers': ('Tipo', 'Referência', 'Descrição',
                              'Alternativa', 'Consumo', 'Estágio'),
                'u_fields': ('TIPO', 'REF', 'DESCR',
                             'ALTERNATIVA', 'CONSUMO', 'ESTAGIO'),
                'u_data': u_data,
                'u_link': u_link,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'item' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'item' in kwargs:
            form.data['item'] = kwargs['item']
        if form.is_valid():
            item = form.cleaned_data['item']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, item))
        context['form'] = form
        return render(request, self.template_name, context)


class ListaInsumo(View):
    Form_class = FiltroForm
    template_name = 'insumo/lista_insumo.html'
    title_name = 'Listagem de insumos'

    def mount_context(self, cursor, busca):
        context = {'busca': busca}

        # Informações básicas
        data = models.lista_insumo(cursor, busca)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhum insumo selecionado',
            })
        else:
            link = ('REF')
            for row in data:
                row['LINK'] = '/insumo/ref/{}'.format(row['REF'])
            context.update({
                'headers': ('#', 'Nível', 'Referência', 'Descrição'),
                'fields': ('NUM', 'NIVEL', 'REF', 'DESCR'),
                'data': data,
                'link': link,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'busca' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'busca' in kwargs:
            form.data['busca'] = kwargs['busca']
        if form.is_valid():
            busca = form.cleaned_data['busca']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, busca))
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
    data = models.rolo_ref(cursor, barcode)
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
    Form_class = RoloForm
    template_name = 'insumo/bipa_rolo.html'
    title_name = 'Bipa rolo'

    def mount_context(self, request, form):
        cursor = connections['so'].cursor()

        rolo = form.cleaned_data['rolo']
        identificado = form.cleaned_data['identificado']

        context = {}

        data = models.rolo_ref(cursor, rolo)
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

        data = models.necessidade(
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
            row['REF|LINK'] = '/insumo/ref/{}'.format(row['REF'])
            row['OPS'] = re.sub(
                r'([1234567890]+)',
                r'<a href="/lotes/op/\1">\1&nbsp;<span '
                'class="glyphicon glyphicon-link" '
                'aria-hidden="true"></span></a>',
                str(row['OPS']))
            row['REFS'] = re.sub(
                r'([^, ]+)',
                r'<a href="/produto/ref/\1">\1&nbsp;<span '
                'class="glyphicon glyphicon-link" '
                'aria-hidden="true"></span></a>',
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

        data = models.receber(cursor, insumo, conta_estoque, recebimento)

        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhum pedido de insumos encontrado',
            })
            return context

        for row in data:
            row['REF|LINK'] = '/insumo/ref/{}'.format(row['REF'])
            row['DT_ENTREGA'] = row['DT_ENTREGA'].date()

        group = ['NIVEL', 'REF', 'DESCR', 'COR', 'TAM']
        totalize_grouped_data(data, {
            'group': group,
            'sum': ['QTD_PEDIDA', 'QTD_RECEBIDA', 'QTD_A_RECEBER'],
            'count': [],
            'descr': {'DT_ENTREGA': 'Totais:'}
        })
        group_rowspan(data, group)

        context.update({
            'headers': ('Nível', 'Insumo', 'Descrição', 'Cor',
                        'Tamanho', 'Dt. Entrega',
                        'Qtd.Pedida', 'Qtd.Recebida', '%Recebido',
                        'Qtd.A receber', '%A receber', 'Pedidos'),
            'fields': ('NIVEL', 'REF', 'DESCR', 'COR',
                       'TAM', 'DT_ENTREGA',
                       'QTD_PEDIDA', 'QTD_RECEBIDA', 'P_RECEBIDO',
                       'QTD_A_RECEBER', 'P_A_RECEBER', 'PEDIDOS'),
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

        data = models.estoque(cursor, insumo, conta_estoque)

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
            row['REF|LINK'] = '/insumo/ref/{}'.format(row['REF'])
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


class MapaRefs(View):
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

        data = models.mapa_refs(cursor, insumo, conta_estoque, necessidade)

        if len(data) == 0:
            context.update({
                'msg_erro':
                    'Nenhum insumo selecionado',
            })
            return context
        for row in data:
            link = reverse(
                'insumo_mapa',
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
            necessidade = form.cleaned_data['necessidade']
            cursor = connections['so'].cursor()
            context.update(
                self.mount_context(cursor, insumo, conta_estoque, necessidade))
        context['form'] = form
        return render(request, self.template_name, context)


class Mapa(View):
    template_name = 'insumo/mapa.html'
    title_name = 'Mapa de compras'

    def mount_context(self, cursor, nivel, ref, cor, tam):
        context = {}

        # Informações gerais
        data_id = models.insumo_descr(cursor, nivel, ref, cor, tam)

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
            if row['ULT_ENTRADA']:
                row['ULT_ENTRADA'] = row['ULT_ENTRADA'].date()
            else:
                row['ULT_ENTRADA'] = ''
            if row['ULT_SAIDA']:
                row['ULT_SAIDA'] = row['ULT_SAIDA'].date()
            else:
                row['ULT_SAIDA'] = ''
            if row['DT_INVENTARIO']:
                row['DT_INVENTARIO'] = row['DT_INVENTARIO'].date()
            else:
                row['DT_INVENTARIO'] = ''
            semanas = math.ceil(row['REPOSICAO'] / 7)
            row['REP_STR'] = '{}d. ({}s.)'.format(row['REPOSICAO'], semanas)

        context.update({
            'headers_id': ['Nível', 'Insumo', 'Cor', 'Tamanho',
                           'Reposição', 'Est.Mínimo', 'Múltiplo',
                           'Estoque', 'Unid.',
                           'Última Entrada', 'Última Saída',
                           'Inventário'],
            'fields_id': ['NIVEL', 'REF', 'COR', 'TAM',
                          'REP_STR', 'STQ_MIN', 'LOTE_MULTIPLO',
                          'QUANT', 'UNID',
                          'ULT_ENTRADA', 'ULT_SAIDA',
                          'DT_INVENTARIO'],
            'data_id': data_id,
        })

        semana_hoje = segunda(datetime.date.today())

        qtd_estoque = data_id[0]['QUANT']
        estoque_minimo = data_id[0]['STQ_MIN']
        dias_reposicao = data_id[0]['REPOSICAO']
        lote_multiplo = data_id[0]['LOTE_MULTIPLO']

        # Necessidades
        data_ins = models.insumo_necessidade_semana(
            cursor, nivel, ref, cor, tam)

        max_digits = 0
        for row in data_ins:
            num_digits = str(row['QTD_INSUMO'])[::-1].find('.')
            max_digits = max(max_digits, num_digits)

        semana1 = None
        for row in data_ins:
            row['SEMANA_NECESSIDADE'] = row['SEMANA_NECESSIDADE'].date()
            row['SEMANA_NECESSIDADE|LINK'] = reverse(
                'insumo_necessidade_detalhe',
                args=[nivel, ref, cor, tam, row['SEMANA_NECESSIDADE']])
            row['SEMANA_NECESSIDADE|TARGET'] = '_blank'
            row['QTD_INSUMO|DECIMALS'] = max_digits
            if semana1 is None:
                semana1 = row['SEMANA_NECESSIDADE']
            if semana1 < semana_hoje and \
                    row['SEMANA_NECESSIDADE'] <= semana_hoje:
                row['QTD_INSUMO|STYLE'] = 'font-weight: bold;'

        context.update({
            'headers_ins': ['Semana da necessidade', 'Quantidade necessária'],
            'fields_ins': ['SEMANA_NECESSIDADE', 'QTD_INSUMO'],
            'style_ins': {2: 'text-align: right;'},
            'data_ins': data_ins,
        })

        # Previsões
        # data_ins = models.insumo_previsoes_semana_insumo(
        #     cursor, nivel, ref, cor, tam)

        # Recebimentos
        data_irs = models.insumo_recebimento_semana(
            cursor, nivel, ref, cor, tam)

        max_digits = 0
        for row in data_irs:
            num_digits = str(row['QTD_A_RECEBER'])[::-1].find('.')
            max_digits = max(max_digits, num_digits)

        semana1 = None
        for row in data_irs:
            row['SEMANA_ENTREGA'] = row['SEMANA_ENTREGA'].date()
            row['QTD_A_RECEBER|DECIMALS'] = max_digits
            if semana1 is None:
                semana1 = row['SEMANA_ENTREGA']
            if semana1 < semana_hoje and row['SEMANA_ENTREGA'] <= semana_hoje:
                row['QTD_A_RECEBER|STYLE'] = 'font-weight: bold;'

        context.update({
            'headers_irs': ['Semana do recebimento', 'Quantidade a receber'],
            'fields_irs': ['SEMANA_ENTREGA', 'QTD_A_RECEBER'],
            'style_irs': {2: 'text-align: right;'},
            'data_irs': data_irs,
        })

        # Dicionários por semana (sem passado)
        necessidades = {}
        pri_necessidade = None
        ult_necessidade = None
        for row in data_ins:
            semana = max(
                row['SEMANA_NECESSIDADE'],
                semana_hoje)
            if semana in necessidades:
                necessidades[semana] += row['QTD_INSUMO']
            else:
                necessidades[semana] = row['QTD_INSUMO']
            if pri_necessidade is None:
                pri_necessidade = semana
            ult_necessidade = semana

        recebimentos = {}
        pri_recebimento = None
        ult_recebimento = None
        for row in data_irs:
            semana = max(
                row['SEMANA_ENTREGA'],
                semana_hoje)
            if semana in recebimentos:
                recebimentos[semana] += row['QTD_A_RECEBER']
            else:
                recebimentos[semana] = row['QTD_A_RECEBER']
            if pri_recebimento is None:
                pri_recebimento = semana
            ult_recebimento = semana

        # criando mapa de compras
        semana = semana_hoje

        semana_fim = max_not_None(
            ult_recebimento,
            ult_necessidade)
        semana_fim += datetime.timedelta(days=7)

        data = []
        estoque = qtd_estoque
        while semana <= semana_fim:
            if semana in recebimentos:
                recebimento = recebimentos[semana]
            else:
                recebimento = 0

            if semana in necessidades:
                necessidade = necessidades[semana]
            else:
                necessidade = 0

            data.append({
                'DATA': semana,
                'NECESSIDADE': necessidade,
                'RECEBIMENTO': recebimento,
                'ESTOQUE': estoque,
                'ESTOQUE_IDEAL': estoque,
                'COMPRAR': 0,
                'RECEBER': 0,
                'RECEBER_IDEAL': 0,
                'RECEBER_IDEAL_ANTES': 0,
            })
            estoque = estoque - necessidade + recebimento

            semana += datetime.timedelta(days=7)

        # monta sugestões de compra
        data_sug = []
        for i in range(len(data)):
            row = data[i]
            sugestao_quatidade = 0
            if row['ESTOQUE_IDEAL'] < estoque_minimo:
                sugestao_quatidade = estoque_minimo - row['ESTOQUE_IDEAL']
                sugestao_quatidade = max(sugestao_quatidade, lote_multiplo)
                sugestao_receber_ideal = row['DATA'] + \
                    datetime.timedelta(days=-7)
                sugestao_receber = row['DATA'] + datetime.timedelta(days=-7)
                sugestao_comprar = segunda(
                    sugestao_receber +
                    datetime.timedelta(days=-dias_reposicao))
                data_sug.append({
                    'SEMANA_COMPRA': sugestao_comprar,
                    'SEMANA_RECEPCAO': sugestao_receber,
                    'QUANT': sugestao_quatidade,
                })
                if sugestao_comprar < semana_hoje:
                    avancar = semana_hoje - sugestao_comprar
                    delta_avancar = datetime.timedelta(days=avancar.days)
                    sugestao_comprar += delta_avancar
                    sugestao_receber += delta_avancar

            if sugestao_quatidade != 0:

                if semana_fim <= sugestao_receber:
                    semana = semana_fim + datetime.timedelta(days=7)
                    semana_fim = sugestao_receber + datetime.timedelta(days=7)
                    while semana <= semana_fim:
                        data.append({
                            'DATA': semana,
                            'NECESSIDADE': 0,
                            'RECEBIMENTO': 0,
                            'ESTOQUE': 0,
                            'ESTOQUE_IDEAL': 0,
                            'COMPRAR': 0,
                            'RECEBER': 0,
                            'RECEBER_IDEAL': 0,
                            'RECEBER_IDEAL_ANTES': 0,
                        })
                        semana += datetime.timedelta(days=7)

                estoque = qtd_estoque
                estoque_ideal = qtd_estoque
                for row in data:
                    if row['DATA'] == sugestao_comprar:
                        row['COMPRAR'] += sugestao_quatidade
                    if row['DATA'] == sugestao_receber:
                        row['RECEBER'] += sugestao_quatidade
                    if sugestao_receber_ideal < semana_hoje:
                        if row['DATA'] == semana_hoje:
                            row['RECEBER_IDEAL_ANTES'] += sugestao_quatidade
                    else:
                        if row['DATA'] == sugestao_receber_ideal:
                            row['RECEBER_IDEAL'] += sugestao_quatidade

                    row['ESTOQUE'] = estoque
                    estoque = estoque - row['NECESSIDADE'] + \
                        row['RECEBIMENTO'] + row['RECEBER']

                    row['ESTOQUE_IDEAL'] = \
                        row['RECEBER_IDEAL_ANTES'] + estoque_ideal
                    estoque_ideal = row['RECEBER_IDEAL_ANTES'] + \
                        estoque_ideal - row['NECESSIDADE'] + \
                        row['RECEBIMENTO'] + row['RECEBER_IDEAL']

        max_digits = 0
        for row in data_sug:
            num_digits = str(row['QUANT'])[::-1].find('.')
            max_digits = max(max_digits, num_digits)

        semana1 = None
        for row in data_sug:
            row['QUANT|DECIMALS'] = max_digits
            if semana1 is None:
                semana1 = row['SEMANA_COMPRA']
            if semana1 < semana_hoje and row['SEMANA_COMPRA'] <= semana_hoje:
                row['QUANT|STYLE'] = 'font-weight: bold;'

        context.update({
            'headers_sug': ['Semana de compra', 'Semana de chegada',
                            'Quantidade'],
            'fields_sug': ['SEMANA_COMPRA', 'SEMANA_RECEPCAO', 'QUANT'],
            'style_sug': {3: 'text-align: right;'},
            'data_sug': data_sug,
        })

        max_digits = 0
        for row in data:
            num_digits = max(
                str(row['ESTOQUE'])[::-1].find('.'),
                str(row['NECESSIDADE'])[::-1].find('.'),
                str(row['RECEBIMENTO'])[::-1].find('.'),
                str(row['COMPRAR'])[::-1].find('.'),
                str(row['RECEBER'])[::-1].find('.'),
                )
            max_digits = max(max_digits, num_digits)

        for row in data:
            row['ESTOQUE|DECIMALS'] = max_digits
            row['NECESSIDADE|DECIMALS'] = max_digits
            row['RECEBIMENTO|DECIMALS'] = max_digits
            row['COMPRAR|DECIMALS'] = max_digits
            row['RECEBER|DECIMALS'] = max_digits

        context.update({
            'headers': ['Semana', 'Estoque',
                        'Necessidade', 'Recebimento',
                        'Compra sugerida', 'Recebimento sugerido'],
            'fields': ['DATA', 'ESTOQUE',
                       'NECESSIDADE', 'RECEBIMENTO',
                       'COMPRAR', 'RECEBER'],
            'style': {2: 'text-align: right;',
                      3: 'text-align: right;',
                      4: 'text-align: right;',
                      5: 'text-align: right;',
                      6: 'text-align: right;'},
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        cursor = connections['so'].cursor()
        context.update(
            self.mount_context(
                cursor, kwargs['nivel'], kwargs['ref'],
                kwargs['cor'], kwargs['tam']))
        return render(request, self.template_name, context)


class MapaNecessidadeDetalhe(View):
    template_name = 'insumo/necessidade_detalhe.html'
    title_name = 'Detalhe de necessidade de insumo em uma semana'

    def mount_context(self, cursor, nivel, ref, cor, tam, semana):
        context = {}

        # Informações gerais
        data_id = models.insumo_descr(cursor, nivel, ref, cor, tam)

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
        data = models.insumo_necessidade_detalhe(
            cursor, nivel, ref, cor, tam, semana)

        max_digits = 0
        for row in data:
            num_digits = str(row['QTD_INSUMO'])[::-1].find('.')
            max_digits = max(max_digits, num_digits)

        for row in data:
            semana = row['SEMANA'].date()
            row['REF|LINK'] = reverse('ref_ref', args=[row['REF']])
            row['REF'] = row['REF'] + ' - ' + row['DESCR']
            row['OP|LINK'] = reverse('producao:op_op', args=[row['OP']])

        group = ['REF', 'DESCR']
        totalize_grouped_data(data, {
            'group': group,
            'sum': ['QTD_PRODUTO', 'QTD_INSUMO'],
            'count': [],
            'descr': {'OP': 'Totais:'}
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

        data = models.previsao(cursor, periodo)
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
            row['QTD|DECIMALS'] = max_digits
            row['REF|LINK'] = '/produto/ref/{}'.format(row['REF'])
            if row['COR'] != row['COR_DESCR']:
                row['COR'] = '{} ({})'.format(row['COR'], row['COR_DESCR'])
            if row['TAM'] != row['TAM_DESCR']:
                row['TAM'] = '{} ({})'.format(row['TAM'], row['TAM_DESCR'])

        context.update({
            'headers': ('Nível', 'Referência', 'Descrição',
                        'Cor', 'Tamanho',
                        'Alternativa', 'Quantidade'),
            'fields': ('NIVEL', 'REF', 'REF_DESCR',
                       'COR', 'TAM',
                       'ALT', 'QTD'),
            'style': {7: 'text-align: right;'},
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
            periodo = form.cleaned_data['periodo']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, periodo))
        context['form'] = form
        return render(request, self.template_name, context)


class Necessidade1Previsao(View):
    template_name = 'insumo/necessidade_previsao.html'
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

        data = models.previsao(cursor, periodo)
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
                data = models.necessidade_previsao(cursor, dual_nivel1)

        insumo = sorted(
            insumo, key=itemgetter('NIVEL', 'REF', 'COR', 'ORD_TAM', 'ALT'))

        max_digits = 0
        for row in data:
            qtd = float16digits(row['QTD'])
            num_digits = str(qtd).strip('0')[::-1].find('.')
            max_digits = max(max_digits, num_digits)

        for row in insumo:
            row['QTD|DECIMALS'] = max_digits
            row['REF|LINK'] = '/insumo/ref/{}'.format(row['REF'])

        context.update({
            'headers': ('Nível', 'Insumo',
                        'Cor', 'Tamanho',
                        'Alternativa', 'Quantidade'),
            'fields': ('NIVEL', 'REF',
                       'COR', 'TAM',
                       'ALT', 'QTD'),
            'style': {6: 'text-align: right;'},
            'data': insumo,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        cursor = connections['so'].cursor()
        context.update(self.mount_context(cursor, kwargs['periodo']))
        return render(request, self.template_name, context)


class NecessidadesPrevisoes(View):
    pass
