from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.views import group_rowspan

from lotes.forms import OsForm
import lotes.queries.lote
import lotes.queries.os
from lotes.queries.lote import get_lotes


class Os(View):

    def __init__(self):
        super().__init__()
        self.Form_class = OsForm
        self.template_name = 'lotes/os.html'
        self.title_name = 'OS'

    def mount_context(self, cursor, os):
        context = {'os': os}

        # A ser produzido
        data = lotes.queries.os.os_inform(cursor, os)
        if len(data) == 0:
            context.update({
                'msg_erro': 'OS vazia',
            })
        else:
            for row in data:
                cnpj = '{:08d}/{:04d}-{:02d}'.format(
                    row['CNPJ9'],
                    row['CNPJ4'],
                    row['CNPJ2'])
                row['TERC'] = '{} - {}'.format(cnpj, row['NOME'])
            context.update({
                'headers': ('Serviço', 'Terceiro', 'Emissão', 'Entrega',
                            'Situação', 'Cancelamento'),
                'fields': ('SERV', 'TERC', 'DATA_EMISSAO', 'DATA_ENTREGA',
                           'SITUACAO', 'CANC'),
                'data': data,
            })
            context.update({
                'headers2': ('Observação', 'Lotes', 'Quant.'),
                'fields2': ('OBSERVACAO', 'LOTES', 'QTD'),
                'data2': data,
            })

            # Totais por OP
            o_data = lotes.queries.os.os_op(cursor, os)
            if len(o_data) != 0:
                for row in o_data:
                    row['OP|LINK'] = reverse('producao:op__get', args=[row['OP']])
                    if row['PED_CLIENTE'] is None:
                        row['PED_CLIENTE'] = '-'
                    if row['PEDIDO'] == 0:
                        row['PEDIDO'] = '-'
                    else:
                        row['PEDIDO|LINK'] = reverse(
                            'producao:pedido__get', args=[row['PEDIDO']])
                context.update({
                    'o_headers': ('OP', 'Lotes', 'Quant.', 'Pedido',
                                  'Pedido do cliente'),
                    'o_fields': ('OP', 'LOTES', 'QTD', 'PEDIDO',
                                 'PED_CLIENTE'),
                    'o_data': o_data,
                })

        # Grade
        g_header, g_fields, g_data = lotes.queries.os.os_sortimento(cursor, os)
        if len(g_data) != 0:
            context.update({
                'g_headers': g_header,
                'g_fields': g_fields,
                'g_data': g_data,
            })

        # Itens para nota de OS
        i_data = lotes.queries.os.os_itens(cursor, os)
        for row in i_data:
            rowlinks = {}
            if row['NIVEL'] == '1':
                row['REF|LINK'] = reverse(
                    'produto:ref__get', args=[row['REF']])
            else:
                row['REF|LINK'] = reverse('insumo:ref__get', args=[row['REF']])

            if row['NF'] == 0:
                row['NF'] = ''
                row['DATA_NF'] = ''
            else:
                row['DATA_NF'] = row['DATA_NF'].date()

            if row['NF_RETORNO'] is None:
                row['DIAS'] = ''
                row['NF_RETORNO'] = ''
                row['DATA_RETORNO'] = ''
                row['QTD_RETORNO'] = ''
                row['RETORNO'] = ''
                row['APLICADO'] = ''
            else:
                if row['DATA_RETORNO'] is None:
                    row['DATA_RETORNO'] = ''
                else:
                    row['DATA_RETORNO'] = row['DATA_RETORNO'].date()
        i_group = ['NIVEL', 'REF', 'COR', 'TAM', 'NARRATIVA',
                   'UN', 'VALOR_UN', 'QTD_ESTR',
                   'QTD_ENV', 'NF', 'DATA_NF']
        group_rowspan(i_data, i_group)

        context.update({
            'i_headers': ('Nível', 'Ref.', 'Cor', 'Tam.', 'Narrativa',
                          'Unidade', 'Valor unitário', 'Qtd.Estrutura',
                          'Qtd.Enviada', 'NF de saída',
                          'Data emissão', 'Dias',
                          'NF de retorno', 'Data emissão',
                          'Qtd.Retorno', 'Retorno', 'Aplicado'),
            'i_fields': ('NIVEL', 'REF', 'COR', 'TAM', 'NARRATIVA',
                         'UN', 'VALOR_UN', 'QTD_ESTR',
                         'QTD_ENV', 'NF',
                         'DATA_NF', 'DIAS',
                         'NF_RETORNO', 'DATA_RETORNO',
                         'QTD_RETORNO', 'RETORNO', 'APLICADO'),
            'i_group': i_group,
            'i_data': i_data,
        })

        # Lotes ordenados por OS + referência + estágio
        l_data = get_lotes.os_lotes(cursor, os)
        if len(l_data) != 0:
            l_link = ('LOTE')
            for row in l_data:
                row['LOTE'] = '{}{:05}'.format(row['PERIODO'], row['OC'])
                row['LINK'] = reverse('producao:lote__get', args=[row['LOTE']])
            context.update({
                'l_headers': ('OP', 'Referência', 'Cor', 'Tamanho',
                              'Estágio', 'Período', 'OC', 'Quant.', 'Lote'),
                'l_fields': ('OP', 'REF', 'COR', 'TAM',
                             'EST', 'PERIODO', 'OC', 'QTD', 'LOTE'),
                'l_data': l_data,
                'l_link': l_link,
            })

        return context

    def get(self, request, *args, **kwargs):
        if 'os' in kwargs:
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
        if 'os' in kwargs:
            form.data['os'] = kwargs['os']
        if form.is_valid():
            os = form.cleaned_data['os']
            cursor = db_cursor_so(request)
            context.update(self.mount_context(cursor, os))
        context['form'] = form
        return render(request, self.template_name, context)
