from pprint import pprint

from django.views import View

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

import produto.queries

import comercial.forms as forms
import comercial.queries as queries


class VendasPor(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(VendasPor, self).__init__(*args, **kwargs)
        self.Form_class = forms.VendasPorForm
        self.template_name = 'comercial/vendas_por.html'
        self.get_args = ['ref']
        self.title_name = '?'
        self.por = '?'
        self.por_name = '?'

    def mount_context(self):
        # cliente = self.form.cleaned_data['cliente']
        self.ref = self.form.cleaned_data['ref']
        self.context.update({
            # 'cliente': cliente,
            'ref': self.ref,
        })
        self.cursor = db_cursor_so(self.request)

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

        self.periodos = ['3:', '6:', '12:', '24:']
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


class VendasPorCor(VendasPor):

    def __init__(self, *args, **kwargs):
        super(VendasPorCor, self).__init__(*args, **kwargs)
        self.title_name = 'Distribuição de vendas por cor'
        self.por = 'cor'
        self.por_name = 'Cor'


class VendasPorTamanho(VendasPor):

    def __init__(self, *args, **kwargs):
        super(VendasPorTamanho, self).__init__(*args, **kwargs)
        self.title_name = 'Distribuição de vendas por tamanho'
        self.por = 'tam'
        self.por_name = 'Tamanho'


class Vendas(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Vendas, self).__init__(*args, **kwargs)
        self.Form_class = forms.VendasForm
        self.template_name = 'comercial/vendas.html'
        self.title_name = 'Vendas'

    def mount_context(self):
        ref = self.form.cleaned_data['ref']
        if ref == '':
            ref = None

        cursor = db_cursor_so(self.request)

        periodo_cols = {
            'meses3': '3:0',
            'anos2': '24:',
        }

        av = queries.AnaliseVendas(
            cursor, ref=ref, por='qtd_ref', periodo_cols=periodo_cols)
        data = av.data

        self.context.update({
            'headers': ['Referência', 'Quantidade'],
            'fields': ['ref', 'qtd'],
            'data': data,
        })
