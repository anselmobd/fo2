from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetView

from cd.queries.novo_modulo.solicitacoes import get_solicitacao


class Solicitacao(O2BaseGetView):

    def __init__(self, *args, **kwargs):
        super(Solicitacao, self).__init__(*args, **kwargs)
        self.template_name = 'cd/novo_modulo/solicitacao.html'
        self.title_name = 'Solicitação'
        self.get_args = ['solicitacao']
        self.get_args2context = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        data = get_solicitacao(cursor, self.context['solicitacao'])

        for row in data:
            if not row['codigo_estagio']:
                row['codigo_estagio'] = 'Finalizado'

        self.context.update({
            'headers': [
                'Situação',
                'Estágio',
                'OP',
                'OC',
                'Alter.',
                'Referência',
                'Tamanho',
                'Cor',
                'Quantidade',
                'Pedido destino',
                'OP destino',
            ],
            'fields': [
                'situacao',
                'codigo_estagio',
                'ordem_producao',
                'ordem_confeccao',
                'alter_destino',
                'grupo_destino',
                'sub_destino',
                'cor_destino',
                'qtde',
                'pedido_destino',
                'op_destino',
            ],
            'data': data,
        })
