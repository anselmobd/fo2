from django.shortcuts import render
from django.views import View

import email_signature.models as models


class GerarAssinaturas(View):

    def __init__(self):
        self.template_name = 'email_signature/gerar_assinaturas.html'
        self.context = {'titulo': 'Gerar assinaturas'}

    def gerar_assinatura(self, conta):
        pass

    def mount_context(self):
        contas = models.Account.objects.all()
        self.context['lista'] = []
        for conta in contas:
            erro = self.gerar_assinatura(conta)
            self.context['lista'].append(dict(
                conta=conta.codigo,
                erro=erro,
            ))

    def get(self, request, *args, **kwargs):
        self.mount_context()
        return render(request, self.template_name, self.context)
