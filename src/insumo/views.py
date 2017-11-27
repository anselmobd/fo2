import re
from pprint import pprint

from django.shortcuts import render, redirect
from django.db import connections
from django.views import View
from django.db import connections
from django.http import JsonResponse, HttpResponse

from fo2.models import rows_to_dict_list

from geral.models import Dispositivos
from utils.forms import FiltroForm

import insumo.models as models
from .forms import RefForm


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
    return JsonResponse(data[0])
    return HttpResponse('')
