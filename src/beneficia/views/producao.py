from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views.o2.get_post import O2BaseGetPostView
from utils.functions.date import dmy_or_empty
from utils.functions.dictlist.dictlist_to_grade import dictlist_to_grade_qtd
from utils.functions.strings import min_max_string
from utils.table_defs import TableDefsHpSD
from utils.views import totalize_data

from beneficia.forms.producao import Form as ProducaoForm
from beneficia.queries.producao import query as producao_query


class Producao(O2BaseGetPostView):

    def __init__(self):
        super(Producao, self).__init__()
        self.Form_class = ProducaoForm
        self.template_name = 'beneficia/producao.html'
        self.title_name = 'Producao'
        self.form_class_has_initial = True
        self.cleaned_data2self = True

    def form_report(self):
        form_report_lines_before = []
        
        filtro = min_max_string(
            self.data_de,
            self.data_ate,
            process_input=(
                dmy_or_empty,
            ),
            msg_format="Data {}",
            mm='de_ate',
        )
        if filtro:
            form_report_lines_before.append(filtro)

        return {
            'form_report_lines_before': form_report_lines_before,
            'form_report_excludes': [
                'data_de',
                'data_ate',
            ],
        }

    def get_producao(self):
        data = producao_query(
            self.cursor,
            data_de=self.data_de,
            data_ate=self.data_ate,
            turno=self.turno,
            estagio=self.estagio.codigo_estagio if self.estagio else None,
            tipo=2,
            horario=int(self.horario),
        )
        result = {
            'titulo': 'OB2',
            'data': data,
            'vazio': "Sem produção",
        }
        grade = {
            'data': None,
        }
        if data:

            grade = dictlist_to_grade_qtd(
                dados=data,
                field_linha='cor',
                field_coluna='tipo_tecido',
                facade_coluna='Tecido',
                field_quantidade='quilos',
            )

            for row in grade['data']:
                for field in grade['fields'][1:]:
                    row[f'{field}|DECIMALS'] = 3

            for row in data:
                if not row['usuario']:
                    row['usuario'] = '-'
                if row['dt_fim']:
                    row['dt_fim'] = row['dt_fim'].date()
                if row['h_fim']:
                    row['h_fim'] = row['h_fim'].strftime('%H:%M')
                row['ob|TARGET'] = '_blank'
                row['ob|LINK'] = reverse(
                    'beneficia:ob__get',
                    args=[row['ob']],
                )

            totalize_data(
                data,
                {
                    'sum': ['quilos'],
                    'descr': {'dt_fim': 'Total:'},
                    'row_style':
                        "font-weight: bold;"
                        "background-image: linear-gradient(#DDD, white);",
                    'flags': ['NO_TOT_1'],
                }
            )
            TableDefsHpSD({
                'ob': ["OB2"],
                'maq': ["Máquina"],
                'est': ["Estágio"],
                'usuario': ["Usuário"],
                'dt_fim': ["Data"],
                'h_fim': ["Hora"],
                'turno': ["Turno"],
                'tipo_tecido': ["Tipo tecido"],
                'cor': ["Cor"],
                'quilos': ["Quilos", 'r', 3],
            }).hfs_dict(context=result)

        return result, grade

    def mount_context(self):
        self.cursor = db_cursor_so(self.request)

        if not self.data_ate:
            self.data_ate = self.data_de

        self.context.update(self.form_report())

        self.context['producao'], self.context['grade'] = self.get_producao()
