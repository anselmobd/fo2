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

        # print('raw_data')
        # pprint(raw_data)

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

        # print('data')
        # pprint(data)

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

            # linhas = row['sql_text'].split('\n')
            # min_spaces = 1000
            # state = 'inicio'
            # linhas_vazias_inicio = 0
            # iguais = 0
            # ult_tem_algo = True
            # for linha in linhas:
            #     linhas_strip = linha.strip()
            #     tem_algo = linhas_strip and linhas_strip[:2] != '--'

            #     if state == 'inicio':
            #         if not tem_algo:
            #             linhas_vazias_inicio += 1
            #         else:
            #             state = 'final'

            #     if state == 'final':
            #         if tem_algo == ult_tem_algo:
            #             iguais += 1
            #         else:
            #             ult_tem_algo = tem_algo
            #             iguais = 1

            #     if tem_algo:
            #         spaces = sum(1 for _ in takewhile(lambda c: c == ' ', linha))
            #         min_spaces = min(spaces, min_spaces)

            # if ult_tem_algo:
            #     linhas_vazias_final = 0
            # else:
            #     linhas_vazias_final = iguais

            # sql_text_list = []
            # for linha in linhas[linhas_vazias_inicio:-linhas_vazias_final]:
            #     linhas_strip = linha.strip()
            #     if linhas_strip and linhas_strip[:2] != '--':
            #         sql_text_list.append(linha[min_spaces:])
            #     else:
            #         sql_text_list.append(linhas_strip)

            # row['sql_text_format'] = '\n'.join(sql_text_list)
                   
            # quebras = row['sql_text'].count('\n')
            # print('quebras', quebras)
            # i = 0
            # while True:
            #     n_chars = len(row['sql_text'])
            #     print('n_chars', n_chars)
            #     sql_temp = row['sql_text'].replace('\n ', '\n')
            #     new_n_chars = len(sql_temp)
            #     print('new_n_chars', new_n_chars)
            #     print('n_chars - new_n_chars', n_chars - new_n_chars)
            #     if (n_chars - new_n_chars) != quebras:
            #         break
            #     row['sql_text'] = sql_temp
            #     i += 1
            #     if i == 30:
            #         break

        self.context.update({
            'headers': ['Username', 'SID', 'Serial', 'Rodando a', 'SQL'],
            # 'fields': ['username', 'sid', 'serial', 'mins', 'sql_text'],
            # 'pre': ['sql_text'],
            'data': data,
        })
