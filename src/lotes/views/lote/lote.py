from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from geral.functions import has_permission
from utils.functions import untuple_keys_concat
from utils.functions.digits import fo2_digit_with
from utils.views import totalize_data

import lotes.models as models
import lotes.queries as queries
import lotes.queries.lote
from lotes.forms import LoteForm
from lotes.queries.lote import get_lotes

__all__ = ['Lote']


class Lote(View):

    def __init__(self):
        super().__init__()
        self.Form_class = LoteForm
        self.template_name = 'lotes/posicao.html'
        self.title_name = 'Lote/OC'
        self.request = {}

    def mount_context(self, cursor, periodo, ordem_confeccao, lote):
        context = {}
        produz_estorna =(
            self.request.user.is_authenticated and
            has_permission(self.request, 'lotes.pode_produzir_lote')
        )

        data = queries.lote.posicoes_lote(cursor, periodo, ordem_confeccao)
        if len(data) != 0:
            headers = ['Posição', 'Quantidade', 'Estágio']
            fields = ['TIPO', 'QTD', 'ESTAGIO']
            context.update({
                'p_headers': headers,
                'p_fields': fields,
                'p_style': {0: 'font-size: large;', },
                'p_data': data,
            })

        oc_data = queries.lote.posicao_periodo_oc(
            cursor, periodo, ordem_confeccao)
        if len(oc_data) != 0:
            context.update({
                'l_headers': ('Período', 'Incício', 'Fim', 'OC'),
                'l_fields': ('PERIODO', 'INI', 'FIM', 'OC'),
                'l_data': oc_data,
            })

        op_data = queries.lote.posicao_get_op(cursor, periodo, ordem_confeccao)
        if len(op_data) != 0:
            link = ('OP')
            for row in op_data:
                row['LINK'] = reverse('producao:op__get', args=[row['OP']])
            context.update({
                'o_headers': ('OP', 'Situação', 'Programa',
                              'Data digitação', 'Data de corte'),
                'o_fields': ('OP', 'SITU', 'PRG',
                             'DT', 'DT_CORTE'),
                'o_data': op_data,
                'o_link': link,
            })

        nlote_data = get_lotes.get_lotes(
            cursor, op=op_data[0]['OP'], oc=oc_data[0]['OC'], order='o')
        nloted = nlote_data[0]
        context.update({
            'nloted': nloted,
        })

        os_data = queries.os.get_os(
            cursor, periodo=periodo, oc=ordem_confeccao)
        if len(os_data) != 0:
            os_link = ('OS')
            for row in os_data:
                row['LINK'] = reverse('producao:os__get', args=[row['OS']])
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

        i_data = queries.lote.posicao_get_item(
            cursor, periodo, ordem_confeccao)
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

        data = queries.lote.posicao_so_estagios(
            cursor, periodo, ordem_confeccao)
        estagios = []
        for row in data:
            estagios.append(row['COD_EST'])
            if row['Q_DB'] > 0:
                row['Q_PRODUZ|SAFE'] = True
                row['Q_PRODUZ'] = f"""
                    <input value="{row['Q_DB']}" type="text" size="3" id="QTDPROD_{row['COD_EST']}" class="input_ajax">
                """
                row['PRODUZ'] = "Produz⭣"
                row['PRODUZ|CLASS'] = 'produzir_ajax'
                row['PRODUZ|TARGET'] = 'BLANK'
                row['PRODUZ|A'] = reverse(
                    'producao:produz_lote_programa',
                    args=[
                        lote,
                        row['COD_EST'],
                        'QTDPROD',
                        'lote_oc',
                    ]
                )
            else:
                row['Q_PRODUZ'] = "."
                row['PRODUZ'] = "."
        q_estornavel = data[-1]['Q_PROD']
        for row in data[::-1]:
            if q_estornavel > 0:
                row['Q_ESTORMA|SAFE'] = True
                row['Q_ESTORMA'] = f"""
                    <input value="{q_estornavel}" type="text" size="3" id="QTDESTO_{row['COD_EST']}" class="input_ajax">
                """
                row['ESTORMA'] = "Extorna⮌"
                row['ESTORMA|CLASS'] = 'produzir_ajax'
                row['ESTORMA|TARGET'] = 'BLANK'
                row['ESTORMA|A'] = reverse(
                    'producao:produz_lote_programa',
                    args=[
                        lote,
                        row['COD_EST'],
                        '-QTDESTO',
                        'lote_oc',
                    ]
                )
            else:
                row['Q_ESTORMA'] = "."
                row['ESTORMA'] = "."
            q_estornavel = row['Q_DB']
        for row in data:
            for field in [
                    'Q_AP', 'Q_EP', 'Q_DB', 'Q_PROD', 'Q_2A', 'Q_PERDA',
                    'Q_CONSERTO', 'FAMI', 'OS']:
                if row[field] == 0:
                    row[field] = '.'
        context.update({
            'se_headers': (
                ['Estágio', 'Progr.', 'A Prod.', 'Em Prod.', 'Disp. Baixa']
                + (["Qtd. Produz", "Produz", "Qtd. Extorna", "Extorna"] if produz_estorna else [])
                + [
                    'Prod. 1ª', 'Prod. 2ª', 'Perda', 'Cons./End.', 'Família', 'OS',
                    'Seq. Oper.', 'Seq. Est.', 'Est. Ant.',
                ]),
            'se_fields': (
                ['EST', 'Q_P', 'Q_AP', 'Q_EP', 'Q_DB']
                + (['Q_PRODUZ', 'PRODUZ', 'Q_ESTORMA', 'ESTORMA'] if produz_estorna else [])
                + [
                    'Q_PROD', 'Q_2A', 'Q_PERDA', 'Q_CONSERTO', 'FAMI', 'OS',
                    'SEQ_OPER', 'SEQ_EST', 'EST_ANT',
                ]),
            'se_data': data,
            'se_style': untuple_keys_concat({
                (2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 16, 17, 18): 'text-align: right;',
                (7, 9, 14, 15): 'text-align: center;',
            }),
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
            if row['Q_C'] == 0:
                row['Q_C'] = ''
                row['C_OU_E'] = '.'
            else:
                if row['EST'] == 63:
                    row['C_OU_E'] = 'endereçado'
                else:
                    row['C_OU_E'] = 'em conserto'
            for field in ['FAMILIA', 'Q_P1', 'Q_P2', 'Q_P']:
                if row[field] == 0 or row[field] is None:
                    row[field] = '.'
            row['DT_PROD'] = row['DT_PROD'].date()
            row['EST'] = (f"{'&middot;&nbsp;'*estagios.index(row['EST'])}"
                          f"{row['EST']}")

        context.update({
            'h_headers': (
                'Data Bipagem', 'Data Produção', 'Turno', 'Família', 'Estágio',
                'Prod. 1ª', 'Prod. 2ª', 'Perda',
                '', 'Cons./End.',
                'Usuário', 'Programa'),
            'h_fields': (
                'DT', 'DT_PROD', 'TURNO', 'FAMILIA', 'EST',
                'Q_P1', 'Q_P2', 'Q_P',
                'Q_C', 'C_OU_E',
                'USU', 'PRG'),
            'h_data': data,
            'h_safe': ['EST'],
            'h_style': untuple_keys_concat({
                (6, 7, 8, 9): 'text-align: right;',
                (2, 3, 4): 'text-align: center;',
            }),
        })

        slq = models.SolicitaLoteQtd.objects.filter(
            lote__lote=lote,
            ).order_by('-create_at').values(
            'solicitacao_id', 'solicitacao__codigo', 'solicitacao__descricao',
            'solicitacao__data', 
            'solicitacao__usuario__username', 'create_at', 'qtd')
        slq = list(slq)

        desreserva_lote = False
        solicit_id = None
        if len(slq) != 0:
            if has_permission(self.request, 'lotes.change_solicitalote'):
                desreserva_lote = True
                solicit_id = slq[0]['solicitacao_id']

        for row in slq:
            if row['solicitacao__data'] is None:
                row['solicitacao__data'] = ''
            row['numero'] = f"#{fo2_digit_with(row['solicitacao_id'])}"
            row['solicitacao__codigo|TARGET'] = '_blank'
            row['solicitacao__codigo|LINK'] = reverse(
                'cd:solicitacao_detalhe', args=[row['solicitacao_id']])
        if len(slq) > 1:
            totalize_data(slq, {
                'sum': ['qtd'],
                'descr': {'create_at': 'Total:'},
                'row_style': 'font-weight: bold;',
            })
        context.update({
            'slq_headers': (
                '#', 'Solicidação', 'Descrição',
                'Data de embarque',
                'Usuário', 'Data', 'Quantidade'),
            'slq_fields': (
                'numero', 'solicitacao__codigo', 'solicitacao__descricao',
                'solicitacao__data',
                'solicitacao__usuario__username', 'create_at', 'qtd'),
            'slq_data': slq,
            'slq_style': {7: 'text-align: right;'},
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
        form.data = form.data.copy()
        if 'lote' in kwargs:
            form.data['lote'] = kwargs['lote']
        if form.is_valid():
            lote = form.cleaned_data['lote']
            periodo = lote[:4]
            ordem_confeccao = lote[-5:]
            cursor = db_cursor_so(request)
            data = queries.lote.existe_lote(cursor, periodo, ordem_confeccao)
            if len(data) == 0:
                context['erro'] = '.'
            else:
                context['lote'] = lote
                data = self.mount_context(
                    cursor, periodo, ordem_confeccao, lote)
                context.update(data)
        context['form'] = form
        return render(request, self.template_name, context)
