from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin

from base.views import O2BaseGetPostView

import logistica.forms
import logistica.models


class EntradaNfSemXml(LoginRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(EntradaNfSemXml, self).__init__(*args, **kwargs)
        self.cleaned_data2self = True
        self.Form_class = logistica.forms.EntradaNfSemXmlForm
        self.template_name = 'logistica/entrada_nf/sem_xml.html'
        self.title_name = 'Entrada de NF sem XML'

    def mount_context(self):
        valores = {
            key: getattr(self, key, '')
            for key in [
                'cadastro', 'emissor', 'numero', 'descricao', 'qtd',
                'hora_entrada', 'transportadora', 'motorista', 'placa',
                'responsavel'
            ]
        }
        try:
            nf = logistica.models.NfEntrada(**valores)
            nf.save()
        except Exception as e:
            self.context.update({
                'msg_erro': f"NF não gravada <{e}>"
            })
