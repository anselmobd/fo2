from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import totalize_data

import lotes.forms as forms
import lotes.queries.op


class BuscaOP(View):
    Form_class = forms.BuscaOpForm
    template_name = 'lotes/busca_op.html'
    title_name = 'Busca OP'

    def mount_context(
            self, cursor, ref, modelo, tam, cor, deposito, tipo, tipo_alt,
            situacao, posicao, motivo, quant_fin, quant_emp, data_de, data_ate):
        context = {
            'ref': ref,
            'modelo': modelo,
            'tam': tam,
            'cor': cor,
            'deposito': deposito,
            'tipo': tipo,
            'tipo_alt': tipo_alt,
            'situacao': situacao,
            'posicao': posicao,
            'motivo': motivo,
            'quant_fin': quant_fin,
            'quant_emp': quant_emp,
            'data_de': data_de,
            'data_ate': data_ate,
        }

        data = lotes.queries.op.busca_op(
            cursor, ref=ref, modelo=modelo, tam=tam, cor=cor,
            deposito=deposito, tipo=tipo, tipo_alt=tipo_alt, situacao=situacao,
            posicao=posicao, motivo=motivo, quant_fin=quant_fin,
            quant_emp=quant_emp, data_de=data_de, data_ate=data_ate)
        if len(data) == 0:
            context.update({
                'msg_erro': 'OPs não encontradas',
            })
            return context

        safe = []
        for row in data:
            row['OP|LINK'] = '/lotes/op/{}'.format(row['OP'])
            if row['OP_REL'] == '0':
                row['OP_REL'] = '-'
            else:
                # row['OP_REL|SAVE'] = True
                if 'OP_REL' not in safe:
                    safe.append('OP_REL')
                oprel_html = ''
                oprel_sep = ''
                for oprel in row['OP_REL'].split(','):
                    oprel = oprel.strip()
                    oprel_html += oprel_sep + '''
                        <a href="{link}">{op}
                        <span class="glyphicon glyphicon-link"
                        aria-hidden="true"></span></a>
                    '''.format(
                        link=reverse(
                            'producao:op__get', args=[oprel]),
                        op=oprel
                    )
                    oprel_sep = '&nbsp;'
                row['OP_REL'] = oprel_html
            row['REF|LINK'] = reverse('produto:ref__get', args=[row['REF']])
            row['DT_DIGITACAO'] = row['DT_DIGITACAO'].date()
            if row['DT_CORTE'] is None:
                row['DT_CORTE'] = '-'
            else:
                row['DT_CORTE'] = row['DT_CORTE'].date()
            if row['DT_EMBARQUE'] is None:
                row['DT_EMBARQUE'] = '-'
            else:
                row['DT_EMBARQUE'] = row['DT_EMBARQUE'].date()
            if row['STATUS_PEDIDO'] == 5:
                row['STATUS_PEDIDO'] = 'Canc.'
            elif row['STATUS_PEDIDO'] == 0:
                row['STATUS_PEDIDO'] = 'Digit.'
            elif row['STATUS_PEDIDO'] == 2:
                row['STATUS_PEDIDO'] = 'Liber.'
            else:
                row['STATUS_PEDIDO'] = '-'
            if row['ESTAGIO'] is None:
                row['ESTAGIO'] = 'Finalizado*'
            if row['PED'] == 0:
                row['PED'] = '-'
            else:
                row['PED|LINK'] = reverse(
                    'producao:pedido__get', args=[row['PED']])
            if row['LOTES'] is None:
                row['LOTES'] = '0'
            row['QTD_OUTROS'] = row['QTD_AP'] - row['QTD_CD']

        totalize_data(data, {
            'sum': ['QTD', 'QTD_AP', 'QTD_F', 'QTD_CD', 'QTD_OUTROS'],
            'count': [],
            'descr': {'LOTES': 'Totais:'}})

        context.update({
            'headers': ('OP', 'Situação', 'Cancel.',
                        'Pedido', 'Status',
                        'Tipo', 'Referência',
                        'Alt.', 'Roteiro', 'Estágio',
                        'Quant. Lotes', 'Quant. Itens',
                        'Quant. CD', 'Quant. não CD',
                        'Quant. a Prod.', 'Quant. Finaliz.',
                        'Depósito', 'Período',
                        'Data Digitação', 'Data Corte', 'Data Embarque',
                        'OP relacionada'),
            'fields': ('OP', 'SITUACAO', 'CANCELAMENTO',
                       'PED', 'STATUS_PEDIDO',
                       'TIPO_REF', 'REF',
                       'ALTERNATIVA', 'ROTEIRO', 'ESTAGIO',
                       'LOTES', 'QTD',
                       'QTD_CD', 'QTD_OUTROS',
                       'QTD_AP', 'QTD_F',
                       'DEPOSITO_CODIGO', 'PERIODO',
                       'DT_DIGITACAO', 'DT_CORTE', 'DT_EMBARQUE',
                       'OP_REL'),
            'data': data,
            'safe': safe,
            'style': {
                11: 'text-align: right;',
                12: 'text-align: right;',
                13: 'text-align: right;',
                14: 'text-align: right;',
                15: 'text-align: right;',
                16: 'text-align: right;',
                17: 'text-align: center;',
                18: 'text-align: center;',
            },
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
            modelo = form.cleaned_data['modelo']
            tam = form.cleaned_data['tam']
            cor = form.cleaned_data['cor']
            deposito = form.cleaned_data['deposito']
            tipo = form.cleaned_data['tipo']
            tipo_alt = form.cleaned_data['tipo_alt']
            situacao = form.cleaned_data['situacao']
            posicao = form.cleaned_data['posicao']
            motivo = form.cleaned_data['motivo']
            quant_fin = form.cleaned_data['quant_fin']
            quant_emp = form.cleaned_data['quant_emp']
            data_de = form.cleaned_data['data_de']
            data_ate = form.cleaned_data['data_ate']
            cursor = db_cursor_so(request)
            context.update(
                self.mount_context(
                    cursor, ref, modelo, tam, cor, deposito, tipo, tipo_alt,
                    situacao, posicao, motivo, quant_fin, quant_emp, data_de, data_ate))
        context['form'] = form
        return render(request, self.template_name, context)
