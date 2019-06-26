from pprint import pprint

from django.db import connections
from django.views import View

from base.views import O2BaseGetPostView

import produto.queries

import comercial.forms as forms
import comercial.queries as queries


class VendasPorCor(O2BaseGetPostView):
    def __init__(self, *args, **kwargs):
        super(VendasPorCor, self).__init__(*args, **kwargs)
        self.Form_class = forms.VendasPorCorForm
        self.template_name = 'comercial/vendas_cor.html'
        self.title_name = 'Distribuição de vendas por cor'
        self.get_args = ['ref']
        self.por = 'cor'
        self.por_name = 'Cor'

    def mount_context(self):
        # cliente = self.form.cleaned_data['cliente']
        self.ref = self.form.cleaned_data['ref']
        self.context.update({
            # 'cliente': cliente,
            'ref': self.ref,
        })
        self.cursor = connections['so'].cursor()

        descricao = ''
        codigo_colecao = ''
        colecao = ''
        cliente_cnpj9 = ''
        cliente = ''
        if self.ref != '':
            # Informações básicas
            data = produto.queries.ref_inform(self.cursor, self.ref)
            if len(data) == 0:
                self.context.update({
                    'msg_erro': 'Referência não encontrada',
                })
                return
            else:
                descricao = data[0]['DESCR']
                codigo_colecao = data[0]['CODIGO_COLECAO']
                colecao = data[0]['COLECAO']
                cliente_cnpj9 = data[0]['CNPJ9']
                cliente = data[0]['CLIENTE']
        self.context.update({
            'descricao': descricao,
            'colecao': colecao,
            'cliente': cliente,
        })

        self.periodos = ['3m+', '6m+', '12m+', '24m+']
        self.periodos_descr = ['3 meses', '6 meses', '1 ano', '2 anos']

        grades = []
        if self.ref == '':
            grades.append(self.get_grade())
        else:
            grades.append(self.get_grade(self.ref, nome='da referência'))
            grades.append(self.get_grade(
                self.ref, codigo_colecao, cliente_cnpj9,
                nome='da coleção para o cliente'))
        self.context.update({
            'grades': grades,
        })

    def get_grade(self, ref=None, colecao=None, cliente=None, nome=None):
        grade = {
            'nome': nome,
        }
        data = []
        zero_data_row = {p: 0 for p in self.periodos}
        total_data_row = zero_data_row.copy()
        for periodo in self.periodos:
            data_periodo = queries.get_vendas(
                self.cursor, ref=ref, periodo=periodo, colecao=colecao,
                cliente=cliente, por=self.por)
            for row in data_periodo:
                data_row = [dr for dr in data if dr[self.por] == row[self.por]]
                if len(data_row) == 0:
                    data.append({
                        self.por: row[self.por],
                        **zero_data_row
                    })
                    data_row = data[len(data)-1]
                else:
                    data_row = data_row[0]
                data_row[periodo] = row['qtd']
                total_data_row[periodo] += row['qtd']

        if len(data) == 0:
            grade.update({
                'msg_erro': 'Nenhuma venda encontrada',
            })
        else:
            for row in data:
                for periodo in self.periodos:
                    if total_data_row[periodo] > 0:
                        row[periodo] /= (total_data_row[periodo] / 100)
                    row['{}|DECIMALS'.format(periodo)] = 2

            grade.update({
                'headers': [self.por_name, *self.periodos_descr],
                'fields': [self.por, *self.periodos],
                'style': {
                    2: 'text-align: right;',
                    3: 'text-align: right;',
                    4: 'text-align: right;',
                    5: 'text-align: right;',
                },
                'data': data,
            })
        return grade
