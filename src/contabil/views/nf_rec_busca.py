from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.views import totalize_data

import contabil.forms.nf
from contabil.queries import (
    nf_rec_info,
    nf_rec_itens,
)
from contabil.functions.nf import nf_situacao_descr

class BuscaNFRecebida(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(BuscaNFRecebida, self).__init__(*args, **kwargs)
        self.Form_class = contabil.forms.nf.NotaFiscalForm
        self.template_name = 'contabil/nf_rec_busca.html'
        self.title_name = "Busca NF recebida"
        self.get_args = ['nf', 'empresa']
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        self.context = {
            'titulo': self.title_name,
        }

        data = nf_rec_info.query(
            cursor, self.nf, self.empresa)
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

            i_data = nf_rec_itens.query(cursor, self.nf, self.empresa)

            if i_data:
                totalize_data(i_data, {
                    'sum': ['qtd'],
                    'descr': {'ref': "Total:"},
                    'row_style': 'font-weight: bold;',
                })

            self.context.update({
                'i_headers': [
                    "Nível",
                    "ref",
                    "tam",
                    "cor",
                    "qtd",
                ],
                'i_fields': [
                    'niv',
                    'ref',
                    'tam',
                    'cor',
                    'qtd',
                ],
                'i_data': i_data,
                'i_style': {
                    5: 'text-align: right;',
                },
            })
