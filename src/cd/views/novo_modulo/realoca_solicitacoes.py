from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.paginator import paginator_basic
from o2.views.base.get_post import O2BaseGetPostView
from utils.functions import untuple_keys_concat
from utils.functions.strings import (
    min_max_string,
    noneifempty,
    only_digits,
)
from utils.views import totalize_data

import cd.forms
from cd.queries.novo_modulo.solicitacoes import get_solicitacoes


class RealocaSolicitacoes(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(RealocaSolicitacoes, self).__init__(*args, **kwargs)
        self.Form_class = cd.forms.RealocaSolicitacoesForm
        self.cleaned_data2self = True
        self.cleaned_data2data = True
        self.template_name = 'cd/novo_modulo/realoca_solicitacoes.html'
        self.title_name = 'Realoca solicitações'
        self.por_pagina = 20

    def mount_context(self):
        cursor = db_cursor_so(self.request)

