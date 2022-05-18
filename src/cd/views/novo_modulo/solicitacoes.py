from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetPostView
from utils.functions import untuple_keys_concat
from utils.views import totalize_data

import cd.forms
from cd.queries.novo_modulo.solicitacoes import get_solicitacoes


class Solicitacoes(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Solicitacoes, self).__init__(*args, **kwargs)
        self.Form_class = cd.forms.SolicitacoesForm
        self.cleaned_data2self = True
        self.cleaned_data2data = True
        self.template_name = 'cd/novo_modulo/solicitacoes.html'
        self.title_name = 'Solicitações'

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        data = get_solicitacoes(
            cursor,
            self.solicitacao,
            self.pedido_destino,
            self.ref_destino,
            self.ref_reservada,
            self.lote,
            self.op,
            self.situacao,
            desc=True,
        )

        qtd_solicit = len(data)
        totalize_data(data, {
            'sum': [
                'l1',
                'q1',
                'l2',
                'q2',
                'l3',
                'q3',
                'l4',
                'q4',
                'l5',
                'q5',
                'lp',
                'qp',
                'lf',
                'qf',
                'lt',
                'qt',
            ],
            'count': [],
            'descr': {'solicitacao': 'Totais:'},
            'row_style': 'font-weight: bold;',
            'flags': ['NO_TOT_1'],
        })

        data = paginator_basic(data, 20, self.page)

        for row in data:
            if row['solicitacao']:
                if row['solicitacao'] == 'Totais:':
                    continue
                row['solicitacao|LINK'] = reverse(
                    'cd:novo_solicitacao',
                    args=[row['solicitacao']]
                )
            else:
                if self.pedido_destino:
                    row['solicitacao'] = 'Sem Número'
                    row['solicitacao|LINK'] = reverse(
                        'cd:novo_solicitacao',
                        args=['-']
                    )+f"?pedido={self.pedido_destino}"
            row['solicitacao|TARGET'] = '_blank'
            row['inclusao'] = row['inclusao'].strftime("%d/%m/%y %H:%M")

        self.context.update({
            'headers': [
                'Solicitação',
                'Tot.L.',
                'Tot.Q.',
                '1 L.',
                '1 Q.',
                '2 L.',
                '2 Q.',
                '3 L.',
                '3 Q.',
                '4 L.',
                '4 Q.',
                '5 L.',
                '5 Q.',
                'Prod.L.',
                'Prod.Q.',
                'Fin.L.',
                'Fin.Q.',
                'Inclusão',
                # 'Peds.Dest.',
            ],
            'fields': [
                'solicitacao',
                'lt',
                'qt',
                'l1',
                'q1',
                'l2',
                'q2',
                'l3',
                'q3',
                'l4',
                'q4',
                'l5',
                'q5',
                'lp',
                'qp',
                'lf',
                'qf',
                'inclusao',
                # 'pedidos_destino',
            ],
            'style': untuple_keys_concat({
                tuple(range(2, 19)): 'text-align: right;',
            }),
            'data': data,
            'qtd_solicit': qtd_solicit,
        })
