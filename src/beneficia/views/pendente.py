from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.functions.strings import min_max_string
from utils.functions.date import dmy_or_empty
from utils.table_defs import TableDefsHpSD
from utils.views import totalize_data

from beneficia.forms.pendente import Form as PendenteForm
from beneficia.queries.pendente import query as pendente_query


class Pendente(O2BaseGetPostView):

    def __init__(self):
        super(Pendente, self).__init__()
        self.Form_class = PendenteForm
        self.template_name = 'beneficia/pendente.html'
        self.title_name = 'Pendente'
        self.form_class_has_initial = True
        self.cleaned_data2self = True

    def get_pendente(self):
        return {
            'titulo': 'OB2',
            'data': pendente_query(
                self.cursor,
                data_de=self.data_de,
                data_ate=self.data_ate,
                estagio=(self.estagio.codigo_estagio 
                    if self.estagio else None),
                tipo=2,
            ),
            'vazio': "Sem pendente",
        }

    def mount_link(self, pendente):
        for row in pendente['data']:
            row['ob|TARGET'] = '_blank'
            row['ob|LINK'] = reverse(
                'beneficia:ob__get',
                args=[row['ob']],
            )

    def mount_total(self, pendente):
        totalize_data(
            pendente['data'],
            {
                'sum': ['quilos'],
                'descr': {'ob': 'Total:'},
                'row_style':
                    "font-weight: bold;"
                    "background-image: linear-gradient(#DDD, white);",
                'flags': ['NO_TOT_1'],
            }
        )

    def mount_hfs(self, pendente):
        TableDefsHpSD({
            'ob': ["OB2"],
            'tipo_tecido': ["Tipo tecido"],
            'cor': ["Cor"],
            'quilos': ["Quilos", 'r', 3],
        }).hfs_dict(context=pendente)

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        pendente = self.get_pendente()

        if pendente['data']:
            self.mount_link(pendente)
            self.mount_total(pendente)
            self.mount_hfs(pendente)

        self.context['pendente'] = pendente
