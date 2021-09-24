from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import totalize_grouped_data, group_rowspan

from insumo.queries import insumos_de_produtos_em_dual

import lotes.forms as forms
import lotes.queries.lote
import lotes.queries.op
import lotes.queries.os


class ComponentesDeOp(View):
    Form_class = forms.OpForm
    template_name = 'lotes/componentes_de_op.html'
    title_name = 'Grades de produtos componentes de OP'

    def mount_context(self, cursor, op):
        context = {'op': op}

        # Lotes ordenados por OS + referência + estágio
        ref_data = lotes.queries.op.op_inform(cursor, op)
        if len(ref_data) == 0:
            context.update({
                'msg_erro': 'OP não encontrada',
            })
            return context

        ref2_data = [ref_data[0]]

        # referência
        ref_row = ref_data[0]
        ref_row['REF|LINK'] = reverse(
            'produto:ref__get', args=[ref_row['REF']])
        ref_row['MODELO|LINK'] = reverse(
            'produto:modelo__get', args=[ref_row['MODELO']])
        context.update({
            'ref_headers': ('Modelo', 'Tipo de referência', 'Referência',
                            'Alternativa', 'Roteiro',
                            'Descrição'),
            'ref_fields': ('MODELO', 'TIPO_REF', 'REF',
                           'ALTERNATIVA', 'ROTEIRO',
                           'DESCR_REF'),
            'ref_data': ref_data,
        })

        for row in ref2_data:
            row['DT_CORTE'] = row['DT_CORTE'].date()
        context.update({
            'ref2_headers': ('Observação', 'Observação 2', 'Data Corte'),
            'ref2_fields': ('OBSERVACAO', 'OBSERVACAO2', 'DT_CORTE'),
            'ref2_data': ref2_data,
        })

        # tam, cor e quantidade de produto de OP
        data = lotes.queries.op.op_tam_cor_qtd(cursor, op)
        for row in data:
            row['NIVEL'] = '1'
            row['REF'] = ref_row['REF']
            row['ALT'] = ref_row['ALTERNATIVA']

        op_comp = None
        componentes = []
        componentes_nivel = 0
        while True:
            if len(data) == 0:
                break

            if componentes_nivel == 0:
                header_text = 'Produtos da OP'
                comp_headers = ['Nivel', 'Ref.', 'Tamanho', 'Cor', 'Alt.', 'Qtd.']
                comp_fields = ['NIVEL', 'REF', 'TAM', 'COR', 'ALT', 'QTD']
            else:
                header_text = f'Produtos componentes {componentes_nivel}ª descendência'
                header_text += f' (OP {op_comp})'
                comp_headers = ['Nivel', 'Ref.', 'Tamanho', 'Cor', 'Descr. Cor', 'Alt.', 'Qtd. Calculada']
                comp_fields = ['NIVEL', 'REF', 'TAM', 'COR', 'COR_DESCR', 'ALT', 'QTD']

            group = ['NIVEL', 'REF']
            totalize_grouped_data(data, {
                'group': group,
                'sum': ['QTD'],
                'count': [],
                'descr': {'ALT': 'Total:'}
            })
            group_rowspan(data, group)

            table = {
                'header_text': header_text,
                'headers': comp_headers,
                'fields': comp_fields,
                'group': group,
                'data': data,
            }
            componentes.append(table)

            dual_nivel = None
            dual_nivel_list = []
            for row in data:
                if row['NIVEL'] == '1' and row['ALT'] != 'Total:':
                    dual_nivel_list.append('''
                        SELECT
                        '{nivel}' NIVEL
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
                    ))
            dual_nivel = ' UNION '.join(dual_nivel_list)
            data = []

            if dual_nivel is not None:
                op_comp = None
                insumos = insumos_de_produtos_em_dual(
                    cursor, dual_nivel, order='tc')
                # data = [f_row for f_row in data if (f_row['NIVEL'] == '1')]
                for row in insumos:

                    if op_comp is None:
                        r_data = lotes.queries.op.op_relacionamentos(cursor, op, row['REF'])
                        if len(r_data) != 0:
                            op_comp = r_data[0]['OP_REL']
                        else:
                            op_comp = 'não existe'

                    if row['NIVEL'] == '1':
                        busca_insumo = [
                            item for item in data
                            if item['NIVEL'] == row['NIVEL']
                            and item['REF'] == row['REF']
                            and item['COR'] == row['COR']
                            and item['TAM'] == row['TAM']
                            and item['ALT'] == row['ALT']
                        ]
                        if busca_insumo == []:
                            data.append(row)
                        else:
                            busca_insumo[0]['QTD'] += row['QTD']

            componentes_nivel += 1

        context.update({
            'componentes': componentes,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'op' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        form.data = form.data.copy()
        if 'op' in kwargs:
            form.data['op'] = kwargs['op']
        if form.is_valid():
            op = form.cleaned_data['op']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, op))
        context['form'] = form
        return render(request, self.template_name, context)


class OpConserto(View):
    template_name = 'lotes/conserto.html'
    title_name = 'Produtos em conserto'

    def mount_context(self, cursor):
        context = {}

        # Peças no conserto
        data = lotes.queries.op.op_conserto(cursor)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma peça em conserto',
            })
            return context

        for row in data:
            row['OP|LINK'] = '/lotes/op/{}'.format(row['OP'])
            row['REF|LINK'] = reverse('produto:ref__get', args=[row['REF']])

        context.update({
            'headers': ('Referência', 'Cor', 'Tamanho', 'OP', 'Quantidade'),
            'fields': ('REF', 'COR', 'TAM', 'OP', 'QTD'),
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        cursor = db_cursor_so(request)
        context.update(self.mount_context(cursor))
        return render(request, self.template_name, context)


class OpPerda(View):
    Form_class = forms.OpPerdaForm
    template_name = 'lotes/perda.html'
    title_name = 'Perdas de produção'

    def mount_context(self, cursor, data_de, data_ate, detalhe):
        context = {
            'data_de': data_de,
            'data_ate': data_ate,
            'detalhe': detalhe,
        }
        # Peças em perda
        data = lotes.queries.op.op_perda(cursor, data_de, data_ate, detalhe)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma perda de produção encontrada',
            })
            return context

        for row in data:
            row['OP|LINK'] = '/lotes/op/{}'.format(row['OP'])
            row['REF|LINK'] = reverse('produto:ref__get', args=[row['REF']])
            row['PERC'] = row['QTD'] / row['QTDOP'] * 100
            row['PERC|DECIMALS'] = 2

        group = ['REF']
        totalize_grouped_data(data, {
            'group': group,
            'sum': ['QTD'],
            'count': [],
            'descr': {'OP': 'Total:'},
            'flags': ['NO_TOT_1'],
            'global_sum': ['QTD'],
            'global_descr': {'OP': 'Total geral:'},
        })
        group_rowspan(data, group)

        if detalhe == 'c':
            headers = ('Referência', 'Cor', 'Tamanho', 'OP', 'Quantidade', '%')
            fields = ('REF', 'COR', 'TAM', 'OP', 'QTD', 'PERC')
            style = {
                5: 'text-align: right;',
                6: 'text-align: right;',
            }
        else:
            headers = ('Referência', 'OP', 'Quantidade', '%')
            fields = ('REF', 'OP', 'QTD', 'PERC')
            style = {
                3: 'text-align: right;',
                4: 'text-align: right;',
            }
        context.update({
            'headers': headers,
            'fields': fields,
            'data': data,
            'group': group,
            'style': style,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            data_de = form.cleaned_data['data_de']
            data_ate = form.cleaned_data['data_ate']
            detalhe = form.cleaned_data['detalhe']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(
                cursor, data_de, data_ate, detalhe))
        context['form'] = form
        return render(request, self.template_name, context)


class ListaLotes(View):

    def __init__(self):
        self.Form_class = forms.OpForm
        self.template_name = 'lotes/lista_lotes.html'
        self.title_name = 'Lista lotes de OP'

    def mount_context(self, cursor, op):
        context = {'op': op}

        data = lotes.queries.lote.get_lotes(cursor, op=op, order='o')
        if len(data) == 0:
            context.update({
                'msg_erro': 'Sem lotes',
            })
            return context
        # colunas OP, Referência, Cor, Tamanho, Período, OC, Quant.)
        i = 1
        for row in data:
            row['N'] = '{}/{}'.format(i, len(data))
            i += 1
            row['OP|LINK'] = '/lotes/op/{}'.format(row['OP'])
            row['REF|LINK'] = reverse('produto:ref__get', args=[row['REF']])
        context.update({
            'headers': ('OP', 'Rerefência', 'Tamanho', 'Cor', 'Período', 'OC',
                        'Quantidade', '#'),
            'fields': ('OP', 'REF', 'TAM', 'COR', 'PERIODO', 'OC',
                       'QTD', 'N'),
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            op = form.cleaned_data['op']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, op))
        context['form'] = form
        return render(request, self.template_name, context)
