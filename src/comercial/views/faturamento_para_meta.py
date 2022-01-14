import datetime
from pprint import pprint

from django.shortcuts import render
from django.views import View

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.functions import dias_mes_data
from utils.functions.models import queryset_to_dict_list_lower
from utils.views import totalize_data

import lotes.queries.pedido as l_q_p

import comercial.forms
import comercial.models
import comercial.queries


class FaturamentoParaMeta(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(FaturamentoParaMeta, self).__init__(*args, **kwargs)
        self.Form_class = comercial.forms.FaturamentoParaMetaForm
        self.template_name = 'comercial/faturamento_para_meta.html'
        self.title_name = 'Faturamento no mês'

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        ano = self.form.cleaned_data['ano']
        mes = self.form.cleaned_data['mes']
        ref = self.form.cleaned_data['ref']
        colecao = self.form.cleaned_data['colecao']
        cliente = self.form.cleaned_data['cliente']
        apresentacao = self.form.cleaned_data['apresentacao']
        ordem = self.form.cleaned_data['ordem']

        colecao_codigo = None if colecao is None else colecao.colecao

        percentual = (
            ordem == 'valor' and
            apresentacao in ['cliente', 'referencia', 'modelo']
        )

        if ano is None:
            hoje = datetime.date.today()
            ano_atual = hoje.year
        else:
            ano_atual = ano

        self.context.update({
            'ano': ano_atual,
            'mes': mes,
            'ref': ref,
            'colecao': colecao,
            'colecao_codigo': colecao_codigo,
            'cliente': cliente,
        })

        faturados = comercial.queries.faturamento_para_meta(
            cursor, ano_atual, mes, ref=ref, cliente=cliente,
            tipo=apresentacao, ordem=ordem, colecao=colecao_codigo)

        if len(faturados) == 0:
            self.context.update({
                'msg_erro': 'Nenhum faturamento encontrado',
            })
            return

        totalize_data(faturados, {
            'sum': ['qtd', 'valor'],
            'descr': {'cliente': 'Total:'},
            'row_style': 'font-weight: bold;',
        })

        valor_total = faturados[-1]['valor']
        participacao_acumulada = 0
        for idx, faturado in enumerate(faturados):
            if percentual:
                faturado['percent'] = faturado['valor'] / valor_total * 100
                faturado['percent|DECIMALS'] = 1
                participacao_acumulada += faturado['valor']
                faturado['acumulada'] = participacao_acumulada / valor_total * 100
                faturado['acumulada|DECIMALS'] = 1
                if (idx + 1) < len(faturados):
                    faturado['idx'] = idx + 1
                else:
                    faturado['idx'] = ' '
            faturado['valor|DECIMALS'] = 2
            if apresentacao in ['nota', 'nota_referencia']:
                faturado['cfop'] = f"{faturado['nat']}{faturado['div']}"
                if (idx + 1) < len(faturados):
                    if not faturado['pedido']:
                        faturado['pedido'] = '-'
                    if not faturado['pedido_cliente']:
                        faturado['pedido_cliente'] = '-'

        tabela = {
            'mes': {
                'headers': [
                    'Mês', 'Valor',
                ],
                'fields': [
                    'mes', 'valor',
                ],
                'style': {
                    2: 'text-align: right;',
                },
            },
            'nota': {
                'headers': [
                    'Nota', 'Data', 'CFOP', 'Cliente',
                    'Pedido', 'Pedido cliente', 'Valor',
                ],
                'fields': [
                    'nf', 'data', 'cfop', 'cliente',
                    'pedido', 'pedido_cliente', 'valor',
                ],
                'style': {
                    7: 'text-align: right;',
                },
            },
            'nota_referencia': {
                'headers': [
                    'Nota', 'Data', 'CFOP', 'Cliente',
                    'Pedido', 'Pedido cliente',
                    'Referência', 'Quantidade', 'Valor',
                ],
                'fields': [
                    'nf', 'data', 'cfop', 'cliente',
                    'pedido', 'pedido_cliente',
                    'ref', 'qtd', 'valor',
                ],
                'style': {
                    8: 'text-align: right;',
                    9: 'text-align: right;',
                },
            },
            'cliente': {
                'headers': ['Cliente', 'Valor', ],
                'fields': ['cliente', 'valor', ],
                'style': {
                    2: 'text-align: right;',
                },
            },
            'cliente_percentual': {
                'headers': ['Cliente', 'Valor', 'Participação(%)', 'Acumulada(%)', '#'],
                'fields': ['cliente', 'valor', 'percent', 'acumulada', 'idx'],
                'style': {
                    2: 'text-align: right;',
                    3: 'text-align: right;',
                    4: 'text-align: right;',
                    5: 'text-align: right;',
                },
            },
            'referencia': {
                'headers': ['Referencia', 'Coleção', 'Valor', ],
                'fields': ['ref', 'colecao', 'valor', ],
                'data': faturados,
                'style': {
                    3: 'text-align: right;',
                },
            },
            'referencia_percentual': {
                'headers': ['Referencia', 'Coleção', 'Valor', 'Participação(%)', 'Acumulada(%)', '#'],
                'fields': ['ref', 'colecao', 'valor', 'percent', 'acumulada', 'idx'],
                'data': faturados,
                'style': {
                    3: 'text-align: right;',
                    4: 'text-align: right;',
                    5: 'text-align: right;',
                    6: 'text-align: right;',
                },
            },
            'modelo': {
                'headers': ['Modelo', 'Coleção', 'Valor', ],
                'fields': ['modelo', 'colecao', 'valor', ],
                'data': faturados,
                'style': {
                    3: 'text-align: right;',
                },
            },
            'modelo_percentual': {
                'headers': ['Modelo', 'Coleção', 'Valor', 'Participação(%)', 'Acumulada(%)', '#'],
                'fields': ['modelo', 'colecao', 'valor', 'percent', 'acumulada', 'idx'],
                'data': faturados,
                'style': {
                    3: 'text-align: right;',
                    4: 'text-align: right;',
                    5: 'text-align: right;',
                    6: 'text-align: right;',
                },
            },
        }

        if percentual:
            apresentacao += '_percentual'

        headers = tabela[apresentacao]['headers']
        fields = tabela[apresentacao]['fields']
        style = tabela[apresentacao]['style']

        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': faturados,
            'style': style,
        })
