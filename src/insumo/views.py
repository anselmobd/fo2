import os
import re
import time
from pprint import pprint
import datetime
import math

from django.urls import reverse
from django.shortcuts import render, redirect
from django.db import connections
from django.views import View
from django.db import connections
from django.http import JsonResponse, HttpResponse

from fo2 import settings
from fo2.models import rows_to_dict_list
from fo2.template import group_rowspan

from geral.models import Dispositivos, RoloBipado
from utils.forms import FiltroForm
from utils.views import totalize_grouped_data
from utils.functions import segunda, max_not_None, min_not_None

import insumo.models as models
from .forms import RefForm, RolosBipadosForm, NecessidadeForm, ReceberForm, \
                   EstoqueForm, MapaRefsForm


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
            nivedatetimel = item[0]
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
    sql = """
        SELECT
          x.CODIGO_ROLO ROLO
        , x.PANOACAB_NIVEL99 NIVEL
        , x.PANOACAB_GRUPO REF
        , x.PANOACAB_SUBGRUPO TAM
        , x.PANOACAB_ITEM COR
        FROM PCPT_020 x -- cadastro de rolos
        WHERE x.CODIGO_ROLO = %s
    """
    cursor.execute(sql, (barcode,))
    data = rows_to_dict_list(cursor)
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
            rolos = rolos.filter(dispositivo__nome__icontains=dispositivo)
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
            data = []
            dir_filename = os.path.join('insumos_rolos_bipados', filename)
            arq = os.path.join(settings.MEDIA_ROOT, dir_filename)
            with open(arq, 'w') as f:
                for rolo in rolos:
                    row = rolo.__dict__
                    row['dispositivo'] = rolo.dispositivo
                    data.append(row)
                    print("{:06}{:09}".format(1, rolo.rolo), file=f)
            context.update({
                'filename': dir_filename,
                'headers': ('dispositivo', 'Rolo', 'Data/hora',
                            'Referencia', 'Tamanho', 'Cor'),
                'fields': ('dispositivo', 'rolo', 'date',
                           'referencia', 'tamanho', 'cor'),
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
            'style': {'QUANT': 'text-align: right;',
                      'Quant.': 'text-align: right;'},
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

        context.update({
            'headers_id': ['Nível', 'Insumo', 'Cor', 'Tamanho',
                           'Est.Mínimo', 'Rep.', 'Múltiplo',
                           'Estoque', 'Unid.',
                           'Última Entrada', 'Última Saída',
                           'Inventário'],
            'fields_id': ['NIVEL', 'REF', 'COR', 'TAM',
                          'STQ_MIN', 'REPOSICAO', 'LOTE_MULTIPLO',
                          'QUANT', 'UNID',
                          'ULT_ENTRADA', 'ULT_SAIDA',
                          'DT_INVENTARIO'],
            'data_id': data_id,
        })

        semana_hoje = segunda(datetime.date.today())

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

        for row in data_ins:
            row['SEMANA_NECESSIDADE'] = row['SEMANA_NECESSIDADE'].date()
            row['QTD_INSUMO|DECIMALS'] = max_digits

        context.update({
            'headers_ins': ['Semana da necessidade', 'Quantidade necessária'],
            'fields_ins': ['SEMANA_NECESSIDADE', 'QTD_INSUMO'],
            'style_ins': {'QTD_INSUMO': 'text-align: right;',
                          'Quantidade necessária': 'text-align: right;'},
            'data_ins': data_ins,
        })

        # Recebimentos
        data_irs = models.insumo_recebimento_semana(
            cursor, nivel, ref, cor, tam)

        max_digits = 0
        for row in data_irs:
            num_digits = str(row['QTD_A_RECEBER'])[::-1].find('.')
            max_digits = max(max_digits, num_digits)

        for row in data_irs:
            row['SEMANA_ENTREGA'] = row['SEMANA_ENTREGA'].date()
            row['QTD_A_RECEBER|DECIMALS'] = max_digits

        context.update({
            'headers_irs': ['Semana do recebimento', 'Quantidade a receber'],
            'fields_irs': ['SEMANA_ENTREGA', 'QTD_A_RECEBER'],
            'style_irs': {'QTD_A_RECEBER': 'text-align: right;',
                          'Quantidade a receber': 'text-align: right;'},
            'data_irs': data_irs,
        })

        # Dicionários por semana (sem passado)
        estoque = {}
        estoque[semana_hoje] = data_id[0]['QUANT']

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
        estoque_final = 0
        while semana <= semana_fim:
            if semana in recebimentos:
                recebimento = recebimentos[semana]
            else:
                recebimento = 0

            if semana in necessidades:
                necessidade = necessidades[semana]
            else:
                necessidade = 0

            if semana == semana_hoje:
                qtd_estoque = estoque[semana]
            else:
                qtd_estoque = qtd_estoque - necessidade + recebimento

            data.append({
                'DATA': semana,
                'NECESSIDADE': necessidade,
                'RECEBIMENTO': recebimento,
                'ESTOQUE': qtd_estoque,
                'COMPRAR': 0,
                'RECEBER': 0,
            })
            semana += datetime.timedelta(days=7)

        # monta sugestões de compra
        for i in range(len(data)):
            row = data[i]
            sugestao_quatidade = 0
            if row['ESTOQUE'] < estoque_minimo:
                sugestao_quatidade = estoque_minimo - row['ESTOQUE']
                sugestao_quatidade = max(sugestao_quatidade, lote_multiplo)
                sugestao_receber = row['DATA']
                sugestao_comprar = segunda(
                    row['DATA'] + datetime.timedelta(days=-dias_reposicao))
                if sugestao_comprar < semana_hoje:
                    avancar = semana_hoje - sugestao_comprar
                    delta_avancar = datetime.timedelta(days=avancar.days)
                    sugestao_comprar += delta_avancar
                    sugestao_receber += delta_avancar

            if sugestao_quatidade != 0:

                if semana_fim < sugestao_receber:
                    semana = semana_fim + datetime.timedelta(days=7)
                    semana_fim = sugestao_receber
                    while semana <= semana_fim:
                        data.append({
                            'DATA': semana,
                            'NECESSIDADE': 0,
                            'RECEBIMENTO': 0,
                            'ESTOQUE': 0,
                            'COMPRAR': 0,
                            'RECEBER': 0,
                        })
                        semana += datetime.timedelta(days=7)

                estoque = None
                for row in data:
                    if row['DATA'] == sugestao_comprar:
                        row['COMPRAR'] = sugestao_quatidade
                    if row['DATA'] == sugestao_receber:
                        row['RECEBER'] = sugestao_quatidade

                    if estoque is None:
                        estoque = row['ESTOQUE']
                    else:
                        row['ESTOQUE'] = estoque - row['NECESSIDADE'] + \
                            row['RECEBIMENTO'] + row['RECEBER']

        context.update({
            'headers': ['Semana', 'Estoque',
                        'Necessidade', 'Recebimento',
                        'Compra sugerida', 'Recebimento sugerido'],
            'fields': ['DATA', 'ESTOQUE',
                       'NECESSIDADE', 'RECEBIMENTO',
                       'COMPRAR', 'RECEBER'],
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
