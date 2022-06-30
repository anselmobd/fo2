from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.views import totalize_data

import contabil.forms.nf_rec_busca
from contabil.queries import (
    nf_rec_info,
    nf_rec_itens,
)
from contabil.functions.nf import nf_situacao_descr

class BuscaNFRecebida(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(BuscaNFRecebida, self).__init__(*args, **kwargs)
        self.Form_class = contabil.forms.nf_rec_busca.BuscaNFRecebidaForm
        self.template_name = 'contabil/nf_rec_busca.html'
        self.title_name = "Busca NF recebida"
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        
        data = nf_rec_info.query(
            cursor,
            ref=self.ref,
            tam=self.tam,
            cor=self.cor,
        )
        if len(data) == 0:
            self.context.update({
                'msg_erro': "Nota fiscal recebida não encontrada",
            })
        else:
            self.context.update({
                'headers': [
                    "Data",
                    "NF",
                    "Fornecedor",
                    "UF",
                    "nat_op",
                    "nat_uf",
                    'nat_cod',
                    'nat_of',
                    "nat_descr",
                    "tran_est",
                    "tran_descr",
                    "hist_cont",
                    "hist_descr",
                ],
                'fields': [
                    'dt',
                    'nf',
                    'forn_cnpj_nome',
                    'nat_uf',
                    'nat_op',
                    'nat_uf',
                    'nat_cod',
                    'nat_of',
                    'nat_descr',
                    'tran_est',
                    'tran_descr',
                    'hist_cont',
                    'hist_descr',
                ],
                'data': data,
            })
