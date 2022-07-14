from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from base.views import O2BaseGetPostView
from utils.functions import untuple_keys_concat
from utils.functions.strings import (
    min_max_string,
    noneifempty,
    only_digits,
)
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
                args = [row['solicitacao']]
            else:
                row['solicitacao'] = '#'
                args = ['sn']
            get_filtro = []
            if self.pedido_destino:
                get_filtro.append(
                    f"pedido={self.pedido_destino}"
                )
            if self.ref_destino:
                get_filtro.append(
                    f"ref_destino={self.ref_destino}"
                )
            if self.ref_reservada:
                get_filtro.append(
                    f"ref_reservada={self.ref_reservada}"
                )
            if self.lote:
                get_filtro.append(
                    f"lote={self.lote}"
                )
            if self.op:
                get_filtro.append(
                    f"op={self.op}"
                )
            url_filtro = '&'.join(get_filtro)
            if url_filtro:
                url_filtro = f"?{url_filtro}"
            row['solicitacao|LINK'] = reverse(
                'cd:novo_solicitacao',
                args=args
            ) + url_filtro
            row['solicitacao|TARGET'] = '_blank'
            row['inclusao'] = row['inclusao'].strftime("%d/%m/%y %H:%M")

        form_report_lines = []
        
        filtro = min_max_string(
            self.com_lotes_situacao_de,
            self.com_lotes_situacao_ate,
            process_input=(
                only_digits,
                noneifempty,
            ),
            msg_format="Com lotes em situação {}",
        )
        if filtro:
            form_report_lines.append(filtro)

        fields = {
            'solicitacao': 'Solicitação',
            'lt': 'Tot.L.',
            'qt': 'Tot.Q.',
            'l1': '1 L.',
            'q1': '1 Q.',
            'l2': '2 L.',
            'q2': '2 Q.',
            'l3': '3 L.',
            'q3': '3 Q.',
            'l4': '4 L.',
            'q4': '4 Q.',
            'l5': '5 L.',
            'q5': '5 Q.',
            'lp': 'Prod.L.',
            'qp': 'Prod.Q.',
            'lf': 'Fin.L.',
            'qf': 'Fin.Q.',
            'inclusao': 'Inclusão',
            # 'pedidos_destino': 'Peds.Dest.',
        }
        self.context.update({
            'headers': fields.values(),
            'fields': fields.keys(),
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
