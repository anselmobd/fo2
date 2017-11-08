from django.shortcuts import render
from django.db import connections
from django.views import View

from fo2.template import group_rowspan

from lotes.forms import OsForm
import lotes.models as models


class Os(View):
    Form_class = OsForm
    template_name = 'lotes/os.html'
    title_name = 'OS'

    def mount_context(self, cursor, os):
        context = {'os': os}

        # A ser produzido
        data = models.os_inform(cursor, os)
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
            o_data = models.os_op(cursor, os)
            if len(o_data) != 0:
                for row in o_data:
                    row['OP|LINK'] = '/lotes/op/{}'.format(row['OP'])
                    if row['PEDIDO'] == 0:
                        row['PEDIDO'] = ''
                    else:
                        row['PEDIDO|LINK'] = '/lotes/pedido/{}'.format(
                            row['PEDIDO'])
                context.update({
                    'o_headers': ('OP', 'Lotes', 'Quant.', 'Pedido',
                                  'Pedido do cliente'),
                    'o_fields': ('OP', 'LOTES', 'QTD', 'PEDIDO',
                                 'PED_CLIENTE'),
                    'o_data': o_data,
                })

        # Grade
        g_header, g_fields, g_data = models.os_sortimento(cursor, os)
        if len(g_data) != 0:
            context.update({
                'g_headers': g_header,
                'g_fields': g_fields,
                'g_data': g_data,
            })

        # Itens para nota de OS
        i_data = models.os_itens(cursor, os)
        for row in i_data:
            rowlinks = {}
            if row['NIVEL'] is '1':
                row['REF|LINK'] = '/produto/ref/{}'.format(row['REF'])
            else:
                row['REF|LINK'] = '/insumo/ref/{}'.format(row['REF'])

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
        l_data = models.os_lotes(cursor, os)
        if len(l_data) != 0:
            l_link = ('LOTE')
            for row in l_data:
                row['LOTE'] = '{}{:05}'.format(row['PERIODO'], row['OC'])
                row['LINK'] = '/lotes/posicao/{}'.format(row['LOTE'])
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
        if 'os' in kwargs:
            form.data['os'] = kwargs['os']
        if form.is_valid():
            os = form.cleaned_data['os']
            cursor = connections['so'].cursor()
            context.update(self.mount_context(cursor, os))
        context['form'] = form
        return render(request, self.template_name, context)
