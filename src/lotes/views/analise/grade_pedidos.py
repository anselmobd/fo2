from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.forms.forms2 import Forms2
from base.views import O2BaseGetPostView
from utils.views import totalize_data

from lotes.queries.pedido.pedido_faturavel_sortimento \
    import pedido_faturavel_sortimento


class GradePedidos(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(GradePedidos, self).__init__(*args, **kwargs)
        self.Form_class = Forms2().DepositoColecaoDatas
        self.template_name = 'lotes/analise/grade_pedidos.html'
        self.title_name = 'Grade de pedidos a embarcar'
        self.get_args = ['deposito']

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        deposito = self.form.cleaned_data['deposito']
        data_de = self.form.cleaned_data['data_de']
        data_ate = self.form.cleaned_data['data_ate']
        self.context.update({
            'deposito': deposito,
            'data_de': data_de,
            'data_ate': data_ate,
        })

        data = pedido_faturavel_sortimento(cursor, deposito, data_de, data_ate)
        if len(data) == 0:
            self.context.update({
                'msg_erro': 'Pedidos não encontrados',
            })
            return

        totalize_data(data, {
            'sum': ['qtd'],
            'descr': {'tam': 'Total:'},
            'row_style': 'font-weight: bold;',
        })

        self.context.update({
            'headers': ['Referência', 'Cor', 'Tamanho', 'Quantidade'],
            'fields': ['ref', 'cor', 'tam', 'qtd'],
            'data': data,
            'style': {
                4: 'text-align: right;',
            },
        })

        m_data = pedido_faturavel_sortimento(
            cursor, deposito, data_de, data_ate, retorno='m')

        totalize_data(m_data, {
            'sum': ['qtd'],
            'descr': {'modelo': 'Total:'},
            'row_style': 'font-weight: bold;',
        })

        self.context.update({
            'm_headers': ['Modelo', 'Quantidade'],
            'm_fields': ['modelo', 'qtd'],
            'm_data': m_data,
            'm_style': {
                2: 'text-align: right;',
            },
        })

        p_data = pedido_faturavel_sortimento(
            cursor, deposito, data_de, data_ate, retorno='p')

        for row in p_data:
            row['data'] = row['data'].date()
            row['pedido|LINK'] = reverse(
                'producao:pedido__get', args=[row['pedido']])
            row['pedido|TARGET'] = '_BLANK'

            cnpj9 = row['cnpj9']
            cnpj4 = row['cnpj4']
            cnpj2 = row['cnpj2']
            nome = row['nome_cliente']
            row['cliente'] = f"{cnpj9}/{cnpj4}-{cnpj2} {nome}"

        totalize_data(p_data, {
            'sum': ['qtd'],
            'descr': {'pedido': 'Total:'},
            'row_style': 'font-weight: bold;',
        })

        self.context.update({
            'p_headers': ['Data de embarque', 'Pedido', 'Cliente', 'Quantidade'],
            'p_fields': ['data', 'pedido', 'cliente', 'qtd'],
            'p_data': p_data,
            'p_style': {
                4: 'text-align: right;',
            },
        })
