from pprint import pprint

from base.views import O2BaseGetPostView

import logistica.forms
import logistica.models


class EntradaNfSemXml(O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(EntradaNfSemXml, self).__init__(*args, **kwargs)
        self.Form_class = logistica.forms.EntradaNfSemXmlForm
        self.template_name = 'logistica/entrada_nf/sem_xml.html'
        self.title_name = 'Entrada de NF sem XML'

    def mount_context(self):
        pprint(self.context)
        pprint(self.form)




