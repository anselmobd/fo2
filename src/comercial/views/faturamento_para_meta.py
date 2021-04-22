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
        apresentacao = self.form.cleaned_data['apresentacao']
        ordem = self.form.cleaned_data['ordem']

        percentual = (
            ordem == 'valor' and
            apresentacao in ['cliente', 'referencia', 'modelo']
        )

        if ano is None or mes is None:
            hoje = datetime.date.today()
            ano_atual = hoje.year
            mes_atual = hoje.month
        else:
            ano_atual = ano
            mes_atual = mes

        self.context.update({
            'ano': ano_atual,
            'mes': mes_atual,
        })

        faturados = comercial.queries.faturamento_para_meta(
            cursor, ano_atual, mes_atual, tipo=apresentacao, ref=ref, ordem=ordem)

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
            'referencia': {
                'headers': ['Referencia', 'Valor', ],
                'fields': ['ref', 'valor', ],
                'data': faturados,
                'style': {
                    2: 'text-align: right;',
                },
            },
            'modelo': {
                'headers': ['Modelo', 'Valor', ],
                'fields': ['modelo', 'valor', ],
                'data': faturados,
                'style': {
                    2: 'text-align: right;',
                },
            },
        }

        headers = tabela[apresentacao]['headers']
        fields = tabela[apresentacao]['fields']
        style = tabela[apresentacao]['style']
        if percentual:
            headers += ['Participação(%)', 'Acumulada(%)', '#']
            fields += ['percent', 'acumulada', 'idx']
            style.update({
                3: 'text-align: right;',
                4: 'text-align: right;',
                5: 'text-align: right;',
            })

        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': faturados,
            'style': style,
        })
