from pprint import pprint

from django.urls import reverse

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView
from utils.table_defs import TableDefs

from lotes.forms.corte.envia_insumo import EnviaInsumoForm
from lotes.queries.corte import relaciona_nfs


class EnviaInsumo(O2BaseGetPostView):

    table_defs = TableDefs(
        {
            'dt_emi': ["Dt.emissão"],
            'nf': ["NF"],
            'valor': ["Valor", 'r'],
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

        relaciona_nfs.verifica_novos_relacionamentos(cursor)
        
        data = relaciona_nfs.lista_relacionamentos(
            cursor,
            dt_de=self.dt_de,
            dt_ate=self.dt_ate,
        )
        if len(data) == 0:
            self.context['msg_erro'] = "Não encontrada NF de envio"
            return

        self.context.update(self.table_defs.hfs_dict())
        self.context['data'] = data
