from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from o2.views.base.get_post import O2BaseGetPostView
from geral.functions import has_permission
from utils.table_defs import TableDefs

from lotes.forms.corte.envio_insumo import EnvioInsumoForm
from lotes.queries.corte import (
    nfs_de_envio,
    nfs_de_forn,
    relacionamentos,
)


class EnvioInsumo(O2BaseGetPostView):

    def init_defs(self):
        self.env_defs = TableDefs(
            {
                'dt_emi': ["Dt.emissão", 'c'],
                'nf': ["NF", 'c'],
                'valor': ["Valor", 'r'],
                'forn_nome': ["Fornecedor"],
                'itens': ["Itens"],
                'nfe_nf': ["NF Forn.", 'c'],
                'nfe_dt_emi': ["Dt.emissão", 'c'],
                'nfe_dt_dig': ["Dt.digitação", 'c'],
                'nfe_valor': ["Valor", 'r'],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

        self.rec_defs = TableDefs(
            {
                'dt_emi': ["Dt.emissão", 'c'],
                'forn_nome': ["Fornecedor"],
                'itens': ["Itens"],
                'nf': ["NF", 'c'],
                'valor': ["Valor", 'r'],
                'nf': ["NF", 'c'],
                'nf_envia': ["NF de envio", 'c'],
                'editar': ["Editar", 'c'],
                'nf_env_dt_emi': ["Dt.emissão", 'c'],
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

        self.init_defs()

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        # relacionamentos.verifica_novos(cursor)
        
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
            editar_link = reverse(
                'producao:corte-informa_nf_envio',
                args=[
                    row['empr'],
                    row['nf_num'],
                    row['nf_ser'],
                    row['cnpj_num']
                ],
            )
            row['editar'] = f"""
              <a title="Editar" target="_blank" href="{editar_link}"><span class="glyphicon glyphicon-pencil" aria-hidden="true"></span></a>
            """
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
            if row['nf_env_valor'] != '-':
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

        edita = has_permission(
            self.request, 'lotes.informa_nf_envio_matriz_filial')

        if not edita:
            self.rec_defs.dele('editar')

        self.context['rec_data'] = self.rec_defs.hfs_dict()
        self.context['rec_data']['data'] = rec_data

        if edita:
            self.context['rec_data']['safe'] = ['editar']
