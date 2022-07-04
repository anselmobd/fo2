from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.table_defs import TableDefs

from lotes.forms.corte.envio_insumo import EnvioInsumoForm
from lotes.queries.corte import (
    nfs_de_envio,
    nfs_de_forn,
    relacionamentos,
)


class EnvioInsumo(O2BaseGetPostView):

    env_defs = TableDefs(
        {
            'dt_emi': ["Dt.emissão"],
            'nf': ["NF"],
            'valor': ["Valor", 'r'],
            'forn_nome': ["Fornecedor"],
            'nfe_nf': ["NF Forn."],
            'nfe_dt_emi': ["Dt.emissão"],
            'nfe_valor': ["Valor", 'r'],
        },
        ['header', '+style'],
        style = {'_': 'text-align'},
    )

    rec_defs = TableDefs(
        {
            'dt_emi': ["Dt.emissão"],
            'forn_nome': ["Fornecedor"],
            'nf': ["NF"],
            'valor': ["Valor", 'r'],
            'nf': ["NF"],
            'nf_envia': ["NF de envio"],
            'nf_env_dt_emi': ["Dt.emissão"],
            'nf_env_valor': ["Valor", 'r'],
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
                if row['nfe_valor'] != row['valor']:
                    row['valor|STYLE'] = 'color: red;'
                    row['nfe_valor|STYLE'] = 'color: red;'

        self.context['env_data'] = self.env_defs.hfs_dict()
        self.context['env_data']['data'] = env_data

        rec_data = nfs_de_forn.query(
            cursor,
            dt_de=self.dt_de,
            dt_ate=self.dt_ate,
        )

        for row in rec_data:
            row['nf|TARGET'] = '_blank'
            row['nf|LINK'] = reverse(
                'contabil:nf_recebida__get',
                args=[
                    row['empr'],
                    row['nf_num'],
                    row['nf_ser'],
                    row['cnpj_num']
                ],
            )
            if row['nf_envia'] != '-':
                row['nf_envia|TARGET'] = '_blank'
                row['nf_envia|LINK'] = reverse(
                    'contabil:nota_fiscal__get',
                    args=[
                        row['empr'],
                        row['nf_envia'],
                    ]
                )
                if row['nf_env_valor'] != row['valor']:
                    row['valor|STYLE'] = 'color: red;'
                    row['nf_env_valor|STYLE'] = 'color: red;'

        self.context['rec_data'] = self.rec_defs.hfs_dict()
        self.context['rec_data']['data'] = rec_data
