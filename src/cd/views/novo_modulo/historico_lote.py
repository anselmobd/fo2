from pprint import pprint

from django.db import connection
from django.shortcuts import render
from django.urls import reverse

from base.views import O2BaseGetPostView
from geral.functions import rec_trac_log_to_dict

import lotes.models

import cd.queries as queries
import cd.forms


class HistoricoLote(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(HistoricoLote, self).__init__(*args, **kwargs)
        self.Form_class = cd.forms.ALoteForm
        self.template_name = 'cd/novo_modulo/historico_lote.html'
        self.title_name = 'Histórico de lote'
        self.get_args = ['lote']

    def mount_context(self):
        cursor = connection.cursor()
        lote = self.form.cleaned_data['lote']

        data = queries.historico_lote(cursor, lote)
        if len(data) == 0:
            self.context.update({'erro': 'Lote não encontrado ou nunca endereçado'})
            return

        lote_cd = lotes.models.Lote.objects.get(lote=lote)
        op = str(lote_cd.op)
        self.context.update({
            'op': op,
        })

        old_estagio = None
        old_usuario = None
        old_local = None
        for row in data:
            n_info = 0
            dict_log = rec_trac_log_to_dict(row['log'], row['log_version'])

            if 'estagio' in dict_log:
                row['estagio'] = dict_log['estagio']
                old_estagio = row['estagio']
                n_info += 1
            else:
                if old_estagio is None:
                    row['estagio'] = '-'
                else:
                    row['estagio'] = '='
            if row['estagio'] == 999:
                row['estagio'] = 'Finalizado'

            if 'local' in dict_log:
                row['local'] = dict_log['local']
                old_local = row['local']
                n_info += 1
            else:
                if old_local is None:
                    row['local'] = '-'
                else:
                    row['local'] = '='
            if row['local'] is None:
                row['local'] = 'SAIU!'

            if 'local_usuario' in dict_log:
                row['local_usuario'] = dict_log['local_usuario']
                old_usuario = row['local_usuario']
                n_info += 1
            else:
                if old_usuario is None or row['local'] in ('-', '='):
                    row['local_usuario'] = '-'
                else:
                    row['local_usuario'] = '='

            row['n_info'] = n_info

        for row in reversed(data):
            if row['local'] == 'SAIU!':
                break
            if row['local'] not in ['-', '=']:
                row['local|LINK'] = reverse(
                    'cd:estoque_filtro',
                    args=['E', row['local']])
                row['local|TARGET'] = '_BLANK'
                break

        self.context.update({
            'headers': ('Data', 'Estágio', 'Local', 'Usuário'),
            'fields': ('time', 'estagio', 'local', 'local_usuario'),
            'data': [row for row in data if row['n_info'] != 0],
        })
