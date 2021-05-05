from pprint import pprint

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction

from base.views import O2BaseGetPostView

import servico.forms
import servico.models
from servico.models.functions import salva_interacao


class CriaOrdem(LoginRequiredMixin, O2BaseGetPostView):

    def __init__(self, *args, **kwargs):
        super(CriaOrdem, self).__init__(*args, **kwargs)
        self.cleaned_data2self = True
        self.Form_class = servico.forms.CriaInteracaoForm
        self.template_name = 'servico/cria_ordem.html'
        self.title_name = 'Cria ordem'

    def mount_context(self):
        try:
            msg = {}
            with transaction.atomic():
                self.doc = salva_interacao(
                    msg, self.request, 
                    classificacao=self.classificacao,
                    equipe=self.equipe,
                    descricao=self.descricao,
                )
        except Exception:
            self.context.update(msg)
            return
        doc_num = self.doc.id
        self.redirect = ('servico:ordem__get', doc_num)
