import copy
import time
from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.template import group_rowspan

from utils.views import totalize_grouped_data
from utils.classes import Perf
from insumo.queries import insumos_de_produtos_em_dual
from geral.functions import config_get_value

import lotes.forms as forms
import lotes.models as models
import lotes.functions as functions


class Op(View):
    Form_class = forms.OpForm
    template_name = 'lotes/op.html'
    title_name = 'OP'

    def mount_context(self, cursor, op, request):
        p = Perf(False)

        context = {'op': op}

        # informações gerais
        i_data = models.op_inform(cursor, op)
        p.prt('op_inform')

        if len(i_data) == 0:
            context.update({
                'msg_erro': 'OP não encontrada',
            })
        else:

            # Lotes ordenados por OS + referência + estágio
            data = models.op_lotes(cursor, op)
            p.prt('op_lotes')

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

            i2_data = [i_data[0]]
            i3_data = [i_data[0]]
            i4_data = [i_data[0]]

            for row in i_data:
                if row['PEDIDO'] == 0:
                    row['PEDIDO'] = ''
                else:
                    row['PEDIDO|LINK'] = '/lotes/pedido/{}'.format(
                        row['PEDIDO'])
            val_parm = config_get_value('OP-UNIDADE', request.user)
            if val_parm is None:
                val_parm = 'S'
            else:
                context.update({
                    'op_unidade': val_parm,
                })

            if val_parm == 'S':
                i_headers = (
                    'Situação', 'Cancelamento', 'Unidade', 'Pedido',
                    'Pedido do cliente', 'Relacionamento com OPs')
                i_fields = (
                    'SITUACAO', 'CANCELAMENTO', 'UNIDADE', 'PEDIDO',
                    'PED_CLIENTE', 'TIPO_OP')
            else:
                i_headers = (
                    'Situação', 'Cancelamento', 'Pedido',
                    'Pedido do cliente', 'Relacionamento com OPs')
                i_fields = (
                    'SITUACAO', 'CANCELAMENTO', 'PEDIDO',
                    'PED_CLIENTE', 'TIPO_OP')
            context.update({
                'i_headers': i_headers,
                'i_fields': i_fields,
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

            # posição de OP
            p_data = models.posicao_op(cursor, op)
            p.prt('posicao_op')
            if len(p_data) != 0:
                context.update({
                    'p_headers': ('Posição', 'Quantidade', 'Estágio'),
                    'p_fields': ('TIPO', 'QTD', 'ESTAGIO'),
                    'p_style': {2: 'font-weight: bold; text-align: right;'},
                    'p_data': p_data,
                })

            # relacionamentos entre OPs
            r_data = models.op_relacionamentos(cursor, op)
            p.prt('op_relacionamentos')

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
            p.prt('op_sortimento 1ª')

            if len(g_data) != 0:
                context.update({
                    'g_headers': g_header,
                    'g_fields': g_fields,
                    'g_data': g_data,
                })

            # Grade de perda
            gp_header, gp_fields, gp_data, total = models.op_sortimentos(
                cursor, op, 'p')
            p.prt('op_sortimentos perda')

            if total != 0:
                context.update({
                    'gp_headers': gp_header,
                    'gp_fields': gp_fields,
                    'gp_data': gp_data,
                })

            # Grade de segunda qualidade
            gs_header, gs_fields, gs_data, total = models.op_sortimentos(
                cursor, op, 's')
            p.prt('op_sortimentos 2ª')

            if total != 0:
                context.update({
                    'gs_headers': gs_header,
                    'gs_fields': gs_fields,
                    'gs_data': gs_data,
                })

            # Grade de conserto
            gc_header, gc_fields, gc_data, total = models.op_sortimentos(
                cursor, op, 'c')
            p.prt('op_sortimentos conserto')

            if total != 0:
                context.update({
                    'gc_headers': gc_header,
                    'gc_fields': gc_fields,
                    'gc_data': gc_data,
                })

            # Estágios
            e_data = models.op_estagios(cursor, op)
            p.prt('op_estagios')

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
            p.prt('op_ref_estagio')

            context.update({
                't_headers': ('Referência', 'Tamanho', 'Cor', 'Estágio',
                              'Qtd. Lotes', 'Quant. Itens'),
                't_fields': ('REF', 'TAM', 'COR', 'EST', 'LOTES', 'QTD'),
                't_data': t_data,
            })

            # OSs da OP
            os_data = models.op_get_os(cursor, op)
            p.prt('op_get_os')

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
            p.prt('op_os_ref')

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
            p.prt('op_movi_estagios')

            for row in u_data:
                if row['DT_MIN'] == row['DT_MAX']:
                    row['DT_MAX'] = '='
                else:
                    row['DT_MAX'] = row['DT_MAX'].date()
                row['DT_MIN'] = row['DT_MIN'].date()
            context.update({
                'u_headers': ('Estagio', 'Movimento', 'De', 'Até',
                              'Usuário', 'Lotes'),
                'u_fields': ('EST', 'MOV', 'DT_MIN', 'DT_MAX',
                             'USU', 'LOTES'),
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
            context.update(self.mount_context(cursor, op, request))
        context['form'] = form
        return render(request, self.template_name, context)


class BuscaOP(View):
    Form_class = forms.BuscaOpForm
    template_name = 'lotes/busca_op.html'
    title_name = 'Busca OP'

    def mount_context(
            self, cursor, ref, tam, cor, deposito, tipo, situacao, posicao):
        context = {
            'ref': ref,
            'tam': tam,
            'cor': cor,
            'deposito': deposito,
            'tipo': tipo,
            'situacao': situacao,
            'posicao': posicao,
        }

        data = models.busca_op(
            cursor, ref=ref, tam=tam, cor=cor, deposito=deposito, tipo=tipo,
            situacao=situacao, posicao=posicao)
        if len(data) == 0:
            context.update({
                'msg_erro': 'OPs não encontradas',
            })
            return context

        for row in data:
            row['OP|LINK'] = '/lotes/op/{}'.format(row['OP'])
            row['OP_REL|LINK'] = '/lotes/op/{}'.format(row['OP_REL'])
            row['REF|LINK'] = reverse('produto:ref__get', args=[row['REF']])
            row['DT_DIGITACAO'] = row['DT_DIGITACAO'].date()
            if row['DT_CORTE'] is None:
                row['DT_CORTE'] = ''
            else:
                row['DT_CORTE'] = row['DT_CORTE'].date()
            if row['ESTAGIO'] is None:
                row['ESTAGIO'] = 'Finalizado*'
        context.update({
            'headers': ('OP', 'Situação', 'Cancelamento',
                        'Tipo', 'Referência',
                        'Alt.', 'Roteiro', 'Estágio',
                        'Q. Lotes', 'Q. Itens',
                        'Depósito', 'Período',
                        'Data Digitação', 'Data Corte', 'OP relacionada'),
            'fields': ('OP', 'SITUACAO', 'CANCELAMENTO',
                       'TIPO_REF', 'REF',
                       'ALTERNATIVA', 'ROTEIRO', 'ESTAGIO',
                       'LOTES', 'QTD',
                       'DEPOSITO_CODIGO', 'PERIODO',
                       'DT_DIGITACAO', 'DT_CORTE', 'OP_REL'),
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
            tam = form.cleaned_data['tam']
            cor = form.cleaned_data['cor']
            deposito = form.cleaned_data['deposito']
            tipo = form.cleaned_data['tipo']
            situacao = form.cleaned_data['situacao']
            posicao = form.cleaned_data['posicao']
            cursor = connections['so'].cursor()
            context.update(
                self.mount_context(
                    cursor, ref, tam, cor, deposito, tipo, situacao, posicao))
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
                insumos = insumos_de_produtos_em_dual(
                    cursor, dual_nivel, order='tc')
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


class OpConserto(View):
    template_name = 'lotes/conserto.html'
    title_name = 'Produtos em conserto'

    def mount_context(self, cursor):
        context = {}

        # Peças no conserto
        data = models.op_conserto(cursor)
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
        cursor = connections['so'].cursor()
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
        data = models.op_perda(cursor, data_de, data_ate, detalhe)
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
            cursor = connections['so'].cursor()
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

        data = models.base.get_lotes(cursor, op=op, order='o')
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
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, op))
        context['form'] = form
        return render(request, self.template_name, context)


class CorrigeSequenciamento(PermissionRequiredMixin, View):

    def __init__(self):
        self.permission_required = 'lotes.can_repair_seq_op'
        self.Form_class = forms.OpForm
        self.template_name = 'lotes/corrige_sequenciamento.html'
        self.title_name = 'Corrige sequenciamento de lotes de OP'

    def mount_context(self):
        op = self.form.cleaned_data['op']
        self.context.update({
            'op': op
        })

        cursor = connections['so'].cursor()

        data = models.base.get_lotes(cursor, op=op, order='o')
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Sem lotes',
            })
            return

        exec = 'repair' in self.request.POST.keys()

        count_repair = 0
        for row in data:
            ret, alt = functions.repair_sequencia_estagio(
                    cursor, row['PERIODO'], row['OC'], exec)
            if ret:
                if exec:
                    row['INFO'] = 'Reparado'
                else:
                    row['INFO'] = 'Reparar'
                    count_repair += 1
            else:
                row['INFO'] = 'OK'
            row['ALT'] = alt

        self.context.update({
            'count_repair': count_repair,
            'headers': ['Período', 'OC', 'Informação', 'Alteração'],
            'fields': ['PERIODO', 'OC', 'INFO', 'ALT'],
            'data': data,
        })

    def start(self, request):
        self.request = request
        self.context = {'titulo': self.title_name}

    def end(self):
        self.context['form'] = self.form
        return render(self.request, self.template_name, self.context)

    def get(self, request, *args, **kwargs):
        self.start(request)
        self.form = self.Form_class()
        return self.end()

    def post(self, request, *args, **kwargs):
        self.start(request)
        self.form = self.Form_class(self.request.POST)
        if self.form.is_valid():
            self.mount_context()
        return self.end()
