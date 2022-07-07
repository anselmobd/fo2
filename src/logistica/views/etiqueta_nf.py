from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

from logistica.forms.nf import NfForm


class EtiquetaNf(O2BaseGetPostView):

    def __init__(self):
        super(EtiquetaNf, self).__init__()
        self.Form_class = NfForm
        self.cleaned_data2self = True
        self.template_name = 'logistica/etiqueta_nf.html'
        self.title_name = 'Estoque'

        self.lotes_por_pagina = 20

