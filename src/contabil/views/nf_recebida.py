from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.table_defs import TableDefs
from utils.views import totalize_data

import contabil.forms.nf
from contabil.queries import (
    nf_rec_info,
    nf_rec_itens,
)


class NFRecebida(O2BaseGetPostView):

    capa_defs = TableDefs(
        {
            'dt_trans': ['Dt.recebimento'],
            'dt_emi': ['Dt.emissão'],
            'forn_cnpj_nome': ["Fornecedor"],
            'nat_uf': ["UF"],
            'qtde_itens': ["Quant. itens", 'r'],
            'valor_itens': ["Valor", 'r'],
        },
        ['header', '+style'],
        style = {'_': 'text-align'},
    )
    itens_defs = TableDefs(
        {
            'item': ["Item"],
            'qtd': ["Quantidade", 'r'],
            'preco': ["Preço", 'r'],
            'valor': ["Valor", 'r'],
        },
        ['header', '+style'],
        style = {'_': 'text-align'},
    )

    def __init__(self, *args, **kwargs):
        super(NFRecebida, self).__init__(*args, **kwargs)
        self.Form_class = contabil.forms.nf.NotaFiscalForm
        self.template_name = 'contabil/nf_recebida.html'
        self.title_name = "Nota fiscal recebida"
        self.get_args = ['nf', 'empresa']
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        data = nf_rec_info.query(
            cursor, empresa=self.empresa, nf=self.nf)
        if len(data) == 0:
            self.context.update({
                'msg_erro': "Nota fiscal recebida não encontrada",
            })
            return

        self.context.update(self.capa_defs.hfs_dict())
        self.context['data'] = data

        i_data = nf_rec_itens.query(cursor, self.nf, self.empresa)
        if len(i_data) == 0:
            return

        totalize_data(i_data, {
            'sum': ['valor'],
            'descr': {'ref': "Total:"},
            'row_style': 'font-weight: bold;',
        })

        self.context['itens'] = self.itens_defs.hfs_dict()
        self.context['itens']['data'] = i_data
