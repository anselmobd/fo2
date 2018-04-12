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
                 'Q_CONCERTO', 'FAMI', 'OS')
        group_rowspan(data, group)
        context.update({
            'e_headers': (
                'Estágio', 'Prog.', 'A Prod.', 'Em Prod.', 'Prod.', '2a.',
                'Perda', 'Concerto', 'Família', 'OS', 'Usuário', 'Data',
                'Programa'),
            'e_fields': (
                'EST', 'Q_P', 'Q_AP', 'Q_EP', 'Q_PROD', 'Q_2A',
                'Q_PERDA', 'Q_CONCERTO', 'FAMI', 'OS', 'USU', 'DT',
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
