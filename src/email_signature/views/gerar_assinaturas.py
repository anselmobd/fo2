from django.shortcuts import render
from django.template import loader
from django.views import View

import email_signature.models as models
from email_signature.views.views import get_template_file


class GerarAssinaturas(View):

    def __init__(self):
        self.template_name = 'email_signature/gerar_assinaturas.html'
        self.context = {'titulo': 'Gerar assinaturas'}

    def gerar_assinatura(self, conta):
        context = {
            'nome': conta.nome,
            'setor': conta.setor,
            'email': conta.email,
            'num_1': conta.num_1,
            'num_2': conta.num_2,
        }
        http_resp = HttpResponse(
            self.template.render(context, self.request),
            content_type='text/plain')
        http_resp['Content-Disposition'] = \
            'attachment; filename="index.html"'
        # return http_resp

    def mount_context(self):
        template_file = get_template_file()
        self.template = loader.get_template(template_file)

        contas = models.Account.objects.all()
        self.context['lista'] = []
        for conta in contas:
            erro = self.gerar_assinatura(conta)
            self.context['lista'].append(dict(
                conta=conta.codigo,
                erro=erro,
            ))
            return

    def get(self, request, *args, **kwargs):
        self.request = request
        self.mount_context()
        return render(request, self.template_name, self.context)
