from pprint import pprint

from django.shortcuts import render
from django.urls import reverse
from django.views import View

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.table_defs import TableDefs
from utils.views import totalize_data

import contabil.forms.nf_rec
from contabil.queries import (
    nf_rec_info,
    nf_rec_itens,
)


class NFRecebida(O2BaseGetPostView):

    balloon = (
        '<span style="font-size: 50%;vertical-align: super;" '
        'class="glyphicon glyphicon-comment" '
        'aria-hidden="true"></span>'
    )
    capa_defs = TableDefs(
        {
            'dt_trans': ['Dt.recebimento'],
            'dt_emi': ['Dt.emissão'],
            'nf': ["NF"],
            'forn_cnpj_nome': ["Fornecedor"],
            'nat': [(f"Nat.Op.{balloon}", )],
            'cfop': ["CFOP", 'c'],
            'tran_est': [(f"Tran.est.{balloon}", ), 'c'],
            'hist_cont': [(f"Hist.cont.{balloon}", ), 'c'],
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
        self.Form_class = contabil.forms.nf_rec.NFRecebidaForm
        self.template_name = 'contabil/nf_recebida.html'
        self.title_name = "Nota fiscal recebida"
        self.get_args = ['nf', 'empresa', 'cnpj']
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        data = nf_rec_info.query(
            cursor,
            empresa=self.empresa,
            cnpj=self.cnpj,
            nf=self.nf,
        )
        if len(data) == 0:
            self.context.update({
                'msg_erro': "Nota fiscal recebida não encontrada",
            })
            return

        for row in data:
            row['nf|TARGET'] = '_blank'
            row['nf|LINK'] = reverse(
                'contabil:nf_recebida__get',
                args=[row['empr'], row['nf_num'], row['forn_cnpj_num']],
            )
            row['nat|HOVER'] = row['nat_descr']
            row['tran_est|HOVER'] = row['tran_descr']
            row['hist_cont|HOVER'] = row['hist_descr']

        self.context.update(self.capa_defs.hfs_dict())
        self.context['data'] = data

        if len(data) > 1:
            return

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
