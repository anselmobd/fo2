from pprint import pprint

from django.db import connection
from django.urls import reverse

from base.views import O2BaseGetPostView

import servico.forms
import servico.models
from servico.queries.lista import *


class Lista(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Lista, self).__init__(*args, **kwargs)
        self.cleaned_data2self = True
        self.Form_class = servico.forms.ListaForm
        self.template_name = 'servico/lista.html'
        self.title_name = 'Lista ordens'


    def mount_context(self):
        try:
            self.ordem = int(self.ordem)
        except Exception:
            return
        
        cursor = connection.cursor()
        interacoes = lista_documentos(cursor, self.ordem)

        for row in interacoes:
            row['documento_id|TARGET'] = '_blank'
            row['documento_id|LINK'] = reverse(
                    'servico:ordem__get',
                    args=[row['documento_id']],
                )

        self.context.update({
            'headers': [
                '#', 'Data/hora', 'Status', 'Usuário',
                'Equipe', 'Nível', 'Descrição',
                'Interações', 'Status atual', 'Data/hora', 'Período',
            ],
            'fields': [
                'documento_id', 'create_at', 'status__nome', 'user__username',
                'equipe__nome', 'nivel__nome', 'descricao',
                'conta', 'last_status__nome', 'last_create_at', 'diff_at',
            ],
            'data': interacoes,
        })
