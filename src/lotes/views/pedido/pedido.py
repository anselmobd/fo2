import re
from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from cd.queries.novo_modulo.solicitacoes import get_solicitacoes
from base.forms.forms2 import Forms2
from geral.functions import get_empresa
from utils.functions import coalesce

from cd.queries.novo_modulo.agrupador import get_agrupador

import lotes.models as models
import lotes.queries as queries
from lotes.queries.pedido import ped_nf_rolos
from lotes.queries.pedido.ped_alter import pedidos_filial_na_data


class Pedido(View):
    Form_class = Forms2().Pedido
    title_name = 'Pedido'
    template_name = 'lotes/pedido.html'

    def set_context(self, request):
        self.context = {
            'titulo': self.title_name,
        }
        if get_empresa(request) == 'agator':
            self.empresa = 2
            self.context.update({
                'extends_html': 'lotes/index_agator.html',
            })
        else:
            self.empresa = (1, 3)
            self.context.update({
                'extends_html': 'lotes/index.html'
            })

    def mount_context(self, cursor, pedido):
        self.context.update({
            'pedido': pedido,
        })

        # informações gerais
        data = queries.pedido.ped_inform(cursor, pedido, empresa=self.empresa)
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Pedido não encontrado',
            })
            return

        empresa = data[0]['CODIGO_EMPRESA']
        fantasia = data[0]['FANTASIA']

        for row in data:
            row['DT_EMISSAO'] = row['DT_EMISSAO'].date()
            row['DT_EMBARQUE'] = row['DT_EMBARQUE'].date()
            if row['OBSERVACAO'] is None:
                row['OBSERVACAO'] = '-'
            ped_cliente = row['PEDIDO_CLIENTE'].strip()
            if ped_cliente != '':
                row['PEDIDO_CLIENTE|TARGET'] = '_blank'
                row['PEDIDO_CLIENTE|LINK'] = reverse(
                    'producao:expedicao__get', args=[
                        row['CLIENTE_9'],
                        ped_cliente,
                    ])

        self.context.update({
            'headers': ('Empresa', 'Data de emissão', 'Data de embarque',
                        'Cliente', 'Fantasia', 'Código do pedido no cliente'),
            'fields': ('EMPRESA', 'DT_EMISSAO', 'DT_EMBARQUE',
                        'CLIENTE', 'FANTASIA', 'PEDIDO_CLIENTE'),
            'data': data,
        })

        self.context.update({
            'headers2': (
                'Status do pedido', 'Cancelamento',
                'Situação da venda', 'Observação',
            ),
            'fields2': (
                'STATUS_PEDIDO', 'CANCELAMENTO_DESCR',
                'SITUACAO_VENDA', 'OBSERVACAO',
            ),
            'data2': data,
            'reativa_pedido': pedido if data[0]['COD_CANCELAMENTO'] != 0 else None,
        })

        # Depósitos
        d_data = queries.pedido.ped_dep_qtd(cursor, pedido)
        self.context.update({
            'd_headers': ('Depósito', 'Quantidade'),
            'd_fields': ('DEPOSITO', 'QTD'),
            'd_data': d_data,
        })

        # Solicitações
        s_data = get_solicitacoes(cursor, pedido_destino=pedido)
        for row in s_data:
            if row['solicitacao']:
                solicitacao_url = row['solicitacao']
            else:
                solicitacao_url = 'sn'
                row['solicitacao'] = '#'
            row['solicitacao|TARGET'] = '_blank'
            row['solicitacao|LINK'] = reverse(
                'cd:novo_solicitacao',
                args=[solicitacao_url]
            )+f"?pedido={pedido}"

        self.context.update({
            's_headers': ["Solicitação"],
            's_fields': ["solicitacao"],
            's_data': s_data,
        })

        # agrupador
        agr_data = get_agrupador(cursor, pedido)
        self.context.update({
            'agr_headers': ["Agrupador"],
            'agr_fields': ["agrupador"],
            'agr_data': agr_data,
        })

        # OPs
        o_data = queries.pedido.ped_op(cursor, pedido)

        if any([
            row['TEM_15']
            for row in o_data    
        ]):
            try:
                dados_filial = pedidos_filial_na_data(cursor, fantasia=fantasia)
            except KeyError:
                dados_filial = None

        ops_tecidos = []
        for row in o_data:
            if row['QTD_ROLOS_ALOC'] != 0:
                ops_tecidos.append(row['ORDEM_PRODUCAO'])
            row['ORDEM_PRODUCAO|LINK'] = reverse(
                'producao:op__get', args=[row['ORDEM_PRODUCAO']])
            row['REFERENCIA_PECA|LINK'] = reverse(
                'produto:ref__get', args=[row['REFERENCIA_PECA']])
            if row['ORDEM_PRINCIPAL'] == 0:
                row['ORDEM_PRINCIPAL'] == ''
            else:
                row['ORDEM_PRINCIPAL|LINK'] = reverse(
                    'producao:op__get', args=[row['ORDEM_PRINCIPAL']])
            row['DT_DIGITACAO'] = row['DT_DIGITACAO'].date()
            if row['DT_CORTE'] is None:
                row['DT_CORTE'] = '-'
            else:
                row['DT_CORTE'] = row['DT_CORTE'].date()
            if row['SITUACAO'] == 9:
                row['SITUACAO'] = 'Cancelada'
            else:
                row['SITUACAO'] = 'Ativa'

            row['NF_FILIAL'] = '-'
            if row['TEM_15'] and dados_filial:
                for nf in dados_filial:
                    op_match = re.findall('OP\(([^\)]+)\)', nf['obs'])
                    if not op_match:
                        continue
                    ops = set().union(*[
                        op_str.split(', ')
                        for op_str in op_match
                    ])
                    if f"{row['ORDEM_PRODUCAO']}" in ops:
                        row['NF_FILIAL'] = nf['nf'] if nf['nf'] else '-'
                        break
            if row['NF_FILIAL'] != '-':
                row['NF_FILIAL|TARGET'] = "_blank"
                row['NF_FILIAL|LINK'] = reverse(
                    'contabil:nota_fiscal__get',
                    args=['3', row['NF_FILIAL']],
                )

            if row['TEM_15']:
                row['TEM_15'] = 'S'
            else:
                row['TEM_15'] = 'N'

        self.context.update({
            'o_dados': {
                'headers': (
                    'Stuação', 'OP', 'Tipo', 'Referência',
                    'OP principal', 'Quantidade', 'Data Digitação', 'Data Corte',
                    'Tem est. 15?', 'Qtd.rolos', 'NF filial'
                ),
                'fields': (
                    'SITUACAO', 'ORDEM_PRODUCAO', 'TIPO', 'REFERENCIA_PECA',
                    'ORDEM_PRINCIPAL', 'QTD', 'DT_DIGITACAO', 'DT_CORTE',
                    'TEM_15', 'QTD_ROLOS_ALOC', 'NF_FILIAL'
                ),
                'data': o_data,
                'titulo': "OP do pedido",
            },
        })

        # NF de compra de tecido
        self.context['ops_tecidos'] = ops_tecidos
        if ops_tecidos:
            nft_data = ped_nf_rolos.query(cursor, ops_tecidos)
            for row in nft_data:
                row['op|TARGET'] = '_blank'
                row['op|LINK'] = reverse(
                    'producao:op__get',
                    args=[row['op']],
                )
                row['nf|TARGET'] = '_blank'
                row['nf|LINK'] = reverse(
                    'contabil:nf_recebida__get',
                    args=[
                        '1',
                        row['nf_num'],
                        row['nf_ser'],
                        row['cnpj_num']
                    ],
                )
            self.context.update({
                'nft_headers': [
                    'OP',
                    'NF',
                    'Fornecedor',
                    'Item',
                    'Descrição',
                    'Rolos',
                    'Peso utilizado',
                ],
                'nft_fields': [
                    'op',
                    'nf',
                    'cnpj_forn',
                    'item',
                    'item_descr',
                    'rolos',
                    'qtd',
                ],
                'nft_data': nft_data,
            })

        # NFs
        nf_data = queries.pedido.ped_nf(cursor, pedido, especiais=True, empresa=empresa)
        for row in nf_data:
            row['NF|LINK'] = reverse(
                'contabil:nota_fiscal__get',
                args=[row['CODIGO_EMPRESA'], row['NF']],
            )
            if row['SITUACAO'] == 1:
                row['SITUACAO'] = 'Ativa'
            else:
                row['SITUACAO'] = 'Cancelada'

            if row['NF_DEVOLUCAO'] is None:
                row['NF_DEVOLUCAO'] = '-'
            else:
                row['SITUACAO'] += '/Devolvida'

        self.context.update({
            'nf_headers': (
                'Empresa',
                'NF',
                'Data',
                'Situação',
                'Valor',
                'NF Devolução',
            ),
            'nf_fields': (
                'CODIGO_EMPRESA',
                'NF',
                'DATA',
                'SITUACAO',
                'VALOR',
                'NF_DEVOLUCAO',
            ),
            'nf_data': nf_data,
        })

        # Grade
        g_header, g_fields, g_data, g_style, g_total = \
            queries.pedido.sortimento(
                cursor,
                pedido=pedido,
                total='Total',
                empresa=empresa,
            )
        if len(g_data) != 0:
            for i in range(1, len(g_fields)):
                i_column = i + 1
                g_style[i_column] = g_style[i_column] + \
                    'border-left-style: solid;' \
                    'border-left-width: thin;' \
                    'text-align: right;'

            self.context.update({
                'g_headers': g_header,
                'g_fields': g_fields,
                'g_data': g_data,
                'g_style': g_style,
                'g_total': g_total,
            })


    def get(self, request, *args, **kwargs):
        self.set_context(request)
        if 'pedido' in kwargs:
            return self.post(request, *args, **kwargs)
        else:
            form = self.Form_class()
            self.context['form'] = form
            return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.set_context(request)
        form = self.Form_class(request.POST)
        form.data = form.data.copy()
        if 'pedido' in kwargs:
            form.data['pedido'] = kwargs['pedido']
        if form.is_valid():
            pedido = form.cleaned_data['pedido']
            cursor = db_cursor_so(request)
            self.mount_context(cursor, pedido)
        self.context['form'] = form
        return render(request, self.template_name, self.context)
