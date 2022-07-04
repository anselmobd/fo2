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
        
        data = nfs_de_envio.query(
            cursor,
            dt_de=self.dt_de,
            dt_ate=self.dt_ate,
            relacionado=False,
        )
        if len(data) == 0:
            self.context['msg_erro'] = "Não encontrada NF de envio"
            return

        self.context.update(self.table_defs.hfs_dict())
        self.context['data'] = data
