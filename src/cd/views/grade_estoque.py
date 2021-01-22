from pprint import pprint

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
from django.shortcuts import render
from django.views import View
from django.urls import reverse

from utils.views import group_rowspan
import lotes.models

import cd.queries as queries
import cd.forms


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

        refnum_digitos = "".join([c for c in ref if c in "0123456789"])
        refnum = int(f'0{refnum_digitos}')
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
            tipo = self.tipo(ref)
            referencias = [{
                'referencia': ref,
                'modelo': refnum,
                'tipo': tipo['tipo'],
                'ordem_tipo': tipo['ordem'],
                'grade_tipo': tipo['grade'],
            }]
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
