import os
import subprocess
from pprint import pprint

from django.conf import settings
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import View

import email_signature.classes as classes
import email_signature.models as models
from email_signature.views.views import get_template_file


class GerarAssinaturas(View):

    def __init__(self):
        self.template_name = 'email_signature/gerar_assinaturas.html'
        self.context = {'titulo': 'Gerar assinaturas'}

    def mount_context(self, **kwargs):
        try:
            contas = models.Account.objects.filter(id=kwargs['id'])
        except KeyError:
            contas = models.Account.objects.all()

        self.context['lista'] = []

        for conta in contas:

            erro = classes.assinatura.GeraAssinatura(conta).exec()

            self.context['lista'].append(dict(
                conta=conta.email,
                erro=erro,
            ))

    def get(self, request, *args, **kwargs):
        self.mount_context(**kwargs)
        return render(request, self.template_name, self.context)
