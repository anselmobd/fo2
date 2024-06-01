import datetime
from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from utils.views import totalize_data

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

        empresa = self.form.cleaned_data['empresa']
        ano = self.form.cleaned_data['ano']
        mes = self.form.cleaned_data['mes']
        ref = self.form.cleaned_data['ref']
        tamanho = self.form.cleaned_data['tamanho']
        cor = self.form.cleaned_data['cor']
        colecao = self.form.cleaned_data['colecao']
        cliente = self.form.cleaned_data['cliente']
        apresentacao = self.form.cleaned_data['apresentacao']
        ordem = self.form.cleaned_data['ordem']
        exclui = self.form.cleaned_data['exclui']

        colecao_codigo = None if colecao is None else colecao.colecao

        percentual = (
            ordem in ['valor', 'qtd'] and
            apresentacao in ['cliente', 'referencia', 'modelo', 'colecao']
        )

        if ano is None:
            hoje = datetime.date.today()
            ano_atual = hoje.year
        else:
            ano_atual = ano

        self.context.update({
            'empresa': dict(self.Form_class.empresa_choices)[empresa],
            'ano': ano_atual,
            'mes': mes,
            'ref': ref,
            'tamanho': tamanho,
            'cor': cor,
            'colecao': colecao,
            'colecao_codigo': colecao_codigo,
            'cliente': cliente,
            'apresentacao': dict(self.Form_class.base_fields['apresentacao'].choices)[apresentacao],
            'ordem': dict(self.Form_class.base_fields['ordem'].choices)[ordem],
            'exclui': dict(self.Form_class.base_fields['exclui'].choices)[exclui],
        })

        faturados = comercial.queries.faturamento_para_meta(
            cursor, ano_atual, mes, ref=ref, tamanho=tamanho, cor=cor, 
            cliente=cliente, tipo=apresentacao, ordem=ordem,
            colecao=colecao_codigo, verifica_devolucao=exclui=='devolvidas',
            empresa=empresa)

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

        if percentual:
            valor_total = faturados[-1][ordem]
        participacao_acumulada = 0
        for idx, faturado in enumerate(faturados):
            if percentual:
                faturado['percent'] = faturado[ordem] / valor_total * 100
                faturado['percent|DECIMALS'] = 1
                participacao_acumulada += faturado[ordem]
                faturado['acumulada'] = participacao_acumulada / valor_total * 100
                faturado['acumulada|DECIMALS'] = 1
                if (idx + 1) < len(faturados):
                    faturado['idx'] = idx + 1
                else:
                    faturado['idx'] = ' '
                    faturado['acumulada'] = ' '
            faturado['qtd|DECIMALS'] = 2
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
                'headers': ['Cliente', 'Quantidade', 'Valor', ],
                'fields': ['cliente', 'qtd', 'valor', ],
                'style': {
                    2: 'text-align: right;',
                    3: 'text-align: right;',
                },
            },
            'cliente_percentual': {
                'headers': ['Cliente', 'Quantidade', 'Valor', 'Participação(%)', 'Acumulada(%)', '#'],
                'fields': ['cliente', 'qtd', 'valor', 'percent', 'acumulada', 'idx'],
                'style': {
                    2: 'text-align: right;',
                    3: 'text-align: right;',
                    4: 'text-align: right;',
                    5: 'text-align: right;',
                    6: 'text-align: right;',
                },
            },
            'referencia': {
                'headers': ['Referencia', 'Coleção', 'Quantidade', 'Valor', ],
                'fields': ['ref', 'colecao', 'qtd', 'valor', ],
                'data': faturados,
                'style': {
                    3: 'text-align: right;',
                    4: 'text-align: right;',
                },
            },
            'referencia_percentual': {
                'headers': ['Referencia', 'Coleção', 'Quantidade', 'Valor', 'Participação(%)', 'Acumulada(%)', '#'],
                'fields': ['ref', 'colecao', 'qtd', 'valor', 'percent', 'acumulada', 'idx'],
                'data': faturados,
                'style': {
                    3: 'text-align: right;',
                    4: 'text-align: right;',
                    5: 'text-align: right;',
                    6: 'text-align: right;',
                    7: 'text-align: right;',
                },
            },
            'modelo': {
                'headers': ['Modelo', 'Coleção', 'Quantidade', 'Valor', ],
                'fields': ['modelo', 'colecao', 'qtd', 'valor', ],
                'data': faturados,
                'style': {
                    3: 'text-align: right;',
                    4: 'text-align: right;',
                },
            },
            'modelo_percentual': {
                'headers': ['Modelo', 'Coleção', 'Quantidade', 'Valor', 'Participação(%)', 'Acumulada(%)', '#'],
                'fields': ['modelo', 'colecao', 'qtd', 'valor', 'percent', 'acumulada', 'idx'],
                'data': faturados,
                'style': {
                    3: 'text-align: right;',
                    4: 'text-align: right;',
                    5: 'text-align: right;',
                    6: 'text-align: right;',
                    7: 'text-align: right;',
                },
            },
            'colecao': {
                'headers': ['Coleção', 'Quantidade', 'Valor', ],
                'fields': ['colecao', 'qtd', 'valor', ],
                'data': faturados,
                'style': {
                    2: 'text-align: right;',
                    3: 'text-align: right;',
                },
            },
            'colecao_percentual': {
                'headers': ['Coleção', 'Quantidade', 'Valor', 'Participação(%)', 'Acumulada(%)', '#'],
                'fields': ['colecao', 'qtd', 'valor', 'percent', 'acumulada', 'idx'],
                'data': faturados,
                'style': {
                    2: 'text-align: right;',
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

        if 'pedido' in fields:
            for row in faturados:
                if row['pedido'] and row['pedido'] != '-':
                    row['pedido|TARGET'] = '_blank'
                    row['pedido|LINK'] = reverse(
                        'producao:pedido__get',
                        args=[row['pedido']],
                    )

        self.context.update({
            'headers': headers,
            'fields': fields,
            'data': faturados,
            'style': style,
        })
