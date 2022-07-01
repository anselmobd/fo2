from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.table_defs import TableDefs

from lotes.forms.corte.envia_insumo import EnviaInsumoForm
from contabil.queries import nf_rec_info


class EnviaInsumo(O2BaseGetPostView):

    balloon = (
        '<span style="font-size: 50%;vertical-align: super;" '
        'class="glyphicon glyphicon-comment" '
        'aria-hidden="true"></span>'
    )
    table_defs = TableDefs(
        {
            'dt_trans': ["Dt.recebimento"],
            'dt_emi': ["Dt.emissão"],
            'nf': ["NF"],
            'forn_cnpj_nome': ["Fornecedor"],
            'nat': [(f"Nat.Op.{balloon}", )],
            'cfop': ["CFOP", 'c'],
            'tran_est': [(f"Tran.est.{balloon}", ), 'c'],
            'hist_cont': [(f"Hist.cont.{balloon}", ), 'c'],
            'sit_entr': [(f"Sit. entr.{balloon}", ), 'c'],
            'qtde_itens': ["Quant. itens", 'r'],
            'valor_itens': ["Valor", 'r'],
        },
        ['header', '+style'],
        style = {'_': 'text-align'},
    )

    def __init__(self, *args, **kwargs):
        super(EnviaInsumo, self).__init__(*args, **kwargs)
        self.Form_class = EnviaInsumoForm
        self.form_class_has_initial = True
        self.template_name = 'lotes/corte/envia_insumo.html'
        self.title_name = "Envio de insumos"
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        
        data = nf_rec_info.query(
            cursor,
            empresa=self.empresa,
            sit_entr=self.sit_entr,
            dt_de=self.dt_de,
            dt_ate=self.dt_ate,
            niv=self.niv,
            ref=self.ref,
            tam=self.tam,
            cor=self.cor,
        )
        if len(data) == 0:
            self.context['msg_erro'] = "Nota fiscal recebida não encontrada"
            return

        for row in data:
            row['nf|TARGET'] = '_blank'
            row['nf|LINK'] = reverse(
                'contabil:nf_recebida__get',
                args=[
                    row['empr'],
                    row['nf_num'],
                    row['nf_ser'],
                    row['forn_cnpj_num']
                ],
            )
            row['nat|HOVER'] = row['nat_descr']
            row['tran_est|HOVER'] = row['tran_descr']
            row['hist_cont|HOVER'] = row['hist_descr']
            row['sit_entr|HOVER'] = row['sit_entr_descr']

        self.context.update(self.table_defs.hfs_dict())
        self.context['data'] = data
