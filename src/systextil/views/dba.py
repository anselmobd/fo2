import sqlparse
from itertools import takewhile
from pprint import pprint

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)

from base.views import O2BaseGetPostView
from fo2.connections import db_cursor_so

from systextil.forms import SegundosForm
from systextil.queries.dba.main import rodando_a_segundos

class Demorada(LoginRequiredMixin, PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Demorada, self).__init__(*args, **kwargs)
        self.permission_required = 'systextil.can_be_dba'
        self.template_name = 'systextil/dba/demorada.html'
        self.title_name = 'Queries Demoradas'
        self.Form_class = SegundosForm
        self.form_class_initial = True
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        raw_data = rodando_a_segundos(cursor,self.segundos)

        data = []
        last_sid = -1
        last_serial = -1
        for row in raw_data:
            if row['sid'] == last_sid and row['serial'] == last_serial:
                data[-1]['sql_text'] += row['sql_text']
            else:
                data.append(row)                
                last_sid = row['sid']
                last_serial = row['serial']

        for row in data:
            mins = row['secs'] // 60
            secs = row['secs'] % 60
            row['mins'] = f"{mins}:{secs:02d}"
            row['serial'] = f"{row['serial']:d}"
            row['sql_text_parse'] = sqlparse.format(
                row['sql_text'],
                reindent_aligned=True,
                indent_width=2,
                keyword_case='upper',
            )

            linhas = row['sql_text'].split('\n')

            self.min_spaces = 1000
            def strip_min_spaces(linha):
                linha_strip = linha.strip()
                if linha_strip and linha_strip[:2] != '--':
                    self.min_spaces = min(
                        self.min_spaces,
                        sum(1 for _ in takewhile(lambda c: c == ' ', linha)),
                    )
                return linha_strip

            linhas_strip = list(map(strip_min_spaces, linhas))
            linhas_vazias_inicio = sum(1 for _ in takewhile(lambda l: len(l) == 0, linhas_strip))
            linhas_vazias_final = sum(1 for _ in takewhile(lambda l: len(l) == 0, reversed(linhas_strip)))

            del linhas[:linhas_vazias_inicio]
            if linhas_vazias_final:
                del linhas[-linhas_vazias_final:]

            def put_min_spaces(linha):
                linha_strip = linha.strip()
                if linha_strip and linha_strip[:2] != '--':
                    linha = linha[self.min_spaces:]
                else:
                    linha = linha_strip
                return linha

            linhas = list(map(put_min_spaces, linhas))
            row['sql_text_fo2'] = '\n'.join(linhas)

        self.context.update({
            'headers': ['Username', 'SID', 'Serial', 'Rodando a', 'SQL'],
            'data': data,
        })
