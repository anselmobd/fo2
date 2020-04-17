from pprint import pprint

from django.shortcuts import render
from django.db import connections
from django.urls import reverse
from django.views import View

from geral.functions import request_user, has_permission
from utils.views import group_rowspan

import lotes.models as models
import lotes.queries as queries
import lotes.queries.lote
from lotes.forms import LoteForm


class Posicao(View):
    Form_class = LoteForm
    template_name = 'lotes/posicao.html'
    title_name = 'Posição do lote'
    request = {}

    def mount_context(self, cursor, periodo, ordem_confeccao, lote):
        context = {}

        data = models.posicao2_lote(cursor, periodo, ordem_confeccao)
        if len(data) != 0:
            context.update({
                'p_headers': ('Posição', 'Quantidade', 'Estágio'),
                'p_fields': ('TIPO', 'QTD', 'ESTAGIO'),
                'p_style': {0: 'font-size: large;', },
                'p_data': data,
            })

        oc_data = models.posicao_periodo_oc(cursor, periodo, ordem_confeccao)
        if len(oc_data) != 0:
            context.update({
                'l_headers': ('Período', 'Incício', 'Fim', 'OC'),
                'l_fields': ('PERIODO', 'INI', 'FIM', 'OC'),
                'l_data': oc_data,
            })

        op_data = models.posicao_get_op(cursor, periodo, ordem_confeccao)
        if len(op_data) != 0:
            link = ('OP')
            for row in op_data:
                row['LINK'] = '/lotes/op/{}'.format(row['OP'])
            context.update({
                'o_headers': ('OP', 'Situação', 'Programa',
                              'Data digitação', 'Data de corte'),
                'o_fields': ('OP', 'SITU', 'PRG',
                             'DT', 'DT_CORTE'),
                'o_data': op_data,
                'o_link': link,
            })

        nlote_data = queries.lote.get_lotes(
            cursor, op=op_data[0]['OP'], oc=oc_data[0]['OC'], order='o')
        nloted = nlote_data[0]
        context.update({
            'nloted': nloted,
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
            row['LINK'] = reverse('produto:ref__get', args=[row['REF']])
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
            for field in [
                    'Q_AP', 'Q_EP', 'Q_PROD', 'Q_2A', 'Q_PERDA',
                    'Q_CONSERTO', 'FAMI', 'OS']:
                if row[field] == 0:
                    row[field] = '.'
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

        # data = lotes.queries.lote.posicao_historico(
        #     cursor, periodo, ordem_confeccao)
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

        data = lotes.queries.lote.posicao_historico(
            cursor, periodo, ordem_confeccao)
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
            row['DT_PROD'] = row['DT_PROD'].date()
        context.update({
            'h_headers': (
                'Data Bipagem', 'Data Produção', 'Turno', 'Família', 'Estágio',
                'Prod. 1ª', 'Prod. 2ª', 'Perda', 'Conserto',
                'Usuário', 'Programa'),
            'h_fields': (
                'DT', 'DT_PROD', 'TURNO', 'FAMILIA', 'EST',
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

        slq = models.SolicitaLoteQtd.objects.filter(
            lote__lote=lote,
            ).order_by('-create_at').values(
            'solicitacao_id', 'solicitacao__codigo', 'solicitacao__descricao',
            'solicitacao__usuario__username', 'create_at', 'qtd')
        slq_link = ('solicitacao__codigo')

        desreserva_lote = False
        solicit_id = None
        if len(slq) != 0:
            if has_permission(self.request, 'lotes.change_solicitalote'):
                desreserva_lote = True
                solicit_id = slq[0]['solicitacao_id']

        for row in slq:
            row['LINK'] = reverse(
                'cd:solicitacao_detalhe', args=[row['solicitacao_id']])
        context.update({
            'slq_headers': (
                'Solicidação', 'Descrição',
                'Usuário', 'Data', 'Quantidade'),
            'slq_fields': (
                'solicitacao__codigo', 'solicitacao__descricao',
                'solicitacao__usuario__username', 'create_at', 'qtd'),
            'slq_data': slq,
            'slq_link': slq_link,
            'desreserva_lote': desreserva_lote,
            'solicit_id': solicit_id,
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
        self.request = request
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
                data = self.mount_context(
                    cursor, periodo, ordem_confeccao, lote)
                context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)
