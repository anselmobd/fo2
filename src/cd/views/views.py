from pprint import pprint
import re
import datetime
from datetime import timedelta
from pytz import utc

from django.db import IntegrityError
from django.core import serializers
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connections, connection
from django.db.models import Count, Sum, Q, Value
from django.db.models.functions import Coalesce, Substr
from django.contrib.auth.mixins \
    import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import render
from django.views import View
from django.urls import reverse
from django.http import JsonResponse
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import User

from utils.functions.models import rows_to_dict_list_lower, GradeQtd
from utils.views import totalize_grouped_data, group_rowspan
import lotes.models
from geral.functions import request_user, has_permission

import cd.queries as queries
import cd.forms


def index(request):
    return render(request, 'cd/index.html')


def teste_som(request):
    context = {}
    return render(request, 'cd/teste_som.html', context)


class Mapa(View):

    def __init__(self):
        self.template_name = 'cd/mapa.html'
        self.title_name = 'Mapa'

    def mount_context(self):
        enderecos = {}
        letras = [
            {'letra': 'A', 'int_ini': 1},
            {'letra': 'A', 'int_ini': 29},
            {'letra': 'A', 'int_ini': 57},
            {'letra': 'r'},
            {'letra': 'B', 'int_ini': 57},
            {'letra': 'B', 'int_ini': 29},
            {'letra': 'B', 'int_ini': 1},
            {'letra': 'l'},
            {'letra': 'C', 'int_ini': 1},
            {'letra': 'C', 'int_ini': 29},
            {'letra': 'C', 'int_ini': 57},
            {'letra': 'r'},
            {'letra': 'l'},
            {'letra': 'D', 'int_ini': 1},
            {'letra': 'D', 'int_ini': 29},
            {'letra': 'D', 'int_ini': 57},
            {'letra': 'r'},
            {'letra': 'E', 'int_ini': 57},
            {'letra': 'E', 'int_ini': 29},
            {'letra': 'E', 'int_ini': 1},
            {'letra': 'l'},
            {'letra': 'F', 'int_ini': 1},
            {'letra': 'F', 'int_ini': 29},
            {'letra': 'F', 'int_ini': 57},
            {'letra': 'r'},
            {'letra': 'G', 'int_ini': 57},
            {'letra': 'G', 'int_ini': 29},
            {'letra': 'G', 'int_ini': 1},
        ]
        for num, letra in enumerate(letras):
            ends_linha = []
            for int_end in range(28):
                if letra['letra'] == 'r':
                    conteudo = ''
                elif letra['letra'] == 'l':
                    conteudo = '==='
                else:
                    conteudo = '{}{}'.format(
                        letra['letra'], letra['int_ini']+27-int_end)
                ends_linha.append(conteudo)
            enderecos[num] = ends_linha
        context = {
            'linhas': [
                'A3º', 'A2º', 'A1º', 'rua A/B', 'B1º', 'B2º', 'B3º', '===',
                'C3º', 'C2º', 'C1º', 'rua C', '===',
                'D3º', 'D2º', 'D1º', 'rua D/E', 'E1º', 'E2º', 'E3º', '===',
                'F3º', 'F2º', 'F1º', 'rua F/G', 'G1º', 'G2º', 'G3º'
                ],
            'enderecos': enderecos,
            }

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        data = self.mount_context()
        context.update(data)
        return render(request, self.template_name, context)


class VisaoCd(View):

    def __init__(self):
        self.template_name = 'cd/visao_cd.html'
        self.title_name = 'Visão do CD'

    def mount_context(self):
        context = {}
        locais_recs = lotes.models.Lote.objects.all().exclude(
            local__isnull=True
        ).exclude(
            local__exact=''
        ).annotate(
            rua=Substr('local', 1, 1)
        ).values(
            'rua'
        ).annotate(
            qenderecos=Count('local', distinct=True),
            qlotes=Count('lote'),
            qtdsum=Sum('qtd')
        ).order_by('rua')
        if len(locais_recs) == 0:
            return context

        data = list(locais_recs.values(
            'rua', 'qenderecos', 'qlotes', 'qtdsum'))

        headers = ['Rua', 'Endereços', 'Lotes (caixas)', 'Qtd. itens']
        fields = ['rua', 'qenderecos', 'qlotes', 'qtdsum']

        total = data[0].copy()
        total['rua'] = 'Totais:'
        total['|STYLE'] = 'font-weight: bold;'
        quant_fileds = ['qenderecos', 'qlotes', 'qtdsum']
        for field in quant_fileds:
            total[field] = 0
        for row in data:
            for field in quant_fileds:
                total[field] += row[field]
            row['qenderecos|LINK'] = reverse(
                'cd:visao_rua__get', args=[row['rua']])
            row['qlotes|LINK'] = reverse(
                'cd:visao_rua_detalhe__get', args=[row['rua']])
        data.append(total)

        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'style': {2: 'text-align: right;',
                      3: 'text-align: right;',
                      4: 'text-align: right;'},
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        data = self.mount_context()
        context.update(data)
        return render(request, self.template_name, context)


class VisaoRua(View):

    def __init__(self):
        self.template_name = 'cd/visao_rua.html'
        self.title_name = 'Visão geral de rua do CD'

    def mount_context(self, rua):
        context = {'rua': rua}
        locais_recs = lotes.models.Lote.objects.filter(
            local__startswith=rua
        ).exclude(
            local__isnull=True
        ).exclude(
            local__exact=''
        ).values('local').annotate(
            qlotes=Count('lote'),
            qtdsum=Sum('qtd')
        ).order_by('local')
        if len(locais_recs) == 0:
            return context

        data = list(locais_recs.values(
            'local', 'qlotes', 'qtdsum'))

        for row in data:
            row['local|TARGET'] = '_BLANK'
            row['local|LINK'] = reverse(
                'cd:estoque_filtro', args=['E', row['local']])

        headers = ['Endereço', 'Lotes (caixas)', 'Qtd. itens']
        fields = ['local', 'qlotes', 'qtdsum']

        total = data[0].copy()
        total['local'] = 'Total:'
        total['|STYLE'] = 'font-weight: bold;'
        quant_fileds = ['qlotes', 'qtdsum']
        for field in quant_fileds:
            total[field] = 0
        for row in data:
            for field in quant_fileds:
                total[field] += row[field]
        data.append(total)

        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'style': {2: 'text-align: right;',
                      3: 'text-align: right;'},
        })

        return context

    def get(self, request, *args, **kwargs):
        rua = kwargs['rua'].upper()
        context = {'titulo': self.title_name}
        data = self.mount_context(rua)
        context.update(data)
        return render(request, self.template_name, context)


class VisaoRuaDetalhe(View):

    def __init__(self):
        self.template_name = 'cd/visao_rua_detalhe.html'
        self.title_name = 'Visão detalhada de rua do CD'

    def mount_context(self, rua):
        context = {'rua': rua}
        locais_recs = lotes.models.Lote.objects.filter(
            local__startswith=rua
        ).exclude(
            local__isnull=True
        ).exclude(
            local__exact=''
        ).values('local', 'op', 'referencia', 'cor', 'tamanho').annotate(
            qlotes=Count('lote'),
            qtdsum=Sum('qtd')
        ).order_by('local', 'op', 'referencia', 'cor', 'ordem_tamanho')
        if len(locais_recs) == 0:
            return context

        data = list(locais_recs.values(
            'local', 'op', 'referencia', 'cor', 'tamanho', 'qlotes', 'qtdsum'))

        for row in data:
            row['local|TARGET'] = '_BLANK'
            row['local|LINK'] = reverse(
                'cd:estoque_filtro', args=['E', row['local']])

        group = ['local']
        totalize_grouped_data(data, {
            'group': group,
            'sum': ['qlotes', 'qtdsum'],
            'count': [],
            'descr': {'op': 'Totais:'}
        })
        group_rowspan(data, group)

        headers = ['Endereço', 'OP', 'Referência', 'Cor', 'Tamanho',
                   'Lotes (caixas)', 'Qtd. itens']
        fields = ['local', 'op', 'referencia', 'cor', 'tamanho',
                  'qlotes', 'qtdsum']

        context.update({
            'headers': headers,
            'fields': fields,
            'group': group,
            'data': data,
            'style': {6: 'text-align: right;',
                      7: 'text-align: right;'},
        })

        return context

    def get(self, request, *args, **kwargs):
        rua = kwargs['rua'].upper()
        context = {'titulo': self.title_name}
        data = self.mount_context(rua)
        context.update(data)
        return render(request, self.template_name, context)


class InconsistenciasDetalhe(View):

    def __init__(self):
        self.template_name = 'cd/inconsist_detalhe.html'
        self.title_name = 'Detalhe de inconsistência'

    def mount_context(self, cursor, op):
        context = {'op': op}

        lotes_recs = lotes.models.Lote.objects.filter(
            op=op
        ).exclude(
            local__isnull=True
        ).exclude(
            local__exact=''
        ).values('lote').distinct()
        if len(lotes_recs) == 0:
            return context

        ocs = []
        for lote in lotes_recs:
            ocs.append(lote['lote'][4:].lstrip('0'))

        headers = ['Estágio', 'Lote', 'Referência', 'Cor', 'Tamanho',
                   'Quantidade']
        fields = ['est', 'lote', 'ref', 'cor', 'tam', 'qtd']

        data = queries.inconsistencias_detalhe(cursor, op, ocs)

        for row in data:
            if row['seq'] == 99:
                row['est'] = 'Finalizado'
            if row['qtd'] == 0:
                row['qtd'] = '-'
            row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
            row['lote|LINK'] = reverse(
                'producao:posicao__get', args=[row['lote']])
        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
        })

        data63 = queries.inconsistencias_detalhe(cursor, op, ocs, est63=True)

        for row in data63:
            if row['qtd'] == 0:
                row['qtd'] = '-'
            row['lote'] = '{}{:05}'.format(row['periodo'], row['oc'])
            row['lote|LINK'] = reverse(
                'producao:posicao__get', args=[row['lote']])
        context.update({
            'headers63': headers,
            'fields63': fields,
            'data63': data63,
        })

        return context

    def get(self, request, *args, **kwargs):
        op = int(kwargs['op'])

        context = {'titulo': self.title_name}
        cursor = connections['so'].cursor()
        data = self.mount_context(cursor, op)
        context.update(data)
        return render(request, self.template_name, context)


def solicita_lote(request, solicitacao_id, lote, qtd):
    data = {}

    try:
        solicitacao = lotes.models.SolicitaLote.objects.get(
            id=solicitacao_id)
    except lotes.models.SolicitaLote.DoesNotExist:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Solicitação não encontrada por id',
        })
        return JsonResponse(data, safe=False)

    try:
        lote_rec = lotes.models.Lote.objects.get(lote=lote)
    except lotes.models.Lote.DoesNotExist:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Lote não encontrado',
        })
        return JsonResponse(data, safe=False)

    try:
        iqtd = int(qtd)
    except ValueError:
        iqtd = -1
    if iqtd < 1 or iqtd > lote_rec.qtd:
        data.update({
            'result': 'ERR',
            'descricao_erro': 'Quantidade inválida',
        })
        return JsonResponse(data, safe=False)

    try:
        solicita = lotes.models.SolicitaLoteQtd()
        solicita.solicitacao = solicitacao
        solicita.lote = lote_rec
        solicita.qtd = iqtd
        solicita.save()
    except lotes.models.Lote.DoesNotExist:
        data.update({
            'result': 'ERR',
            'descricao_erro':
                'Erro ao criar registro de quantidade solicitada',
        })
        return JsonResponse(data, safe=False)

    data = {
        'result': 'OK',
        'solicitacao_id': solicitacao_id,
        'lote': lote,
        'qtd': iqtd,
        'solicita_qtd_id': solicita.id,
    }
    return JsonResponse(data, safe=False)


class EnderecoLote(View):

    def __init__(self):
        self.Form_class = cd.forms.AskLoteForm
        self.template_name = 'cd/endereco_lote.html'
        self.title_name = 'Verifica endereço de Lote'

    def mount_context(self, request, form):
        lote = form.cleaned_data['lote']

        context = {'lote': lote}

        try:
            lote_rec = lotes.models.Lote.objects.get(lote=lote)
        except lotes.models.Lote.DoesNotExist:
            context.update({'erro': 'Lote não encontrado'})
            return context

        if lote_rec.local is None or lote_rec.local == '':
            local = 'Não endereçado'
            lotes_no_local = -1
        else:
            local = lote_rec.local
            lotes_no_local = len(lotes.models.Lote.objects.filter(
                local=lote_rec.local))

        context.update({
            'op': lote_rec.op,
            'referencia': lote_rec.referencia,
            'cor': lote_rec.cor,
            'tamanho': lote_rec.tamanho,
            'qtd_produzir': lote_rec.qtd_produzir,
            'local': local,
            'q_lotes': lotes_no_local,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'lote' in kwargs and kwargs['lote'] is not None:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'lote' in kwargs and kwargs['lote'] is not None:
            form.data['lote'] = kwargs['lote']
        if form.is_valid():
            data = self.mount_context(request, form)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)


class Grade(View):

    def __init__(self):
        self.Form_class = cd.forms.AskReferenciaForm
        self.template_name = 'cd/grade_estoque.html'
        self.title_name = 'Seleção de grade de estoque'

    def tipo(self, ref):
        if ref[0].isdigit():
            value = ('PA', 1, 'PA/PG')
        elif ref[0] in ('A', 'B'):
            value = ('PG', 2, 'PA/PG')
        elif ref[0] in ('F', 'Z'):
            value = ('MP', 4, 'MP')
        else:
            value = ('MD', 3, 'MD')
        return dict(zip(('tipo', 'ordem', 'grade'), value))

    def mount_context(self, request, ref, exec, limpo, page=1, detalhe=False):
        modelos_pagina = 5
        sel_modelos = []

        if ref == '':
            exec = 'busca'
        else:
            if ref[0] == '_':
                sel_modelos = ref[1:].split('_')
                ref = 'totais'
        todas = ref == 'todas'
        if todas:
            ref = ''
            exec = 'grade'
        totais = ref == 'totais'
        if totais:
            ref = ''
            exec = 'totais'

        refnum = int('0{}'.format(
            ''.join([c for c in ref if c.isdigit()])))
        context = {
            'ref': ref,
            'refnum': refnum,
            'detalhe': detalhe,
            'exec': exec,
        }
        if limpo:
            context['limpo'] = True

        cursor_def = connection.cursor()

        if totais:
            self.template_name = 'cd/grade_estoque_totais.html'

        if len(ref) == 5:  # Referência
            context.update({
                'link_tot': 1,
                'link_num': 1,
                'title_tipo': 1,
                'link_ref': 1,
            })
            referencias = [{
                'referencia': ref,
                'modelo': refnum,
            }]
            row = referencias[0]
            tipo = self.tipo(ref)
            row['tipo'] = tipo['tipo']
            row['ordem_tipo'] = tipo['ordem']
            row['grade_tipo'] = tipo['grade']

            modelos = [refnum]
            exec = 'grade'
        else:  # Todos ou Modelo ou Totais
            data_rec = lotes.models.Lote.objects
            data_rec = data_rec.exclude(
                local__isnull=True
            ).exclude(
                local__exact=''
            ).exclude(
                qtd__lte=0)

            referencias = data_rec.distinct().values(
                'referencia').order_by('referencia')
            for row in referencias:
                row['modelo'] = int(
                    ''.join([c for c in row['referencia'] if c.isdigit()]))

            if len(sel_modelos) > 0:
                refs_copy = referencias[:]
                referencias = [row for row in refs_copy
                               if str(row['modelo']) in sel_modelos]

            if refnum == 0:  # Todos ou Totais ou busca vazio
                for row in referencias:
                    row['referencia|LINK'] = reverse(
                        'cd:grade_estoque', args=[row['referencia']])
                    row['modelo|LINK'] = reverse(
                        'cd:grade_estoque', args=[row['modelo']])
                    tipo = self.tipo(row['referencia'])
                    row['tipo'] = tipo['tipo']
                    row['ordem_tipo'] = tipo['ordem']
                    row['grade_tipo'] = tipo['grade']
                referencias = sorted(
                    referencias, key=lambda k: (
                        k['modelo'], k['ordem_tipo'], k['referencia']))
                if exec == 'busca':
                    context.update({
                        'link_tot': 1,
                    })
                    group = ['modelo']
                    group_rowspan(referencias, group)
                    context.update({
                        'headers': ['Grades por referência numérica', 'Tipo',
                                    'Grade de referência'],
                        'fields': ['modelo', 'tipo', 'referencia'],
                        'group': group,
                        'data': referencias,
                    })
                else:  # exec == 'grade'
                    context.update({
                        'link_tot': 1,
                        'link_num': 1,
                        'link_num_hr': 1,
                        'title_tipo': 1,
                        'title_tipo_hr': 1,
                        'link_ref': 1,
                    })
                    modelos = []
                    for ref in referencias:
                        if ref['modelo'] not in modelos:
                            modelos.append(ref['modelo'])
            else:  # Modelo ou busca
                referencias = [
                    {'referencia': row['referencia'],
                     'modelo': refnum,
                     }
                    for row in referencias
                    if row['modelo'] == refnum]
                for row in referencias:
                    row['referencia|LINK'] = reverse(
                        'cd:grade_estoque', args=[row['referencia']])
                    tipo = self.tipo(row['referencia'])
                    row['tipo'] = tipo['tipo']
                    row['ordem_tipo'] = tipo['ordem']
                    row['grade_tipo'] = tipo['grade']
                referencias = sorted(
                    referencias, key=lambda k: (
                        k['ordem_tipo'], k['referencia']))

                if exec == 'busca':
                    context.update({
                        'link_tot': 1,
                        'link_num': 1,
                        })
                    context.update({
                        'headers': ['Tipo', 'Grade de referência'],
                        'fields': ['tipo', 'referencia'],
                        'data': referencias,
                    })
                else:  # exec == 'grade'
                    context.update({
                        'link_tot': 1,
                        'link_num': 1,
                        'title_tipo': 1,
                        'title_tipo_hr': 1,
                        'link_ref': 1,
                    })
                    modelos = [refnum]

        if exec in ['grade', 'totais']:
            if not totais:
                paginator = Paginator(modelos, modelos_pagina)
                try:
                    modelos = paginator.page(page)
                except PageNotAnInteger:
                    modelos = paginator.page(1)
                except EmptyPage:
                    modelos = paginator.page(paginator.num_pages)
            grades_ref = []
            for modelo in modelos:
                refnum_ant = -1
                tipo_ant = '##'
                mod_referencias = [
                    ref for ref in referencias if ref['modelo'] == modelo]
                if totais:
                    mod_referencias_todos = []
                else:  # todos ou modelo
                    mod_referencias_todos = mod_referencias
                for row in mod_referencias_todos:
                    ref = row['referencia']

                    invent_ref = queries.grade_solicitacao(
                        cursor_def, ref, tipo='i', grade_inventario=True)
                    grade_ref = {
                        'ref': ref,
                        'inventario': invent_ref,
                        }
                    if refnum_ant != row['modelo']:
                        grade_ref.update({'refnum': row['modelo']})
                        refnum_ant = row['modelo']
                        tipo_ant = '##'

                    if tipo_ant != row['grade_tipo']:
                        grade_ref.update({'tipo': row['grade_tipo']})
                        tipo_ant = row['grade_tipo']

                    sum_pedido = queries.sum_pedido(cursor_def, ref)
                    total_pedido = sum_pedido[0]['qtd']
                    if total_pedido is None:
                        total_pedido = 0
                    solped_ref = queries.grade_solicitacao(
                        cursor_def, ref, tipo='sp', grade_inventario=True)
                    if solped_ref['total'] != 0:
                        if total_pedido == 0:
                            link_detalhe = False
                            solped_titulo = 'Solicitações'
                        elif solped_ref['total'] == total_pedido:
                            link_detalhe = False
                            solped_titulo = 'Pedidos'
                        else:
                            link_detalhe = True
                            solped_titulo = 'Solicitações+Pedidos'
                        dispon_ref = queries.grade_solicitacao(
                            cursor_def, ref, tipo='i-sp',
                            grade_inventario=True)
                        grade_ref.update({
                            'solped_titulo': solped_titulo,
                            'link_detalhe': link_detalhe,
                            'solped': solped_ref,
                            'disponivel': dispon_ref,
                            })
                        if detalhe:
                            solic_ref = queries.grade_solicitacao(
                                cursor_def, ref, tipo='s',
                                grade_inventario=True)
                            if solic_ref['total'] != 0:
                                grade_ref.update({
                                    'solicitacoes': solic_ref,
                                    })
                            pedido_ref = queries.grade_solicitacao(
                                cursor_def, ref, tipo='p',
                                grade_inventario=True)
                            if pedido_ref['total'] != 0:
                                grade_ref.update({
                                    'pedido': pedido_ref,
                                    })

                    grades_ref.append(grade_ref)

                refs = []
                if totais:
                    totaliza_mais_que = 0
                else:
                    totaliza_mais_que = 1
                if len(mod_referencias) > totaliza_mais_que:
                    refs = [row['referencia'] for row in mod_referencias
                            if row['grade_tipo'] == 'PA/PG']

                if len(refs) > totaliza_mais_que:
                    dispon_modelo = queries.grade_solicitacao(
                        cursor_def, refs, tipo='i-sp')
                    if dispon_modelo['total'] != 0:

                        if totais:  # se for totais add borda entre as colunas
                            for i in range(1, len(dispon_modelo['fields'])):
                                i_column = i + 1
                                ori_style = ''
                                if i_column in dispon_modelo['style']:
                                    ori_style = dispon_modelo[
                                        'style'][i_column]
                                dispon_modelo['style'][i_column] = \
                                    ori_style + \
                                    'border-left-style: solid;' \
                                    'border-left-width: thin;'

                        grade_ref = {
                            'ref': '',
                            'refnum': row['modelo'],
                            'tipo': 'PA/PG',
                            'titulo': 'Total disponível',
                            'inventario': dispon_modelo,
                        }
                        if totais:
                            grade_ref.update({'titulo': '-'})
                            grade_ref.update({'refnum': modelo})
                        grades_ref.append(grade_ref)

            if totais:
                refs = [row['referencia'] for row in referencias
                        if row['grade_tipo'] == 'PA/PG']
                dispon_sel_modelo = queries.grade_solicitacao(
                    cursor_def, refs, tipo='i-sp')

                for i in range(1, len(dispon_sel_modelo['fields'])):
                    i_column = i + 1
                    ori_style = ''
                    if i_column in dispon_sel_modelo['style']:
                        ori_style = dispon_sel_modelo[
                            'style'][i_column]
                    dispon_sel_modelo['style'][i_column] = \
                        ori_style + \
                        'border-left-style: solid;' \
                        'border-left-width: thin;'
                grade_ref = {
                    'ref': '',
                    'tipo': 'PA/PG',
                    'titulo': '-',
                    'inventario': dispon_sel_modelo,
                }
                grade_ref.update({'refnum': 'TOTAL'})
                grades_ref.append(grade_ref)

            context.update({
                'grades': grades_ref,
                'modelos': modelos,
                'modelos_pagina': modelos_pagina,
                })

        return context

    def get(self, request, *args, **kwargs):
        page = request.GET.get('page', 1)
        limpo = request.GET.get('limpo', 'N') == 'S'
        if 'referencia' in kwargs and kwargs['referencia'] is not None:
            ref = kwargs['referencia']
        else:
            ref = ''
        if 'detalhe' in kwargs and kwargs['detalhe'] is not None:
            detalhe = kwargs['detalhe'] == 'detalhe'
        else:
            detalhe = False
        context = {'titulo': self.title_name}
        data = self.mount_context(request, ref, 'grade', limpo, page, detalhe)
        context.update(data)
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            ref = form.cleaned_data['ref']
            data = self.mount_context(request, ref, 'busca', False)
            context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)


class Historico(View):

    def __init__(self):
        self.Form_class = cd.forms.HistoricoForm
        self.template_name = 'cd/historico.html'
        self.title_name = 'Histórico de OP'

    def mount_context(self, cursor, op):
        context = {
            'op': op,
            }

        data = queries.historico(cursor, op)
        if len(data) == 0:
            context.update({'erro': 'Sem lotes ativos'})
            return context
        for row in data:
            if row['dt'] is None:
                row['dt'] = 'Nunca inventariado'
            if row['endereco'] is None:
                if row['usuario'] is None:
                    row['endereco'] = '-'
                else:
                    row['endereco'] = 'SAIU!'
            if row['usuario'] is None:
                row['usuario'] = '-'
        context.update({
            'headers': ('Data', 'Qtd. de lotes', 'Endereço', 'Usuário'),
            'fields': ('dt', 'qtd', 'endereco', 'usuario'),
            'data': data,
        })

        data = queries.historico_detalhe(cursor, op)
        for row in data:
            if row['dt'] is None:
                row['dt'] = 'Nunca inventariado'
            if row['endereco'] is None:
                if row['usuario'] is None:
                    row['endereco'] = '-'
                else:
                    row['endereco'] = 'SAIU!'
            if row['usuario'] is None:
                row['usuario'] = '-'
            row['lote|LINK'] = reverse(
                'cd:historico_lote', args=[row['lote']])
        context.update({
            'd_headers': ('Lote', 'Última data', 'Endereço', 'Usuário'),
            'd_fields': ('lote', 'dt', 'endereco', 'usuario'),
            'd_data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'op' in kwargs and kwargs['op'] is not None:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'op' in kwargs and kwargs['op'] is not None:
            form.data['op'] = kwargs['op']
        if form.is_valid():
            op = form.cleaned_data['op']
            cursor = connection.cursor()
            context.update(self.mount_context(cursor, op))
        context['form'] = form
        return render(request, self.template_name, context)


class HistoricoLote(View):

    def __init__(self):
        self.Form_class = cd.forms.ALoteForm
        self.template_name = 'cd/historico_lote.html'
        self.title_name = 'Histórico de lote'

    def mount_context(self, cursor, lote):
        context = {
            'lote': lote,
            }

        data = queries.historico_lote(cursor, lote)
        if len(data) == 0:
            context.update({'erro': 'Lote não encontrado ou nunca endereçado'})
            return context

        lote_cd = lotes.models.Lote.objects.get(lote=lote)
        op = str(lote_cd.op)
        context.update({
            'op': op,
        })

        old_estagio = None
        old_usuario = None
        old_local = None
        for row in data:
            n_info = 0
            log = row['log']
            log = log.replace("<UTC>", "utc")
            log = re.sub(
                r'^(.*)<SimpleLazyObject: <User: ([^\s]*)>>(.*)$',
                r'\1"\2"\3', log)
            log = re.sub(
                r'^(.*)<User: ([^\s]*)>(.*)$',
                r'\1"\2"\3', log)
            dict_log = eval(log)

            if 'estagio' in dict_log:
                row['estagio'] = dict_log['estagio']
                old_estagio = row['estagio']
                n_info += 1
            else:
                if old_estagio is None:
                    row['estagio'] = '-'
                else:
                    row['estagio'] = '='
            if row['estagio'] == 999:
                row['estagio'] = 'Finalizado'

            if 'local' in dict_log:
                row['local'] = dict_log['local']
                old_local = row['local']
                n_info += 1
            else:
                if old_local is None:
                    row['local'] = '-'
                else:
                    row['local'] = '='
            if row['local'] is None:
                row['local'] = 'SAIU!'

            if 'local_usuario' in dict_log:
                row['local_usuario'] = dict_log['local_usuario']
                old_usuario = row['local_usuario']
                n_info += 1
            else:
                if old_usuario is None or row['local'] in ('-', '='):
                    row['local_usuario'] = '-'
                else:
                    row['local_usuario'] = '='

            row['n_info'] = n_info

        context.update({
            'headers': ('Data', 'Estágio', 'Local', 'Usuário'),
            'fields': ('time', 'estagio', 'local', 'local_usuario'),
            'data': [row for row in data if row['n_info'] != 0],
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'lote' in kwargs and kwargs['lote'] is not None:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'lote' in kwargs and kwargs['lote'] is not None:
            form.data['lote'] = kwargs['lote']
        if form.is_valid():
            lote = form.cleaned_data['lote']
            cursor = connection.cursor()
            context.update(self.mount_context(cursor, lote))
        context['form'] = form
        return render(request, self.template_name, context)
