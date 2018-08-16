import copy
from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.urls import reverse
from django.views import View

from fo2.template import group_rowspan

from utils.views import totalize_grouped_data
from insumo.models import insumos_de_produtos_em_dual

import lotes.forms as forms
import lotes.models as models


class Op(View):
    Form_class = forms.OpForm
    template_name = 'lotes/op.html'
    title_name = 'OP'

    def mount_context(self, cursor, op):
        context = {'op': op}

        # Lotes ordenados por OS + referência + estágio
        data = models.op_lotes(cursor, op)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Lotes não encontrados',
            })
        else:
            link = ('LOTE')
            for row in data:
                row['LOTE'] = '{}{:05}'.format(row['PERIODO'], row['OC'])
                row['LINK'] = '/lotes/posicao/{}'.format(row['LOTE'])
            context.update({
                'headers': ('Estágio', 'OS', 'Referência', 'Cor', 'Tamanho',
                            'Período', 'OC', 'Quant.', 'Lote'),
                'fields': ('EST', 'OS', 'REF', 'COR', 'TAM',
                           'PERIODO', 'OC', 'QTD', 'LOTE'),
                'data': data,
                'link': link,
            })

            # informações gerais
            i_data = models.op_inform(cursor, op)
            i2_data = [i_data[0]]
            i3_data = [i_data[0]]
            i4_data = [i_data[0]]

            for row in i_data:
                if row['PEDIDO'] == 0:
                    row['PEDIDO'] = ''
                else:
                    row['PEDIDO|LINK'] = '/lotes/pedido/{}'.format(
                        row['PEDIDO'])
            context.update({
                'i_headers': ('Situação', 'Cancelamento', 'Unidade', 'Pedido',
                              'Pedido do cliente', 'Relacionamento com OPs'),
                'i_fields': ('SITUACAO', 'CANCELAMENTO', 'UNIDADE', 'PEDIDO',
                             'PED_CLIENTE', 'TIPO_OP'),
                'i_data': i_data,
            })

            row = i2_data[0]
            row['REF|LINK'] = reverse('produto:ref__get', args=[row['REF']])
            row['MODELO|LINK'] = reverse(
                'produto:modelo__get', args=[row['MODELO']])
            qtd_lotes_fim = row['LOTES']
            context.update({
                'i2_headers': ('Modelo', 'Tipo de referência', 'Referência',
                               'Alternativa', 'Roteiro',
                               'Descrição', 'Modelagem',
                               'Qtd. Lotes', 'Quant. Itens'),
                'i2_fields': ('MODELO', 'TIPO_REF', 'REF',
                              'ALTERNATIVA', 'ROTEIRO',
                              'DESCR_REF', 'MOLDE',
                              'LOTES', 'QTD'),
                'i2_data': i2_data,
            })

            row = i3_data[0]
            row['DT_DIGITACAO'] = row['DT_DIGITACAO'].date()
            if row['DT_CORTE'] is None:
                row['DT_CORTE'] = ''
            else:
                row['DT_CORTE'] = row['DT_CORTE'].date()
            row['PERIODO_INI'] = row['PERIODO_INI'].date()
            row['PERIODO_FIM'] = row['PERIODO_FIM'].date()
            context.update({
                'i3_headers': ('Depósito', 'Período', 'Período Início',
                               'Período Fim', 'Data Digitação', 'Data Corte'),
                'i3_fields': ('DEPOSITO', 'PERIODO', 'PERIODO_INI',
                              'PERIODO_FIM', 'DT_DIGITACAO', 'DT_CORTE'),
                'i3_data': i3_data,
            })

            row = i4_data[0]
            if row['OBSERVACAO'] or row['OBSERVACAO2']:
                if row['OBSERVACAO'] is None:
                    row['OBSERVACAO'] = ''
                if row['OBSERVACAO2'] is None:
                    row['OBSERVACAO2'] = ''
                context.update({
                    'i4_headers': ('Observação', 'Observação 2'),
                    'i4_fields': ('OBSERVACAO', 'OBSERVACAO2'),
                    'i4_data': i4_data,
                })

            # relacionamentos entre OPs
            r_data = models.op_relacionamentos(cursor, op)
            for row in r_data:
                row['OP_REL|LINK'] = '/lotes/op/{}'.format(row['OP_REL'])
            if len(r_data) != 0:
                context.update({
                    'r_headers': ('OP', 'Tipo de relacionamento',
                                  'OP relacionada'),
                    'r_fields': ('OP', 'REL', 'OP_REL'),
                    'r_data': r_data,
                })

            # Grade
            g_header, g_fields, g_data = models.op_sortimento(cursor, op)
            if len(g_data) != 0:
                context.update({
                    'g_headers': g_header,
                    'g_fields': g_fields,
                    'g_data': g_data,
                })

            # Grade de perda
            gp_header, gp_fields, gp_data, total = models.op_sortimentos(
                cursor, op, 'p')
            if total != 0:
                context.update({
                    'gp_headers': gp_header,
                    'gp_fields': gp_fields,
                    'gp_data': gp_data,
                })

            # Grade de segunda qualidade
            gs_header, gs_fields, gs_data, total = models.op_sortimentos(
                cursor, op, 's')
            if total != 0:
                context.update({
                    'gs_headers': gs_header,
                    'gs_fields': gs_fields,
                    'gs_data': gs_data,
                })

            # Grade de conserto
            gc_header, gc_fields, gc_data, total = models.op_sortimentos(
                cursor, op, 'c')
            if total != 0:
                context.update({
                    'gc_headers': gc_header,
                    'gc_fields': gc_fields,
                    'gc_data': gc_data,
                })

            # Estágios
            e_data = models.op_estagios(cursor, op)
            for row in e_data:
                qtd_lotes_fim -= row['LOTES']
            context.update({
                'e_headers': ('Estágio', '% Produzido',
                              'Itens 1ª Qualidade', 'Itens 2ª Qualidade',
                              'Itens Perda', 'Itens Conserto',
                              'Lotes no estágio'),
                'e_fields': ('EST', 'PERC',
                             'PROD', 'Q2',
                             'PERDA', 'CONSERTO', 'LOTES'),
                'e_data': e_data,
                'qtd_lotes_fim': qtd_lotes_fim,
            })

            # Totais por referência + estágio
            t_data = models.op_ref_estagio(cursor, op)
            context.update({
                't_headers': ('Referência', 'Tamanho', 'Cor', 'Estágio',
                              'Qtd. Lotes', 'Quant. Itens'),
                't_fields': ('REF', 'TAM', 'COR', 'EST', 'LOTES', 'QTD'),
                't_data': t_data,
            })

            # OSs da OP
            os_data = models.op_get_os(cursor, op)
            if len(os_data) != 0:
                os_link = ('OS')
                for row in os_data:
                    row['LINK'] = '/lotes/os/{}'.format(row['OS'])
                    cnpj = '{:08d}/{:04d}-{:02d}'.format(
                        row['CNPJ9'],
                        row['CNPJ4'],
                        row['CNPJ2'])
                    row['TERC'] = '{} - {}'.format(cnpj, row['NOME'])
                context.update({
                    'os_headers': ('OS', 'Serviço', 'Terceiro',
                                   'Emissão', 'Entrega',
                                   'Situação', 'Cancelamento',
                                   'Lotes', 'Quant.'),
                    'os_fields': ('OS', 'SERV', 'TERC',
                                  'DATA_EMISSAO', 'DATA_ENTREGA',
                                  'SITUACAO', 'CANC',
                                  'LOTES', 'QTD'),
                    'os_data': os_data,
                    'os_link': os_link,
                })

            # Totais por OS + referência
            o_data = models.op_os_ref(cursor, op)
            o_link = ('OS')
            for row in o_data:
                if row['OS']:
                    row['LINK'] = '/lotes/os/{}'.format(row['OS'])
                else:
                    row['LINK'] = None
            context.update({
                'o_headers': ('OS', 'Referência', 'Tamanho', 'Cor',
                              'Qtd. Lotes', 'Quant. Itens'),
                'o_fields': ('OS', 'REF', 'TAM', 'COR', 'LOTES', 'QTD'),
                'o_data': o_data,
                'o_link': o_link,
            })

            # Detalhamento de movimentações de estágios
            u_data = models.op_movi_estagios(cursor, op)
            for row in u_data:
                if row['DT_MIN'] == row['DT_MAX']:
                    row['DT_MAX'] = '='
                else:
                    row['DT_MAX'] = row['DT_MAX'].date()
                row['DT_MIN'] = row['DT_MIN'].date()
            context.update({
                'u_headers': ('Estagio', 'De', 'Até',
                              'Usuário', 'Lotes'),
                'u_fields': ('EST', 'DT_MIN', 'DT_MAX',
                             'USUARIO_SYSTEXTIL', 'LOTES'),
                'u_data': u_data,
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
        if 'op' in kwargs:
            form.data['op'] = kwargs['op']
        if form.is_valid():
            op = form.cleaned_data['op']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, op))
        context['form'] = form
        return render(request, self.template_name, context)


class BuscaOP(View):
    Form_class = forms.BuscaOpForm
    template_name = 'lotes/busca_op.html'
    title_name = 'Busca OP'

    def mount_context(self, cursor, ref):
        context = {'ref': ref}

        data = models.busca_op(cursor, ref=ref)
        if len(data) == 0:
            context.update({
                'msg_erro': 'OPs não encontradas',
            })
            return context

        for row in data:
            row['OP|LINK'] = '/lotes/op/{}'.format(row['OP'])
            row['DT_DIGITACAO'] = row['DT_DIGITACAO'].date()
            if row['DT_CORTE'] is None:
                row['DT_CORTE'] = ''
            else:
                row['DT_CORTE'] = row['DT_CORTE'].date()
        context.update({
            'headers': ('OP', 'Situação', 'Cancelamento',
                        'Tipo', 'Referência',
                        'Alt.', 'Roteiro',
                        'Q. Lotes', 'Q. Itens',
                        'Depósito', 'Período',
                        'Data Digitação', 'Data Corte',),
            'fields': ('OP', 'SITUACAO', 'CANCELAMENTO',
                       'TIPO_REF', 'REF',
                       'ALTERNATIVA', 'ROTEIRO',
                       'LOTES', 'QTD',
                       'DEPOSITO_CODIGO', 'PERIODO',
                       'DT_DIGITACAO', 'DT_CORTE'),
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        if 'ref' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            context = {'titulo': self.title_name}
            form = self.Form_class()
            context['form'] = form
            return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if 'ref' in kwargs:
            form.data['ref'] = kwargs['ref']
        if form.is_valid():
            ref = form.cleaned_data['ref']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, ref))
        context['form'] = form
        return render(request, self.template_name, context)


class ComponentesDeOp(View):
    Form_class = forms.OpForm
    template_name = 'lotes/componentes_de_op.html'
    title_name = 'Grades de produtos componentes de OP'

    def mount_context(self, cursor, op):
        context = {'op': op}

        # Lotes ordenados por OS + referência + estágio
        ref_data = models.op_inform(cursor, op)
        if len(ref_data) == 0:
            context.update({
                'msg_erro': 'OP não encontrada',
            })
            return context

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

        # tam, cor e quantidade de produto de OP
        data = models.op_tam_cor_qtd(cursor, op)
        for row in data:
            row['NIVEL'] = '1'
            row['REF'] = ref_row['REF']
            row['ALT'] = ref_row['ALTERNATIVA']

        comp_headers = ['Nivel', 'Ref.', 'Tamanho', 'Cor', 'Alt.', 'Qtd.']
        comp_fields = ['NIVEL', 'REF', 'TAM', 'COR', 'ALT', 'QTD']

        componentes = []
        componentes_nivel = 0
        while True:
            if len(data) == 0:
                break

            if componentes_nivel == 0:
                header_text = 'Produtos da OP'
            else:
                header_text = 'Produtos componentes {}ª descendência'.format(
                    componentes_nivel)

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

            dual_nivel1 = None
            for row in data:
                if row['NIVEL'] == '1' and row['ALT'] != 'Total:':
                    dual_select = '''
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
                    )
                    if dual_nivel1 is None:
                        dual_nivel1 = dual_select
                    else:
                        dual_nivel1 = ' UNION '.join(
                            (dual_nivel1, dual_select))
            data = []
            if dual_nivel1 is not None:
                insumos = insumos_de_produtos_em_dual(
                    cursor, dual_nivel1, order='tc')
                # data = [f_row for f_row in data if (f_row['NIVEL'] == '1')]
                for row in insumos:
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
        if 'op' in kwargs:
            form.data['op'] = kwargs['op']
        if form.is_valid():
            op = form.cleaned_data['op']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, op))
        context['form'] = form
        return render(request, self.template_name, context)


class Conserto(View):
    template_name = 'lotes/conserto.html'
    title_name = 'Produtos em conserto'

    def mount_context(self, cursor):
        context = {}

        # Peças no conserto
        data = models.conserto(cursor)
        if len(data) == 0:
            context.update({
                'msg_erro': 'Nenhuma peça em conserto',
            })
            return context

        context.update({
            'headers': ('Referência', 'Cor', 'Tamanho', 'Quantidade'),
            'fields': ('REF', 'COR', 'TAM', 'QTD'),
            'data': data,
        })

        return context

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        cursor = connections['so'].cursor()
        context.update(self.mount_context(cursor))
        return render(request, self.template_name, context)
