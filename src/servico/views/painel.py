from pprint import pprint

from django.db import connection
from django.urls import reverse

from o2.views.base.get_post import O2BaseGetPostView
from utils.classes import LoggedInUser

import servico.forms
import servico.models
from servico.queries.lista import lista_documentos


class Painel(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(Painel, self).__init__(*args, **kwargs)
        self.cleaned_data2self = True
        self.Form_class = servico.forms.ListaForm
        self.template_name = 'servico/painel.html'
        self.title_name = 'Painel do usuário'


    def mount_context(self):
        logged_in = LoggedInUser()
        self.user = logged_in.user

        if self.ordem:
            try:
                self.ordem = int(self.ordem)
            except Exception:
                return
        else:
            self.ordem = 0

        cursor = connection.cursor()
        interacoes = lista_documentos(cursor, self.ordem, self.user)

        for row in interacoes:
            row['documento_id|TARGET'] = '_blank'
            row['documento_id|LINK'] = reverse(
                    'servico:ordem__get',
                    args=[row['documento_id']],
                )

        self.context.update({
            'headers': [
                '#', 'Data/hora', 'Usuário',
                'Equipe', 'Nível', 'Descrição',
                'Interações', 'Status atual', 'Data/hora', 'Período',
            ],
            'fields': [
                'documento_id', 'create_at', 'user__username',
                'equipe__nome', 'classificacao__nome', 'descricao',
                'conta', 'last_status__nome', 'last_create_at', 'diff_at',
            ],
            'data': interacoes,
        })
