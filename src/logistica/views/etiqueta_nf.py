from pprint import pprint

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.table_defs import TableDefs

from lotes.queries.pedido import ped_inform

from logistica.forms.nf import NfForm
from logistica.queries.etiqueta_nf import get_dados_nf


class EtiquetaNf(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(EtiquetaNf, self).__init__(*args, **kwargs)
        self.Form_class = NfForm
        self.template_name = 'logistica/etiqueta_nf.html'
        self.title_name = 'Etiqueta de NF'
        self.cleaned_data2self = True

        self.init_defs()

    def init_defs(self):
        self.col_defs = TableDefs(
            {
                'empr_nome': ["Empresa"],
                'nf': ["NF"],
                'vols': ["Volumes", 'c'],
                'peso_tot': ["Peso Total"],
                'ped': ["Pedido Tussor"],
                'ped_cli': ["Pedido do cliente"],
                'transp_nome': ["Transportadora"],
                'cli_nome': ["Cliente"],
                'ende': ["Endereço"],
                'end_num': ["Número"],
                'end_compl': ["Complemento"],
                'end_bairro': ["Bairro"],
                'end_cid': ["Cidade"],
                'end_uf': ["UF"],
                'cli_cep': ["CEP"],
            },
            ['header', '+style'],
            style = {'_': 'text-align'},
        )

    def mount_context(self):
        cursor = db_cursor_so(self.request)

        dados_nf = get_dados_nf(cursor, self.nf)
        if len(dados_nf) == 0:
            self.context.update({
                'msg_erro': 'NF não encontrada',
            })
            return
        
        pprint(dados_nf)

        dados_ped = ped_inform(cursor, dados_nf[0]['ped'], 1)

        pprint(dados_ped)

        self.context.update(self.col_defs.hfs_dict())
        self.context.update({
            'data': dados_nf,
        })
