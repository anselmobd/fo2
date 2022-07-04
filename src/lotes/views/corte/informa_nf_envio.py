from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.table_defs import TableDefs
from utils.views import totalize_data

from lotes.forms.corte.informa_nf_envio import InformaNfEnvioForm
from contabil.queries import (
    nf_rec_info,
    nf_rec_itens,
)


class InformaNfEnvio(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(InformaNfEnvio, self).__init__(*args, **kwargs)
        self.Form_class = InformaNfEnvioForm
        self.template_name = 'lotes/corte/informa_nf_envio.html'
        self.title_name = "Informa NF de envio"
        self.get_args = ['empresa', 'nf', 'nf_ser', 'cnpj']
        self.get_args2context = True
        self.get_args2form = False
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        
        # data = nf_rec_info.query(
        #     cursor,
        #     empresa=self.empresa,
        #     nf=self.nf,
        #     nf_ser=self.nf_ser,
        #     cnpj=self.cnpj,
        # )
        # if len(data) == 0:
        #     self.context.update({
        #         'msg_erro': "Nota fiscal recebida não encontrada",
        #     })
        #     return
