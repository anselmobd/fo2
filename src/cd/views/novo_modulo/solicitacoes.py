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
        self.por_pagina = 20

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
            self.com_lotes_situacao_de,
            self.com_lotes_situacao_ate,
            # self.sem_lotes_situacao_de,
            # self.sem_lotes_situacao_ate,
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

        data = paginator_basic(data, self.por_pagina, self.page)

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

        form_report_lines = []
        
        min = self.com_lotes_situacao_de if self.com_lotes_situacao_de.isdigit() else None
        max = self.com_lotes_situacao_ate if self.com_lotes_situacao_ate.isdigit() else None
        if min or max:
            if min == max:
                filtro = f"igual a {min}"
            elif min and max:
                filtro = f"entre {min} e {max}"
            elif min:
                filtro = f"maior que {min}"
            elif max:
                filtro = f"menor que {max}"
            filtro = f"Com lotes em situação {filtro}"
            form_report_lines.append(filtro)

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
            'por_pagina': self.por_pagina,
            'form_report_excludes': [
                'com_lotes_situacao_de',
                'com_lotes_situacao_ate',
            ],
            'form_report_lines': form_report_lines,
        })
