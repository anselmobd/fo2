from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.table_defs import TableDefs

from lotes.forms.corte.envio_insumo import EnvioInsumoForm
from lotes.queries.corte import (
    nfs_de_envio,
    relacionamentos,
)


class EnvioInsumo(O2BaseGetPostView):

    table_defs = TableDefs(
        {
            'dt_emi': ["Dt.emissão"],
            'nf': ["NF"],
            'valor': ["Valor", 'r'],
            'nfe_cnpj': ["CNPJ Forn."],
            'nfe_nf': ["NF Forn."],
            'nfe_dt_emi': ["Dt.emissão"],
            'nfe_valor': ["Valor", 'r'],
        },
        ['header', '+style'],
        style = {'_': 'text-align'},
    )

    def __init__(self, *args, **kwargs):
        super(EnvioInsumo, self).__init__(*args, **kwargs)
        self.Form_class = EnvioInsumoForm
        self.form_class_has_initial = True
        self.template_name = 'lotes/corte/envio_insumo.html'
        self.title_name = "Envio de insumos"
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        relacionamentos.verifica_novos(cursor)
        
        env_data = nfs_de_envio.query(
            cursor,
            dt_de=self.dt_de,
            dt_ate=self.dt_ate,
        )
        if len(env_data) == 0:
            self.context['msg_erro'] = "Não encontrada NF de envio"
            return

        for row in env_data:
            row['nf|TARGET'] = '_blank'
            row['nf|LINK'] = reverse(
                'contabil:nota_fiscal__get',
                args=[
                    row['empr'],
                    row['nf_num'],
                ]
            )
            if row['nfe_nf'] != "-":
                row['nfe_nf|TARGET'] = '_blank'
                row['nfe_nf|LINK'] = reverse(
                    'contabil:nf_recebida__get',
                    args=[
                        row['empr'],
                        row['nfe_num'],
                        row['nfe_ser'],
                        row['nfe_cnpj_num']
                    ],
                )


        self.context['env_data'] = self.table_defs.hfs_dict()
        self.context['env_data']['data'] = env_data
