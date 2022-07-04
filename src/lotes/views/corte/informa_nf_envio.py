from pprint import pprint

from django.contrib.auth.mixins import PermissionRequiredMixin

from fo2.connections import db_cursor_so

from base.views import O2BaseGetPostView

from lotes.forms.corte.informa_nf_envio import InformaNfEnvioForm
from contabil.queries import set_nf_envia


class InformaNfEnvio(PermissionRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(InformaNfEnvio, self).__init__(*args, **kwargs)
        self.permission_required = 'lotes.informa_nf_envio_matriz_filial'
        self.Form_class = InformaNfEnvioForm
        self.template_name = 'lotes/corte/informa_nf_envio.html'
        self.title_name = "Informa NF de envio"
        self.get_args = ['empresa', 'nf', 'nf_ser', 'cnpj']
        self.get_args2context = True
        self.get_args2form = False
        self.cleaned_data2self = True

    def mount_context(self):
        cursor = db_cursor_so(self.request)
        
        ok = set_nf_envia.update(
            cursor,
            empresa=self.context['empresa'],
            nf=self.context['nf'],
            nf_ser=self.context['nf_ser'],
            cnpj=self.context['cnpj'],
            nf_env=self.nf_env,
        )
        self.context.update({
            'msg': f"Nf de envio gravada como '{self.nf_env}'" if ok else "Erro ao gravar FN de envio",
        })
