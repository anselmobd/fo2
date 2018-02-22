import os
import re
import time
from pprint import pprint

from django.shortcuts import render, redirect
from django.db import connections
from django.views import View
from django.db import connections
from django.http import JsonResponse, HttpResponse

from fo2 import settings
from fo2.models import rows_to_dict_list

from geral.models import Dispositivos, RoloBipado
from utils.forms import FiltroForm

import insumo.models as models
from .forms import RefForm, RolosBipadosForm, NecessidadeForm


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
            print(nivel, ref)
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

    def mount_context(self, cursor, op, data_corte, conta_estoque, ref):
        context = {}
        if not (op or data_corte or conta_estoque or ref):
            context.update({
                'msg_erro': 'Especifique ao menos um filtro',
            })
            return context

        context.update({
            'op': op,
            'data_corte': data_corte,
            'conta_estoque': conta_estoque,
            'ref': ref,
        })

        data = models.necessidade(cursor, op, data_corte, conta_estoque, ref)

        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma necessidade de insumos encontrada',
            })
            return context

        for row in data:
            row['REF|LINK'] = '/insumo/ref/{}'.format(row['REF'])
        context.update({
            'headers': ('Nível', 'Referência', 'Cor', 'Tamanho', 'Quant.'),
            'fields': ('NIVEL', 'REF', 'COR', 'TAM', 'QTD'),
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
            conta_estoque = form.cleaned_data['conta_estoque']
            ref = form.cleaned_data['ref']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(
                cursor, op, data_corte, conta_estoque, ref))
        context['form'] = form
        return render(request, self.template_name, context)
