from django.shortcuts import render
from django.views import View


class GerarAssinaturas(View):

    def __init__(self):
        self.template_name = 'email_signature/gerar_assinaturas.html'
        self.context = {'titulo': 'Gerar assinaturas'}

    def mount_context(self):
        pass

    def get(self, request, *args, **kwargs):
        self.mount_context()
        return render(request, self.template_name, self.context)
