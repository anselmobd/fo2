from datetime import datetime
from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

import cd.forms
import cd.views.gerais
from cd.queries.endereco import (
    lotes_em_endereco,
    get_endereco,
    get_esvaziamentos_de_palete,
    get_palete,
)


class VisualizaEsvaziamento(View):

    def __init__(self):
        self.template_name = 'cd/vizualiza_esvaziamento.html'
        self.context = {'titulo': 'Esvaziamento'}

    def mount_context(self):
        palete = self.context['palete']
        data_versao = self.context['data_versao']

    def get(self, request, *args, **kwargs):
        self.cursor = db_cursor_so(request)
        self.context.update(kwargs)
        self.mount_context()
        return render(request, self.template_name, self.context)
