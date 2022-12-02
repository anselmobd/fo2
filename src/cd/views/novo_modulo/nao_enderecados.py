from collections import namedtuple
from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from o2.views.base.get_post import O2BaseGetPostView
from utils.functions.strings import (
    min_max_string,
    noneifempty,
    only_digits,
)
from utils.table_defs import TableDefs

from cd.queries.novo_modulo import nao_enderecados
from cd.forms import NaoEnderecadosForm

class NaoEnderecados(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(NaoEnderecados, self).__init__(*args, **kwargs)
        self.Form_class = NaoEnderecadosForm
        self.form_class_has_initial = True
        self.cleaned_data2self = True
        self.template_name = 'cd/novo_modulo/nao_enderecados.html'
        self.title_name = 'Empenhos não endereçados'
        self.por_pagina = 50

        self.table_defs = TableDefs(
            {
                'sol': ['Solicitação'],
                'ped': ['Ped. destino'],
                'sit': ['Situação'],
                'op': ['OP'],
                'oc': ['OC'],
                'ref': ['Ref.'],
                'tam': ['Tam.'],
                'cor': ['Cor'],
                'qtd_sol': ['Qtd. solicit.', 'r'],
                'qtd_63': ['Qtd. Est. 63', 'r'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )
        self.Lote = namedtuple('Lote', 'op oc')

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        if self.usa_paginador == 'n':
            self.por_pagina = 999999

        data = nao_enderecados.query(
            self.cursor,
            self.sol_de,
            self.sol_ate,
            self.situacao,
        )
        nao_end_len = len(data)

        lotes_len = len(
            set(
                (row['op'], row['oc'])
                for row in data
            )
        )

        data = paginator_basic(data, self.por_pagina, self.page)

        for row in data.object_list:
            if not row['sol']:
                row['sol'] = '#'

        form_report_lines_after = []
        
        filtro = min_max_string(
            self.sol_de,
            self.sol_ate,
            process_input=(
                only_digits,
                noneifempty,
            ),
            msg_format="Solicitação {}",
        )
        if filtro:
            form_report_lines_after.append(filtro)

        self.context.update(self.table_defs.hfs_dict())
        self.context.update({
            'data': data,
            'safe': ['op', 'oc', 'ped', 'sol'],
            'por_pagina': self.por_pagina,
            'nao_end_len': nao_end_len,
            'lotes_len': lotes_len,
            'form_report_lines_after': form_report_lines_after,
            'form_report_excludes': [
                'sol_de',
                'sol_ate',
                'usa_paginador',
                'page',
            ],
        })
