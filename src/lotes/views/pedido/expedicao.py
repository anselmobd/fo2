from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from utils.table_defs import TableDefsHpSD
from utils.views import totalize_grouped_data, group_rowspan

from cd.queries.novo_modulo.solicitacoes import get_solicitacoes

import lotes.models as models
import lotes.queries as queries
from lotes.forms.expedicao import ExpedicaoForm


class Expedicao(View):

    def __init__(self):
        super().__init__()
        self.Form_class = ExpedicaoForm
        self.template_name = 'lotes/expedicao.html'
        self.title_name = 'Expedição'

    def mount_grade(self):
        data = queries.pedido.grade_expedicao(
            self.cursor,
            embarque_de=self.embarque_de,
            embarque_ate=self.embarque_ate,
            emissao_de=self.emissao_de,
            emissao_ate=self.emissao_ate,
            pedido_tussor=self.pedido_tussor,
            pedido_cliente=self.pedido_cliente,
            cliente=self.cliente,
            deposito=self.deposito,
            cancelamento=self.cancelamento,
            faturamento=self.faturamento,
            colecao=self.colecao_codigo,
        )
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Nada selecionado',
            })
            return

        referencia = None
        grade = []
        quant = 0
        data_refs = []
        data.append({
            'REF': 'ZZZZZ',
            'COR': '-',
            'TAM': '-',
            'QTD': 0,
        })
        qtd_total = 0
        for row in data:
            qtd_total += row['QTD']
            if referencia is not None and referencia != row['REF']:
                grade.append({
                    'tam': '',
                    'cor': 'Total',
                    'qtd': quant,
                    '|STYLE': 'font-weight: bold;'
                })
                data_refs.append({
                    'ref': referencia,
                    'grade': {
                        'headers': ['Tamanho', 'Cor', 'Quantidade'],
                        'fields': ['tam', 'cor', 'qtd'],
                        'data': grade,
                        'style': {3: 'text-align: right;'},
                    }
                })
                grade = []
                quant = 0
            grade.append({
                'tam': row['TAM'],
                'cor': row['COR'],
                'qtd': row['QTD'],
            })
            quant += row['QTD']
            referencia = row['REF']
        self.context.update({
            'data_refs': data_refs,
            'qtd_total': qtd_total,
        })

    def cliente_info_ul(self, icone, info):
        return f"""
            <ul style=\"list-style-type: '{icone}'; margin-bottom: 0px;\">
                <li>{info}</li>
            </ul>
        """

    def mount_pedidos(self):
        data = queries.pedido.ped_expedicao(
            self.cursor,
            embarque_de=self.embarque_de,
            embarque_ate=self.embarque_ate,
            emissao_de=self.emissao_de,
            emissao_ate=self.emissao_ate,
            pedido_tussor=self.pedido_tussor,
            pedido_cliente=self.pedido_cliente,
            cliente=self.cliente,
            detalhe=self.detalhe,
            deposito=self.deposito,
            cancelamento=self.cancelamento,
            faturamento=self.faturamento,
            colecao=self.colecao_codigo,
        )
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Nada selecionado',
            })
            return

        table_defs = TableDefsHpSD(
            {
                'PEDIDO_VENDA': ['Pedido Tussor'],
                'AGRUPADOR': [],
                'SOLICITACAO': ['Solicitação'],
                'GTIN_OK': ['GTIN OK'],
                'PEDIDO_CLIENTE': ['Pedido cliente'],
                'DT_EMISSAO': ['Data emissão'],
                'DT_EMBARQUE': ['Data embarque'],
                'CLIENTE': ['Cliente'],
                'CLIENTE_INFO': [
                    '\N{department store}Cliente / '
                    '\N{memo}Observação / '
                    '\N{scroll}Referências'
                ],
                'OP': ['OP'],
                'REF': ['Referência'],
                'COR': ['Cor'],
                'TAM': ['Tamanho'],
                'QTD': ['Quant.', 'r'],
                'VALOR': ['Valor', 'r', 2],
            },
        )

        field_lists = {
            'r': [
                'PEDIDO_VENDA',
                'SOLICITACAO',
                'PEDIDO_CLIENTE',
                'DT_EMISSAO',
                'DT_EMBARQUE',
                'CLIENTE',
                'REF',
                'QTD',
            ],
            'c': [
                'PEDIDO_VENDA',
                'SOLICITACAO',
                'PEDIDO_CLIENTE',
                'DT_EMISSAO',
                'DT_EMBARQUE',
                'CLIENTE',
                'REF',
                'COR',
                'TAM',
                'QTD',
            ],
            'p': [
                'PEDIDO_VENDA',
                'SOLICITACAO',
                'GTIN_OK',
                'PEDIDO_CLIENTE',
                'DT_EMISSAO',
                'DT_EMBARQUE',
                'CLIENTE',
                'QTD',
                'VALOR',
            ],
            'o': [
                'PEDIDO_VENDA',
                'AGRUPADOR',
                'SOLICITACAO',
                'PEDIDO_CLIENTE',
                'DT_EMISSAO',
                'DT_EMBARQUE',
                'CLIENTE_INFO',
                'OP',
                'QTD',
            ],
        }

        pedidos = list(set([
            row['PEDIDO_VENDA']
            for row in data
        ]))

        solict_pedidos = {}
        s_dados = get_solicitacoes(self.cursor, pedido_destino=pedidos)
        for row in s_dados:
            pedidos_destino_list = map(
                str.strip,
                row['pedidos_destino'].split(',')
            )
            for pedido in pedidos_destino_list:
                ped = int(pedido)
                if ped not in solict_pedidos:
                    solict_pedidos[(ped)] = []
                solict_pedidos[ped].append(row['solicitacao'])

        for ped in solict_pedidos:
            solict_pedidos[ped] = ', '.join(map(str, solict_pedidos[ped]))

        qtd_total = 0
        for row in data:
            if row['PEDIDO_VENDA'] in solict_pedidos:
                num_solicit = solict_pedidos[row['PEDIDO_VENDA']]
                if ',' in num_solicit:
                    num_solicit_list = map(str.strip, num_solicit.split(','))
                else:
                    num_solicit_list = [num_solicit]
                link_sol_list = []
                for num_sol in num_solicit_list:
                    if num_sol == 'None':
                        num_sol = "#"
                        link = reverse(
                            'cd:novo_solicitacao',
                            args=["sn"],
                        )+f"?pedido={row['PEDIDO_VENDA']}"
                    else:
                        link = reverse(
                            'cd:novo_solicitacao',
                            args=[num_sol],
                        )
                    link_sol_list.append(
                        f'<a href="{link}" target="_blank">{num_sol}</a>'
                    )
                row['SOLICITACAO'] = ", ".join(link_sol_list)
            else:
                row['SOLICITACAO'] = '-'
            qtd_total += row['QTD']
            row['DT_EMISSAO'] = row['DT_EMISSAO'].date()
            row['DT_EMBARQUE'] = row['DT_EMBARQUE'].date()
            row['PEDIDO_VENDA|LINK'] = reverse(
                'producao:pedido__get', args=[row['PEDIDO_VENDA']])
            if self.detalhe == 'p':
                if row['GTIN_OK'] == 'S':
                    row['GTIN_OK'] = 'Sim'
                else:
                    row['GTIN_OK'] = 'Não'
            if self.detalhe == 'o':
                if row['AGRUPADOR'] == 0:
                    row['AGRUPADOR'] = '-'
                else:
                    row['AGRUPADOR'] = f"{999000000+row['AGRUPADOR']}"
                o_data = queries.pedido.ped_op(self.cursor, row['PEDIDO_VENDA'])
                ops = []
                for o_row in o_data:
                    if o_row['SITUACAO'] != 9:
                        ops.append(o_row['ORDEM_PRODUCAO'])
                row['OP'] = []
                for op in sorted(ops):
                    link = reverse(
                        'producao:op__get', args=[op])
                    row['OP'].append(f'<a href="{link}" target="_blank">{op}</a>')
                if row['OP']:
                    row['OP'] = ', '.join(map(str, sorted(row['OP'])))
                else:
                    row['OP'] = '-'

                r_data = queries.pedido.referencias.query(self.cursor, row['PEDIDO_VENDA'])
                if r_data:
                    referencias = ', '.join([r['ref'] for r in r_data])
                else:
                    referencias = '-'

                cliente_html = self.cliente_info_ul(
                    "\N{department store}", row['CLIENTE'])
                obs_html = self.cliente_info_ul(
                    "\N{memo}", row['OBSERVACAO']) if row['OBSERVACAO'] else ''
                referencias_html = self.cliente_info_ul(
                    "\N{scroll}", referencias)
                row['CLIENTE_INFO'] = f"{cliente_html}{obs_html}{referencias_html}"

        if self.detalhe not in ['p', 'o']:
            group = ['PEDIDO_VENDA', 'SOLICITACAO', 'PEDIDO_CLIENTE',
                     'DT_EMISSAO', 'DT_EMBARQUE',
                     'CLIENTE']
            totalize_grouped_data(data, {
                'group': group,
                'sum': ['QTD'],
                'descr': {'REF': 'Total:'},
            })
            group_rowspan(data, group)
            self.context.update({
                'group': group,
            })

        table_defs.hfsd_dict_context(
            self.context, *field_lists[self.detalhe])
        self.context.update({
            'safe': [
                'SOLICITACAO',
                'CLIENTE_INFO',
                'OP',
            ],
            'data': data,
            'qtd_total': qtd_total,
        })

    def mount_context(self):
        self.context.update({
            'embarque_de': self.embarque_de,
            'embarque_ate': self.embarque_ate,
            'emissao_de': self.emissao_de,
            'emissao_ate': self.emissao_ate,
            'pedido_tussor': self.pedido_tussor,
            'pedido_cliente': self.pedido_cliente,
            'cliente': self.cliente,
            'detalhe': self.detalhe,
            'deposito': self.deposito,
            'cancelamento': self.cancelamento,
            'faturamento': self.faturamento,
            'colecao': self.colecao,
        })

        self.colecao_codigo = None if self.colecao is None else self.colecao.colecao

        if self.detalhe == 'g':
            self.mount_grade()
        else:
            self.mount_pedidos()

    def get(self, request, *args, **kwargs):
        self.context = {'titulo': self.title_name}
        if 'pedido_cliente' in kwargs:
            self.cursor = db_cursor_so(request)
            self.embarque_de = None
            self.embarque_ate = None
            self.emissao_de = None
            self.emissao_ate = None
            self.pedido_tussor = ''
            self.pedido_cliente = kwargs['pedido_cliente']
            self.cliente = kwargs['cliente']
            self.deposito = '-'
            self.detalhe = 'o'
            self.cancelamento = '-'
            self.faturamento = '-'
            self.colecao = None
            self.mount_context()
            form = self.Form_class(
                initial={
                    'embarque_de': self.embarque_de,
                    'embarque_ate': self.embarque_ate,
                    'emissao_de': self.emissao_de,
                    'emissao_ate': self.emissao_ate,
                    'pedido_tussor': self.pedido_tussor,
                    'pedido_cliente': self.pedido_cliente,
                    'cliente': self.cliente,
                    'deposito': self.deposito,
                    'detalhe': self.detalhe,
                    'cancelamento': self.cancelamento,
                    'faturamento': self.faturamento,
                    'colecao': self.colecao,
                }
            )
        else:
            form = self.Form_class()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        self.context = {'titulo': self.title_name}
        form = self.Form_class(request.POST)
        if form.is_valid():
            self.embarque_de = form.cleaned_data['embarque_de']
            self.embarque_ate = form.cleaned_data['embarque_ate']
            self.emissao_de = form.cleaned_data['emissao_de']
            self.emissao_ate = form.cleaned_data['emissao_ate']
            self.pedido_tussor = form.cleaned_data['pedido_tussor']
            self.pedido_cliente = form.cleaned_data['pedido_cliente']
            self.cliente = form.cleaned_data['cliente']
            self.deposito = form.cleaned_data['deposito']
            self.detalhe = form.cleaned_data['detalhe']
            self.cancelamento = form.cleaned_data['cancelamento']
            self.faturamento = form.cleaned_data['faturamento']
            self.colecao = form.cleaned_data['colecao']
            self.cursor = db_cursor_so(request)
            self.mount_context()
        self.context['form'] = form
        return render(request, self.template_name, self.context)
