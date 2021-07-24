from pprint import pprint

from django.shortcuts import render
from django.views import View

import contabil.forms


class Converte(View):

    def __init__(self, *args, **kwargs):
        super(Converte, self).__init__(*args, **kwargs)
        self.Form_class = contabil.forms.UploadArquivoForm
        self.template_name = 'contabil/converte.html'
        self.title_name = 'Converte para importação'

    def get(self, request, *args, **kwargs):
        context = {'titulo': self.title_name}
        form = self.Form_class()
        context['form'] = form
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        self.request = request
        context = {'titulo': self.title_name}
        form = self.Form_class(request.POST, request.FILES)
        if form.is_valid():
            lines = []
            for line in request.FILES['arquivo']:
                print(line)
                line = line.decode(errors='ignore').strip("\n")
                lines.append(line)
            context['original'] = "\n".join(lines)
        else:
            context['erro'] = 'Erro inexperado!'
        context['form'] = form
        return render(request, self.template_name, context)
