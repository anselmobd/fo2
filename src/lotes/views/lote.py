from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.views import View

from fo2.template import group_rowspan

from lotes.forms import LoteForm
import lotes.models as models


class Posicao(View):
    Form_class = LoteForm
    template_name = 'lotes/posicao.html'
    title_name = 'Posição do lote'

    def mount_context(self, cursor, periodo, ordem_confeccao):
        context = {}

        data = models.posicao_lote(cursor, periodo, ordem_confeccao)
        row = data[0]
        context.update({
            'codigo_estagio': row['CODIGO_ESTAGIO'],
            'descricao_estagio': row['DESCRICAO_ESTAGIO'],
        })

        data = models.posicao_periodo_oc(cursor, periodo, ordem_confeccao)
        if len(data) != 0:
            context.update({
                'l_headers': ('Período', 'Incício', 'Fim', 'OC'),
                'l_fields': ('PERIODO', 'INI', 'FIM', 'OC'),
                'l_data': data,
            })

        data = models.posicao_get_op(cursor, periodo, ordem_confeccao)
        if len(data) != 0:
            link = ('OP')
            for row in data:
                row['LINK'] = '/lotes/op/{}'.format(row['OP'])
            context.update({
                'o_headers': ('OP', 'Situação', 'Programa', 'Data/hora'),
                'o_fields': ('OP', 'SITU', 'PRG', 'DT'),
                'o_data': data,
                'o_link': link,
            })

        os_data = models.posicao_get_os(cursor, periodo, ordem_confeccao)
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
                'os_headers': (
                    'OS', 'Serviço', 'Terceiro', 'Emissão', 'Entrega',
                    'Situação', 'Cancelamento', 'Lotes', 'Quant.'),
                'os_fields': (
                    'OS', 'SERV', 'TERC', 'DATA_EMISSAO', 'DATA_ENTREGA',
                    'SITUACAO', 'CANC', 'LOTES', 'QTD'),
                'os_data': os_data,
                'os_link': os_link,
            })

        i_data = models.posicao_get_item(cursor, periodo, ordem_confeccao)
        i_link = ('REF')
        for row in i_data:
            row['LINK'] = '/produto/ref/{}'.format(row['REF'])
        context.update({
            'i_headers': ('Quantidade', 'Tipo', 'Referência', 'Cor', 'Tamanho',
                          'Descrição', 'Item'),
            'i_fields': ('QTDE', 'TIPO', 'REF', 'COR', 'TAM',
                         'NARR', 'ITEM'),
            'i_data': i_data,
            'i_link': i_link,
        })

        data = models.posicao_estagios(cursor, periodo, ordem_confeccao)
        group = ('EST', 'Q_P', 'Q_AP', 'Q_EP', 'Q_PROD', 'Q_2A', 'Q_PERDA',
                 'Q_CONSERTO', 'FAMI', 'OS')
        group_rowspan(data, group)
        context.update({
            'e_headers': (
                'Estágio', 'Prog.', 'A Prod.', 'Em Prod.', 'Prod.', '2a.',
                'Perda', 'Conserto', 'Família', 'OS', 'Usuário', 'Data',
                'Programa'),
            'e_fields': (
                'EST', 'Q_P', 'Q_AP', 'Q_EP', 'Q_PROD', 'Q_2A',
                'Q_PERDA', 'Q_CONSERTO', 'FAMI', 'OS', 'USU', 'DT',
                'PRG'),
            'e_group': group,
            'e_data': data,
        })

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
        form = self.Form_class(request.POST)
        if 'lote' in kwargs:
            form.data['lote'] = kwargs['lote']
        if form.is_valid():
            lote = form.cleaned_data['lote']
            periodo = lote[:4]
            ordem_confeccao = lote[-5:]
            cursor = connections['so'].cursor()
            data = models.existe_lote(cursor, periodo, ordem_confeccao)
            if len(data) == 0:
                context['erro'] = '.'
            else:
                context['lote'] = lote
                data = self.mount_context(cursor, periodo, ordem_confeccao)
                context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)


class Posicao2(View):
    Form_class = LoteForm
    template_name = 'lotes/posicao2.html'
    title_name = 'Posição do lote (versão nova)'

    def mount_context(self, cursor, periodo, ordem_confeccao):
        context = {}

        data = models.posicao2_lote(cursor, periodo, ordem_confeccao)
        if len(data) != 0:
            context.update({
                'p_headers': ('Posição', 'Quantidade', 'Estágio'),
                'p_fields': ('TIPO', 'QTD', 'ESTAGIO'),
                'p_style': {1: 'font-size: large;',
                            2: 'font-size: large;',
                            3: 'font-size: large;',
                            },
                'p_data': data,
            })

        data = models.posicao_periodo_oc(cursor, periodo, ordem_confeccao)
        if len(data) != 0:
            context.update({
                'l_headers': ('Período', 'Incício', 'Fim', 'OC'),
                'l_fields': ('PERIODO', 'INI', 'FIM', 'OC'),
                'l_data': data,
            })

        data = models.posicao_get_op(cursor, periodo, ordem_confeccao)
        if len(data) != 0:
            link = ('OP')
            for row in data:
                row['LINK'] = '/lotes/op/{}'.format(row['OP'])
            context.update({
                'o_headers': ('OP', 'Situação', 'Programa',
                              'Data digitação', 'Data de corte'),
                'o_fields': ('OP', 'SITU', 'PRG',
                             'DT', 'DT_CORTE'),
                'o_data': data,
                'o_link': link,
            })

        os_data = models.posicao_get_os(cursor, periodo, ordem_confeccao)
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
                'os_headers': (
                    'OS', 'Serviço', 'Terceiro', 'Emissão', 'Entrega',
                    'Situação', 'Cancelamento', 'Lotes', 'Quant.'),
                'os_fields': (
                    'OS', 'SERV', 'TERC', 'DATA_EMISSAO', 'DATA_ENTREGA',
                    'SITUACAO', 'CANC', 'LOTES', 'QTD'),
                'os_data': os_data,
                'os_link': os_link,
            })

        i_data = models.posicao_get_item(cursor, periodo, ordem_confeccao)
        i_link = ('REF')
        for row in i_data:
            row['LINK'] = '/produto/ref/{}'.format(row['REF'])
        context.update({
            'i_headers': ('Quantidade', 'Tipo', 'Referência', 'Cor', 'Tamanho',
                          'Descrição', 'Item'),
            'i_fields': ('QTDE', 'TIPO', 'REF', 'COR', 'TAM',
                         'NARR', 'ITEM'),
            'i_data': i_data,
            'i_link': i_link,
        })

        data = models.posicao_so_estagios(cursor, periodo, ordem_confeccao)
        estagios = []
        q_programada = None
        for row in data:
            estagios.append(row['COD_EST'])
            if q_programada is None:
                q_programada = row['Q_P']
            if row['Q_AP'] == 0:
                row['Q_AP'] = '.'
            if row['Q_EP'] == 0:
                row['Q_EP'] = '.'
            if row['Q_PROD'] == 0:
                row['Q_PROD'] = '.'
            if row['Q_2A'] == 0:
                row['Q_2A'] = '.'
            if row['Q_PERDA'] == 0:
                row['Q_PERDA'] = '.'
            if row['Q_CONSERTO'] == 0:
                row['Q_CONSERTO'] = '.'
            if row['FAMI'] == 0:
                row['FAMI'] = '.'
            if row['OS'] == 0:
                row['OS'] = '.'
        context.update({
            'se_headers': (
                'Estágio', 'Progr.', 'A Prod.', 'Em Prod.',
                'Prod. 1ª', 'Prod. 2ª', 'Perda', 'Conserto',
                'Família', 'OS'),
            'se_fields': (
                'EST', 'Q_P', 'Q_AP', 'Q_EP',
                'Q_PROD', 'Q_2A', 'Q_PERDA', 'Q_CONSERTO',
                'FAMI', 'OS'),
            'se_data': data,
        })

        # data = models.posicao_historico(cursor, periodo, ordem_confeccao)
        # hh_headers = ['Data', 'Turno', 'Família', 'Estágio']
        # hh_fields = ['DT', 'TURNO', 'FAMILIA', 'EST']
        # for row in data:
        #     for estagio in estagios:
        #         field_est = 'Q_E{}'.format(estagio)
        #         row[field_est] = ''
        #         sep = ''
        #         if estagio == row['EST']:
        #             if row['Q_P1'] != 0:
        #                 if row['Q_P1'] > 0:
        #                     indicador = '->'
        #                 else:
        #                     indicador = '<-'
        #                 row[field_est] += sep + '1ª:{}{}'.format(
        #                     row['Q_P1'], indicador)
        #                 sep = ', '
        #             if row['Q_P2'] != 0:
        #                 pprint(row['Q_P2'])
        #                 if row['Q_P2'] > 0:
        #                     indicador = '->'
        #                 else:
        #                     indicador = '<-'
        #                 row[field_est] += sep + '2ª:{}{}'.format(
        #                     row['Q_P2'], indicador)
        #                 sep = ', '
        #         else:
        #             row[field_est] = '.'
        #     row['PRG|HOVER'] = row['PRG_DESCR']
        #     if row['FAMILIA'] == 0:
        #         row['FAMILIA'] = '.'
        #     if row['Q_P1'] == 0:
        #         row['Q_P1'] = '.'
        #     if row['Q_P2'] == 0:
        #         row['Q_P2'] = '.'
        #     if row['Q_P'] == 0:
        #         row['Q_P'] = '.'
        #     if row['Q_C'] == 0:
        #         row['Q_C'] = '.'
        # for estagio in estagios:
        #     hh_fields.append('Q_E{}'.format(estagio))
        # hh_fields += [
        #     'Q_P1', 'Q_P2', 'Q_P', 'Q_C',
        #     'USU', 'PRG']
        # hh_headers += estagios
        # hh_headers += [
        #     'Prod. 1ª', 'Prod. 2ª', 'Perda', 'Conserto',
        #     'Usuário', 'Programa']
        # context.update({
        #     'hh_headers': hh_headers,
        #     'hh_fields': hh_fields,
        #     'hh_data': data,
        # })

        data = models.posicao_historico(cursor, periodo, ordem_confeccao)
        for row in data:
            row['PRG|HOVER'] = row['PRG_DESCR']
            if row['FAMILIA'] == 0:
                row['FAMILIA'] = '.'
            if row['Q_P1'] == 0:
                row['Q_P1'] = '.'
            if row['Q_P2'] == 0:
                row['Q_P2'] = '.'
            if row['Q_P'] == 0:
                row['Q_P'] = '.'
            if row['Q_C'] == 0:
                row['Q_C'] = '.'
        context.update({
            'h_headers': (
                'Data', 'Turno', 'Família', 'Estágio',
                'Prod. 1ª', 'Prod. 2ª', 'Perda', 'Conserto',
                'Usuário', 'Programa'),
            'h_fields': (
                'DT', 'TURNO', 'FAMILIA', 'EST',
                'Q_P1', 'Q_P2', 'Q_P', 'Q_C',
                'USU', 'PRG'),
            'h_data': data,
        })

        # data = models.posicao_estagios(cursor, periodo, ordem_confeccao)
        # group = ('EST', 'Q_P', 'Q_AP', 'Q_EP', 'Q_PROD', 'Q_2A', 'Q_PERDA',
        #          'Q_CONSERTO', 'FAMI', 'OS')
        # group_rowspan(data, group)
        # context.update({
        #     'e_headers': (
        #         'Estágio', 'Progr.', 'A Prod.', 'Em Prod.', 'Prod.', '2a.',
        #         'Perda', 'Conserto', 'Família', 'OS', 'Usuário', 'Data',
        #         'Programa'),
        #     'e_fields': (
        #         'EST', 'Q_P', 'Q_AP', 'Q_EP', 'Q_PROD', 'Q_2A',
        #         'Q_PERDA', 'Q_CONSERTO', 'FAMI', 'OS', 'USU', 'DT',
        #         'PRG'),
        #     'e_group': group,
        #     'e_data': data,
        # })

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
        form = self.Form_class(request.POST)
        if 'lote' in kwargs:
            form.data['lote'] = kwargs['lote']
        if form.is_valid():
            lote = form.cleaned_data['lote']
            periodo = lote[:4]
            ordem_confeccao = lote[-5:]
            cursor = connections['so'].cursor()
            data = models.existe_lote(cursor, periodo, ordem_confeccao)
            if len(data) == 0:
                context['erro'] = '.'
            else:
                context['lote'] = lote
                data = self.mount_context(cursor, periodo, ordem_confeccao)
                context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)
